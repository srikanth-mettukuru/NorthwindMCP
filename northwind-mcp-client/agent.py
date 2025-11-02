from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import BaseTool
from mcp_client import MCPClient
import logging
import os
from dotenv import load_dotenv
import json

class MCPTool(BaseTool): 
    """Simple wrapper for MCP tools
        Note:
        MCP servers just return tool metadata (JSON descriptions), not actual executable LangChain tools.
        The MCPTool wrapper bridges this gap - it takes MCP tool name/description, creates a LangChain-compatible tool that inherits from BaseTool and implements "_run()" method to execute the tool.
    """
    
    name: str
    description: str
    mcp_client: MCPClient
    
    def __init__(self, tool_name: str, tool_description: str, mcp_client: MCPClient):
        super().__init__(
            name=tool_name,
            description=tool_description,
            mcp_client=mcp_client
        )
    
    def _run(self, **kwargs) -> str:
        """Execute MCP tool"""
        result = self.mcp_client.call_tool(self.name, kwargs)
        return json.dumps(result, indent=2)

class NorthwindAgent:
    """Simple Northwind database agent using MCP client + LangChain"""
    
    def __init__(self):
        load_dotenv()
        
        self.logger = logging.getLogger(__name__)
        
        # Get configuration from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        mcp_server_path = os.getenv("MCP_SERVER_PATH")
        
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        if not mcp_server_path:
            raise ValueError("MCP_SERVER_PATH not found in environment variables")
        
        # Initialize components
        self.mcp_client = MCPClient(mcp_server_path)  # MCP client to communicate with MCP server
        self.llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4.1-mini", temperature=0)  # LLM for agent reasoning
        
        # Create tools and agent
        self.tools = self._create_tools()
        self.agent_executor = self._create_agent() if self.tools else None
    
    def _create_tools(self):
        """Create LangChain tools from MCP tools"""
        try:
            tools_response = self.mcp_client.get_available_tools()
            if tools_response.get("status") == "error":
                self.logger.error(f"Failed to get MCP tools: {tools_response.get('error')}")
                return []
            
            mcp_tools = tools_response.get("tools", [])
            langchain_tools = []
            
            for tool_info in mcp_tools:
                tool = MCPTool(
                    tool_name=tool_info["name"],
                    tool_description=tool_info.get("description", f"Use {tool_info['name']} tool"),
                    mcp_client=self.mcp_client
                )
                langchain_tools.append(tool)
            
            return langchain_tools
            
        except Exception as e:
            self.logger.error(f"Error creating tools: {e}")
            return []
        
    
    def _create_agent(self):

        """Create LangChain agent"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful Northwind database assistant. 

The Northwind database has tables like: customer, salesorder, product, employee, supplier, etc.
             
VERY IMPORTANT: Do not answer any random questions. Only answer questions related to the Northwind database and its data. If the question is not related to Northwind database, politely refuse to answer.             

When users ask questions about the data in the database:
- Use schema tools (get_tables, get_columns) for database structure questions
- Always use 'get_columns' tool to understand table structure before querying. Example: When users mention customer names (like "FAPSM"), first use get_columns tool to find which column has customer names.             
- Use 'query' tool for specific data requests with proper SQL
- Use pre-defined report tools (sales_report, customer_orders) where possible for business reports. In cases where pre-defined report tools are unavailable, you should be able to create the reports using the other tools mentioned earlier.
- Note that for some tables like supplier, shipper, customer, the 'companyname' column has the business relationship (like 'Supplier', 'Customer') along with the name of the entity. Eg: 'Customer NRZBB', 'Shipper ETYNR' are entries for 'companyname' column in customer and shipper tables respectively. In these cases, use "like" operator in SQL queries to match partial names.
- Also, note that for table 'product', the 'productname' column has the actual product name after the word 'Product'. Eg: 'Product IMEHJ'. In these cases, use "like" operator in SQL queries to match partial names. Also, remove the word 'Product' when specifying the product name.
- Explain what you're doing when you use tools

Be helpful and choose the right tool for each question."""),

            ("user", "{input}"),  # user's question goes here, passed in at runtime by AgentExecutor
            ("assistant", "{agent_scratchpad}")  # gets filled by LangChain with the agent's reasoning process
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)  # Create an agent that uses OpenAI function calling - generates and executes tool function calls directly
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    
    def ask(self, question: str) -> str:
        """Ask the agent a question"""
        if not self.agent_executor:
            return "Agent not initialized. Please check MCP server connection."
        
        try:
            result = self.agent_executor.invoke({"input": question})
            print(f"Agent response: {result}")
            return result["output"]  # AgentExecutor returns a dict with "output" key containing the final answer
        except Exception as e:
            self.logger.error(f"Error occurred while asking question: {e}")
            return f"Error: {str(e)}"