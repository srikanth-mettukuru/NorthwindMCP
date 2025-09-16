import subprocess
import json
import logging
import os
from typing import Dict, List, Any

class MCPClient:
    """Simple MCP client to communicate with the Northwind MCP server"""
    
    def __init__(self, server_path: str):
        self.server_path = server_path
        self.logger = logging.getLogger(__name__)
    
    def _send_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server and return the response"""
        try:
            # Get Python executable from environment variable or use default
            python_executable = os.getenv("MCP_SERVER_PYTHON", "python")

            # Determine the correct working directory based on server path
            server_dir = os.path.dirname(self.server_path)
            if server_dir == "":
                # If server_path is just a filename, use current directory
                server_dir = "."
        
            # Start MCP server as a subprocess
            process = subprocess.Popen(
                [python_executable, self.server_path],  # Use configurable Python executable
                stdin=subprocess.PIPE,   # create a pipe to send data to the server
                stdout=subprocess.PIPE,  # create a pipe to receive data from the server
                stderr=subprocess.PIPE,  # create a pipe for error messages
                text=True,   # data is text, not bytes
                cwd=server_dir  # change to the server directory before running the Python script
            )
            
            # Initialize connection first
            init_request = {
                "jsonrpc": "2.0",  # JSON-RPC 2.0 - Standard protocol that MCP uses
                "id": 1,
                "method": "initialize",  # required first step to establish MCP connection
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "northwind-mcp-client", "version": "1.0.0"}
                }
            }
            
            # Send initialization
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Read initialization response
            init_response_line = process.stdout.readline()
            
            # Send initialized notification (required by MCP protocol)
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            process.stdin.write(json.dumps(initialized_notification) + "\n")
            process.stdin.flush()
            
            # Now send actual request
            process.stdin.write(json.dumps(request) + "\n")
            process.stdin.flush()
            
            # Read actual response
            actual_response = process.stdout.readline()
            
            # Clean up
            process.terminate()  # Gracefully terminate the server process
            process.wait()  # Wait for the server process to exit

            # Parse and return actual response
            response = json.loads(actual_response)
            
            # Check for JSON-RPC error response
            if "error" in response:
                error_info = response["error"]
                self.logger.error(f"MCP server returned error: {error_info}")
                return {"status": "error", "error": error_info.get("message", "Unknown error")}
            
            # Return successful result (JSON-RPC success responses always have "result")
            return response.get("result", {})
            
        except Exception as e:
            self.logger.error(f"Error sending MCP request: {e}")
            return {"status": "error", "error": str(e)}
        
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a specific MCP tool"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",  # MCP method to call a tool
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }
        
        result = self._send_mcp_request(request)
        if result.get("status") == "error":
            self.logger.error(f"Error calling MCP tool {tool_name}: {result.get('error')}")
        
        return result
    

    def get_available_tools(self) -> Dict[str, Any]:
        """Discover available tools from MCP server"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"  # MCP method to list available tools
        }
        
        result = self._send_mcp_request(request)
        if result.get("status") == "error":
            self.logger.error(f"Error discovering tools: {result.get('error')}")
            return {"tools": []}
        
        return result