#!/usr/bin/env python
"""
Script to generate a sitemap on the server and optionally download it.

This script can be run in two modes:
1. Server mode: Generates the sitemap.xml file and optionally serves it for download
2. Download mode: Downloads the sitemap.xml from the server

Usage:
    # On the server, to generate the sitemap:
    python generate_and_download_sitemap.py --generate

    # On the server, to generate and serve the sitemap:
    python generate_and_download_sitemap.py --generate --serve

    # On your local machine, to download the sitemap:
    python generate_and_download_sitemap.py --download SERVER_IP:PORT
"""

import os
import sys
import http.server
import socketserver
import urllib.request
import argparse
import subprocess
import socket
import time

def generate_sitemap():
    """Generate the sitemap.xml file using Django's management command"""
    try:
        print("Generating sitemap.xml...")
        
        # Check if we're in a Django project
        if os.path.exists('manage.py'):
            # Try using the management command first
            result = subprocess.run(
                ['python', 'manage.py', 'generate_sitemap'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(result.stdout)
                print("Sitemap generated successfully using management command")
                return True
            else:
                print("Management command failed, trying standalone script...")
        
        # Fall back to the standalone script
        if os.path.exists('generate_sitemap.py'):
            result = subprocess.run(
                ['python', 'generate_sitemap.py'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(result.stdout)
                print("Sitemap generated successfully using standalone script")
                return True
            else:
                print(f"Failed to generate sitemap: {result.stderr}")
                return False
        else:
            print("Error: Could not find generate_sitemap.py")
            return False
    
    except Exception as e:
        print(f"Error generating sitemap: {e}")
        return False

def serve_sitemap(port=8000):
    """Serve the sitemap.xml file via HTTP server"""
    # Check if sitemap.xml exists
    if not os.path.exists('sitemap.xml'):
        print("Error: sitemap.xml not found. Generate it first with --generate")
        return False
    
    # Get server IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except:
        ip_address = "127.0.0.1"
    
    print(f"Starting HTTP server on port {port}")
    print(f"Sitemap URL: http://{ip_address}:{port}/sitemap.xml")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Create a simple handler that only serves sitemap.xml
        class SitemapHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/sitemap.xml':
                    # Serve the sitemap file
                    self.send_response(200)
                    self.send_header("Content-type", "application/xml")
                    self.end_headers()
                    
                    with open('sitemap.xml', 'rb') as f:
                        self.wfile.write(f.read())
                else:
                    # For security, only allow sitemap.xml
                    self.send_response(403)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b"Access denied. Only sitemap.xml is available.")
        
        # Start the HTTP server
        with socketserver.TCPServer(("", port), SitemapHandler) as httpd:
            httpd.serve_forever()
    
    except KeyboardInterrupt:
        print("\nServer stopped")
        return True
    except Exception as e:
        print(f"Error serving sitemap: {e}")
        return False

def download_sitemap(server_url, output_file='sitemap.xml'):
    """Download the sitemap.xml file from the server"""
    try:
        if "://" not in server_url:
            server_url = f"http://{server_url}"
        
        if not server_url.endswith('/sitemap.xml'):
            server_url = f"{server_url}/sitemap.xml"
        
        print(f"Downloading sitemap from {server_url}...")
        
        # Set a reasonable timeout (30 seconds)
        socket.setdefaulttimeout(30)
        
        start_time = time.time()
        with urllib.request.urlopen(server_url) as response:
            sitemap_content = response.read()
            
            with open(output_file, 'wb') as f:
                f.write(sitemap_content)
        
        elapsed = time.time() - start_time
        size_kb = len(sitemap_content) / 1024
        
        print(f"Download complete: {output_file}")
        print(f"Size: {size_kb:.1f} KB")
        print(f"Time: {elapsed:.2f} seconds")
        
        return True
    
    except Exception as e:
        print(f"Error downloading sitemap: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate and download sitemap.xml")
    
    # Define action groups
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--generate', action='store_true', help='Generate the sitemap.xml file')
    group.add_argument('--download', metavar='SERVER_URL', help='Download sitemap.xml from the server')
    
    # Additional options
    parser.add_argument('--serve', action='store_true', help='Serve the generated sitemap.xml')
    parser.add_argument('--port', type=int, default=8000, help='Port to serve the sitemap on (default: 8000)')
    parser.add_argument('--output', metavar='FILE', default='sitemap.xml', help='Output filename (default: sitemap.xml)')
    
    args = parser.parse_args()
    
    if args.generate:
        success = generate_sitemap()
        if success and args.serve:
            return serve_sitemap(args.port)
        return success
    
    elif args.download:
        return download_sitemap(args.download, args.output)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
