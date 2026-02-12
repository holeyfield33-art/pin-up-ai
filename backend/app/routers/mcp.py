"""MCP (Model Context Protocol) endpoints."""

import logging
from fastapi import APIRouter, HTTPException
from typing import Any, Dict

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mcp", tags=["mcp"])

# Lazy-load MCP server to avoid circular imports
_mcp_server = None


def get_mcp_server():
    """Get MCP server instance with lazy loading."""
    global _mcp_server
    if _mcp_server is None:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mcp"))
        from server import mcp_server
        _mcp_server = mcp_server
    return _mcp_server


@router.get("/tools", response_model=list)
async def get_mcp_tools():
    """Get all available MCP tools."""
    try:
        mcp_server = get_mcp_server()
        return mcp_server.get_tools()
    except Exception as e:
        logger.error(f"Error getting MCP tools: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get tools")


@router.post("/tools/{tool_name}/call", response_model=Dict[str, Any])
async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]):
    """Call an MCP tool."""
    try:
        mcp_server = get_mcp_server()
        result = await mcp_server.call_tool(tool_name, **arguments)
        return result
    except Exception as e:
        logger.error(f"Error calling MCP tool {tool_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to call tool")
