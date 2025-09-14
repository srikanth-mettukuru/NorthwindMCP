from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_mcp import MCPToolkit
import logging
import os
from dotenv import load_dotenv

class NorthwindAgent:
    """Agent that acts as a MCP Client to interact with Northwind database via the Northwind MCP server"""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self.logger = logging.getLogger(__name__)
        
        # Get configuration from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        mcp_server_path = os.getenv("MCP_SERVER_PATH")
        
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        if not mcp_server_path:
            raise ValueError("MCP_SERVER_PATH not found in environment variables")
        
        # Initialize OpenAI LLM
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4.1-mini",
            temperature=0
        )
        
        # Create MCP toolkit - automatically handles MCP connection
        try:
            self.mcp_toolkit = MCPToolkit(
                server_path=mcp_server_path,
                server_params=["python", mcp_server_path],
                working_directory="../northwind-mcp-server"
            )
            
            # Get tools from MCP server
            self.tools = self.mcp_toolkit.get_tools()
            self.logger.info(f"Loaded {len(self.tools)} MCP tools")
            
            # Create the agent
            self.agent_executor = self._create_agent()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP toolkit: {e}")
            self.tools = []
            self.agent_executor = None
    
    def _create_agent(self):
        """Create LangChain agent with MCP tools"""
        if not self.tools:
            return None
        
        # Create system prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful Northwind database assistant.

You have access to database tools that let you query and analyze the Northwind database.
The database contains tables like: customer, salesorder, product, employee, supplier, shipper, territory, etc.

When users ask questions:
- Use the appropriate tools to get the information they need
- For SQL queries, write proper SELECT statements 
- Use LIMIT clauses to avoid returning too much data at once
- Be conversational and explain what you're doing
- If there are errors, explain them clearly to the user

Help users explore and understand their Northwind data!"""),
            ("user", "{input}"),  # user's question goes here, passed in at runtime by AgentExecutor
            ("assistant", "{agent_scratchpad}")  # gets filled by LangChain with the agent's reasoning process
        ])
        
        # Create agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            return_intermediate_steps=False
        )
    
    def ask(self, question: str) -> str:
        """Ask the agent a question about the Northwind database"""
        if not self.agent_executor:
            return "Agent not initialized. Please check MCP server connection."
        
        try:
            self.logger.info(f"Processing question: {question}")
            
            result = self.agent_executor.invoke({"input": question})
            return result["output"]
            
        except Exception as e:
            self.logger.error(f"Error processing question: {e}")
            return f"Sorry, I encountered an error while processing your question: {str(e)}"