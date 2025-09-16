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
        process = None
        try:
            # Get Python executable from environment variable or use default
            python_executable = os.getenv("MCP_SERVER_PYTHON", "python")

            # Determine the correct working directory based on server path
            server_dir = os.path.dirname(self.server_path)
            if server_dir == "":
                # If server_path is just a filename, use current directory
                server_dir = "."
            
            self.logger.debug(f"Starting MCP server: {python_executable} {self.server_path} in directory {server_dir}")
        
            # Start MCP server as a subprocess
            process = subprocess.Popen(
                [python_executable, self.server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=server_dir
            )
        
            # Give the server a moment to start up
            import time
            time.sleep(0.5)
        
            # Check if process is still running
            if process.poll() is not None:
                # Process has already terminated - read error output
                stdout_data, stderr_data = process.communicate()
                error_msg = f"MCP server process terminated immediately. "
                error_msg += f"Exit code: {process.returncode}. "
                if stderr_data:
                    error_msg += f"Stderr: {stderr_data.strip()}. "
                if stdout_data:
                    error_msg += f"Stdout: {stdout_data.strip()}."
                
                self.logger.error(error_msg)
                return {"status": "error", "error": error_msg}
            
            # Initialize connection first
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "northwind-mcp-client", "version": "1.0.0"}
                }
            }
        
            # Send initialization
            try:
                process.stdin.write(json.dumps(init_request) + "\n")
                process.stdin.flush()
            except BrokenPipeError as e:
                # Get any error output from the server
                try:
                    stdout_data, stderr_data = process.communicate(timeout=2)
                    error_msg = f"Broken pipe during initialization. Server stderr: {stderr_data}"
                    self.logger.error(error_msg)
                    return {"status": "error", "error": error_msg}
                except subprocess.TimeoutExpired:
                    process.kill()
                    return {"status": "error", "error": "Server not responding during initialization"}
        
            # Read initialization response
            try:
                init_response_line = process.stdout.readline()
                if not init_response_line:
                    # No response - server likely crashed
                    stdout_data, stderr_data = process.communicate()
                    error_msg = f"No initialization response from server. Stderr: {stderr_data}"
                    self.logger.error(error_msg)
                    return {"status": "error", "error": error_msg}
            except Exception as e:
                self.logger.error(f"Error reading initialization response: {e}")
                return {"status": "error", "error": f"Error reading initialization response: {e}"}
            
            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
        
            try:
                process.stdin.write(json.dumps(initialized_notification) + "\n")
                process.stdin.flush()
            except BrokenPipeError:
                stdout_data, stderr_data = process.communicate()
                error_msg = f"Broken pipe during initialized notification. Server stderr: {stderr_data}"
                self.logger.error(error_msg)
                return {"status": "error", "error": error_msg}
            
            # Now send actual request
            try:
                process.stdin.write(json.dumps(request) + "\n")
                process.stdin.flush()
            except BrokenPipeError:
                stdout_data, stderr_data = process.communicate()
                error_msg = f"Broken pipe during actual request. Server stderr: {stderr_data}"
                self.logger.error(error_msg)
                return {"status": "error", "error": error_msg}
        
            # Read actual response
            try:
                actual_response = process.stdout.readline()
                if not actual_response:
                    stdout_data, stderr_data = process.communicate()
                    error_msg = f"No response from server. Stderr: {stderr_data}"
                    self.logger.error(error_msg)
                    return {"status": "error", "error": error_msg}
            except Exception as e:
                self.logger.error(f"Error reading response: {e}")
                return {"status": "error", "error": f"Error reading response: {e}"}

            # Parse and return actual response
            try:
                response = json.loads(actual_response)
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON response: {actual_response}")
                return {"status": "error", "error": f"Invalid JSON response: {actual_response}"}
            
            # Check for JSON-RPC error response
            if "error" in response:
                error_info = response["error"]
                self.logger.error(f"MCP server returned error: {error_info}")
                return {"status": "error", "error": error_info.get("message", "Unknown error")}
            
            # Return successful result
            return response.get("result", {})
        
        except Exception as e:
            self.logger.error(f"Error sending MCP request: {e}")
            return {"status": "error", "error": str(e)}
        
        finally:
            # Clean up process
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    self.logger.warning(f"Error cleaning up process: {e}")
        
    
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