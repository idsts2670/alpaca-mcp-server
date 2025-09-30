# server.py
#
# Alpaca MCP Server Core Implementation
# Location: /src/alpaca_mcp_server/server.py
# Purpose: Main server class that initializes MCP server and Alpaca clients

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Import configuration management
from .config import ConfigManager


class AlpacaMCPServer:
    """
    Alpaca MCP Server - Trading API integration for Model Context Protocol.

    This class encapsulates the MCP server initialization and provides
    a clean interface for starting the server with different transport methods.
    """

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize the Alpaca MCP Server.

        Args:
            config_file: Path to .env configuration file (defaults to current directory)
        """
        # Initialize configuration manager
        self.config = ConfigManager(config_file)

        # Load environment variables
        if self.config.env_file.exists():
            load_dotenv(self.config.env_file)

        # Initialize MCP server (will be set up in _initialize_server)
        self.mcp: Optional[FastMCP] = None

        # Alpaca clients (will be initialized when server starts)
        self._clients_initialized = False

    def _detect_environment(self) -> str:
        """
        Detect the runtime environment for appropriate log level.

        Returns:
            Appropriate log level based on environment detection
        """
        # Check for PyCharm environment
        mcp_client = os.getenv("MCP_CLIENT", "").lower()
        if mcp_client == "pycharm":
            return "ERROR"  # Reduce noise in PyCharm

        # Check for debug mode
        if os.getenv("DEBUG", "False").lower() == "true":
            return "DEBUG"

        return "INFO"  # Default log level

    def _validate_credentials(self) -> bool:
        """
        Validate that required Alpaca API credentials are available.

        Returns:
            True if credentials are valid, False otherwise
        """
        api_key = os.getenv("ALPACA_API_KEY")
        secret_key = os.getenv("ALPACA_SECRET_KEY")

        if not api_key or not secret_key:
            print("Error: Alpaca API credentials not found in environment variables.")
            print("Run 'alpaca-mcp init' to configure your API keys.")
            return False

        return True

    def _initialize_server(self) -> None:
        """
        Initialize the FastMCP server and import all trading tools.

        This method dynamically imports the original server implementation
        to maintain all existing functionality while providing a clean interface.
        """
        # Validate credentials before initializing
        if not self._validate_credentials():
            raise ValueError("Invalid or missing Alpaca API credentials")

        # Detect appropriate log level
        log_level = self._detect_environment()

        # Initialize FastMCP server
        self.mcp = FastMCP("alpaca-trading", log_level=log_level)

        # Import and register all tools from the original implementation
        self._import_original_tools()

        self._clients_initialized = True

    def _import_original_tools(self) -> None:
        """
        Import all tools from the original alpaca_mcp_server.py implementation.

        This approach maintains backward compatibility by reusing the existing
        comprehensive tool implementations without code duplication.
        """
        # Add the project root to Python path to import the original server
        project_root = Path(__file__).parent.parent.parent
        original_server_path = project_root / "alpaca_mcp_server.py"

        if not original_server_path.exists():
            raise FileNotFoundError(f"Original server file not found: {original_server_path}")

        # Add project root to path temporarily
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        try:
            # Import the original server module
            # This will execute all the tool registrations on our mcp instance
            import alpaca_mcp_server as original_server

            # Copy the configured mcp instance with all registered tools
            # The original server module registers tools on a global 'mcp' variable
            if hasattr(original_server, 'mcp'):
                # Transfer all registered tools to our instance
                self.mcp = original_server.mcp
            else:
                raise RuntimeError("Original server module does not have 'mcp' instance")

        except ImportError as e:
            raise ImportError(f"Failed to import original server implementation: {e}")
        finally:
            # Clean up path
            if str(project_root) in sys.path:
                sys.path.remove(str(project_root))

    def run(self, transport: str = "stdio", host: str = "127.0.0.1", port: int = 8000) -> None:
        """
        Start the Alpaca MCP Server with the specified transport method.

        Args:
            transport: Transport method ("stdio", "http", or "sse")
            host: Host to bind for HTTP/SSE transport
            port: Port to bind for HTTP/SSE transport
        """
        # Initialize server if not already done
        if not self._clients_initialized:
            self._initialize_server()

        # Validate transport method
        if transport not in ["stdio", "http", "sse"]:
            raise ValueError(f"Unsupported transport method: {transport}")

        # Show deprecation warning for SSE
        if transport == "sse":
            print("Warning: SSE transport is deprecated. Consider using HTTP transport instead.")

        # Print startup information (except in PyCharm to reduce noise)
        if os.getenv("MCP_CLIENT", "").lower() != "pycharm":
            print(f"Starting Alpaca MCP Server (transport={transport})")
            if transport in ["http", "sse"]:
                print(f"   Server will be available at: http://{host}:{port}")

        # Start the server with appropriate transport configuration
        if transport == "stdio":
            # Standard I/O transport (default for most MCP clients)
            self.mcp.run()
        else:
            # HTTP or SSE transport for remote connections
            self.mcp.run(transport=transport, host=host, port=port)

    def get_status(self) -> Dict[str, Any]:
        """
        Get current server status and configuration summary.

        Returns:
            Dictionary containing server status information
        """
        return {
            "server_initialized": self._clients_initialized,
            "config_file": str(self.config.env_file),
            "config_exists": self.config.env_file.exists(),
            "config_valid": self.config.validate_config(),
            "config_summary": self.config.get_config_summary()
        }


def main():
    """
    Main entry point for direct server execution.

    This function provides backward compatibility with the original
    alpaca_mcp_server.py script when run directly.
    """
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Alpaca MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport method to use (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind for HTTP/SSE transport (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind for HTTP/SSE transport (default: 8000)"
    )

    args = parser.parse_args()

    # Create and start the server
    try:
        server = AlpacaMCPServer()
        server.run(transport=args.transport, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()