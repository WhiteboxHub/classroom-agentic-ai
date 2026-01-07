"""
MCP Registry
Registers and manages MCP-style tools for agents.
"""
from typing import Dict, Any, Callable, List
import logging

logger = logging.getLogger(__name__)


class MCPRegistry:
    """
    Registry for MCP-style tools.
    Provides a centralized way to register and access tools.
    """
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
    
    def register_tool(
        self,
        name: str,
        function: Callable,
        description: str,
        parameters: Dict[str, Any]
    ) -> None:
        """
        Register a tool in the registry.
        
        Args:
            name: Tool name
            function: Callable function
            description: Tool description
            parameters: Parameter schema
        """
        self.tools[name] = {
            "function": function,
            "description": description,
            "parameters": parameters
        }
        logger.info(f"Registered tool: {name}")
    
    def get_tool(self, name: str) -> Dict[str, Any]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self.tools.keys())
    
    def execute_tool(self, name: str, **kwargs) -> Any:
        """
        Execute a tool by name.
        
        Args:
            name: Tool name
            **kwargs: Tool arguments
            
        Returns:
            Tool execution result
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found in registry")
        
        try:
            result = tool["function"](**kwargs)
            logger.info(f"Executed tool: {name}")
            return result
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}", exc_info=True)
            raise


# Global registry instance
registry = MCPRegistry()

