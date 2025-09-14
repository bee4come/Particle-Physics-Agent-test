"""LaTeX stdio MCP client for FeynmanCraft ADK."""

import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LatexStdioMCPClient:
    """Client for communicating with LaTeX MCP server via stdio."""
    
    def __init__(self):
        self.server_path = Path(__file__).parent.parent.parent.parent / "experimental" / "latex_mcp" / "stdio_server.py"
        
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server."""
        try:
            # Prepare the MCP request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Start the server process
            cmd = [sys.executable, str(self.server_path)]
            logger.info(f"Starting MCP server: {' '.join(cmd)}")
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send the request
            request_json = json.dumps(request) + "\n"
            stdout, stderr = await proc.communicate(request_json.encode())
            
            # Log stderr for debugging
            if stderr:
                logger.info(f"MCP server stderr: {stderr.decode()}")
                
            # Parse the response
            if stdout:
                try:
                    response = json.loads(stdout.decode().strip())
                    if "result" in response:
                        return response["result"]
                    elif "error" in response:
                        logger.error(f"MCP server error: {response['error']}")
                        return {
                            "status": "error", 
                            "errors": [{"message": response["error"].get("message", "Unknown MCP error")}],
                            "warnings": []
                        }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse MCP response: {e}")
                    logger.error(f"Raw stdout: {stdout.decode()}")
            
            return {
                "status": "error",
                "errors": [{"message": "No valid response from MCP server"}],
                "warnings": []
            }
            
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return {
                "status": "error",
                "errors": [{"message": f"MCP client error: {str(e)}"}],
                "warnings": []
            }

# Global client instance
_mcp_client = LatexStdioMCPClient()

async def compile_tikz_mcp(
    tikz_code: str, 
    engine: str = "lualatex", 
    format_type: str = "all"
) -> Optional[Dict[str, Any]]:
    """Compile TikZ code using the MCP server.
    
    Args:
        tikz_code: The TikZ code to compile
        engine: LaTeX engine to use (pdflatex or lualatex)
        format_type: Output format (pdf, svg, png, or all)
        
    Returns:
        Compilation result dictionary or None if failed
    """
    try:
        logger.info(f"Compiling TikZ code via MCP: engine={engine}, format={format_type}")
        
        result = await _mcp_client.call_tool("latex_compile", {
            "tikz": tikz_code,
            "engine": engine,
            "format": format_type
        })
        
        if result and result.get("status") == "success":
            logger.info("TikZ compilation successful via MCP")
        else:
            logger.warning(f"TikZ compilation failed via MCP: {result}")
            
        return result
        
    except Exception as e:
        logger.error(f"Error in compile_tikz_mcp: {e}")
        return None