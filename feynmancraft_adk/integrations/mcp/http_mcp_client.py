"""
HTTP MCP Client for ParticlePhysics MCP Server
Connects to the HTTP API server running on port 8002
"""

import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
import logging
import uuid

logger = logging.getLogger(__name__)


class HTTPParticlePhysicsMCPClient:
    """HTTP client for the ParticlePhysics MCP Server."""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        """Initialize the HTTP MCP client."""
        self.base_url = base_url
        self.session = None
        self._connected = False
        
    async def connect(self) -> bool:
        """Connect to the HTTP MCP server."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Test connection with a simple request
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    self._connected = True
                    logger.info("Connected to ParticlePhysics HTTP MCP Server")
                    return True
                else:
                    logger.error(f"HTTP MCP server returned status {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to connect to HTTP MCP server: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the HTTP MCP server."""
        if self.session:
            await self.session.close()
            self.session = None
        self._connected = False
        logger.info("Disconnected from HTTP MCP server")
    
    async def call_tool(self, name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a tool on the HTTP MCP server."""
        if arguments is None:
            arguments = {}
            
        if not self._connected or not self.session:
            await self.connect()
        
        if not self._connected:
            raise Exception("Not connected to MCP server")
        
        try:
            # Create JSON-RPC request
            request_data = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": name,
                    "arguments": arguments
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-Client-Origin": "http://localhost:8000"
            }
            
            logger.info(f"Calling HTTP MCP tool: {name} with args: {arguments}")
            
            async with self.session.post(
                f"{self.base_url}/mcp",
                json=request_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {response.reason}")
                
                result_data = await response.json()
                
                if "error" in result_data:
                    raise Exception(f"MCP Error: {result_data['error']}")
                
                logger.info(f"HTTP MCP tool {name} completed successfully")
                return result_data.get("result", {})
                
        except Exception as e:
            logger.error(f"HTTP MCP tool call failed: {e}")
            raise
    
    async def search_particle(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for particles using the HTTP MCP server."""
        return await self.call_tool("search_particle", {"query": query, "limit": limit})
    
    async def get_property(self, particle_id: str, quantity: str, pedantic: bool = False) -> Dict[str, Any]:
        """Get particle property using the HTTP MCP server."""
        return await self.call_tool("get_property", {
            "id": particle_id,
            "quantity": quantity,
            "pedantic": pedantic
        })
    
    async def list_decays(self, particle_id: str, limit: int = 50, min_branching_ratio: float = 0) -> Dict[str, Any]:
        """List particle decays using the HTTP MCP server."""
        return await self.call_tool("list_decays", {
            "id": particle_id,
            "limit": limit,
            "min_branching_ratio": min_branching_ratio
        })
    
    async def find_decays(self, final_state: List[str], min_branching_ratio: float = 0) -> Dict[str, Any]:
        """Find decays by final state using the HTTP MCP server."""
        return await self.call_tool("find_decays", {
            "final_state": final_state,
            "min_branching_ratio": min_branching_ratio
        })
    
    async def list_properties(self, particle_id: str) -> Dict[str, Any]:
        """List all properties of a particle using the HTTP MCP server."""
        return await self.call_tool("list_properties", {"id": particle_id})
    
    async def resolve_identifier(self, identifier: str) -> Dict[str, Any]:
        """Resolve particle identifier using the HTTP MCP server."""
        return await self.call_tool("resolve_identifier", {"any": identifier})
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Get database information using the HTTP MCP server."""
        return await self.call_tool("database_info", {})