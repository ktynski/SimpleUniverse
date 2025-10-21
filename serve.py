#!/usr/bin/env python3
"""
Simple HTTP server for testing visualization without CORS issues.
Run with: python3 serve.py
Then open: http://localhost:8000/
"""

import http.server
import socketserver
import os

PORT = 8000

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow cross-origin access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"🌌 SCCMU Visualization Server")
        print(f"Server running at http://localhost:{PORT}")
        print(f"")
        print(f"Open these URLs in your browser:")
        print(f"  • Main visualization: http://localhost:{PORT}/")
        print(f"  • Standalone test: http://localhost:{PORT}/test_temporal_standalone.html")
        print(f"  • Full test suite: http://localhost:{PORT}/test_temporal.html")
        print(f"")
        print(f"Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
