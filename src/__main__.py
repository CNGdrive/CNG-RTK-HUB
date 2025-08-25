"""
Main entry point for CNG-RTK-HUB package.
Allows the package to be run as: python -m src
"""

import argparse
import asyncio
import logging
import sys
from src.rtk_service import RTKService


def main():
    """Main entry point for RTK service."""
    parser = argparse.ArgumentParser(description='CNG-RTK-HUB Universal RTK Client')
    parser.add_argument('--port', type=int, default=8080, help='WebSocket server port')
    parser.add_argument('--http-port', type=int, default=8081, help='HTTP server port')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--config', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run RTK service
    service = RTKService()
    
    try:
        asyncio.run(service.start(
            ws_port=args.port,
            http_port=args.http_port,
            config_file=args.config
        ))
    except KeyboardInterrupt:
        print("\nShutting down RTK service...")
    except Exception as e:
        print(f"Error starting RTK service: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
