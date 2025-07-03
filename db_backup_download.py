"""
Database Backup and Download Utility for GolfPlex

This script helps with:
1. Creating a backup of the SQLite database on the server
2. Starting a simple HTTP server to serve the database file
3. Downloading the database file with resume capability and extended timeout

Usage:
1. Run this script on your server to create a backup and serve it
   python db_backup_download.py --server
   
2. Run this script on your local machine to download the database
   python db_backup_download.py --download SERVER_IP:PORT OUTPUT_FILENAME

Example:
   # On server:
   python db_backup_download.py --server
   
   # On local machine:
   python db_backup_download.py --download 159.223.94.36:8000 ./db_production.sqlite3
"""

import os
import sys
import time
import shutil
import argparse
import subprocess
import http.server
import socketserver
import urllib.request
import socket
import threading
from datetime import datetime
from http.client import HTTPConnection

def create_backup(db_path, backup_dir="./backups"):
    """Create a backup of the database file"""
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return None
        
    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{backup_dir}/db_backup_{timestamp}.sqlite3"
    
    # Create a copy of the database
    try:
        shutil.copy2(db_path, backup_filename)
        print(f"Backup created: {backup_filename}")
        
        # Also create a copy with a consistent name for download
        download_copy = "./db_download.sqlite3"
        shutil.copy2(db_path, download_copy)
        print(f"Download copy created: {download_copy}")
        
        return backup_filename
    except Exception as e:
        print(f"Backup failed: {e}")
        return None

def start_http_server(port=8000, directory="."):
    """Start a simple HTTP server to serve files"""
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        # Try to get the server's IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except:
        ip_address = "127.0.0.1"
    
    print(f"Starting HTTP server at http://{ip_address}:{port}")
    print(f"Serving files from {os.path.abspath(directory)}")
    print(f"Download URL: http://{ip_address}:{port}/db_download.sqlite3")
    print("Press Ctrl+C to stop the server")
    
    # Change to the specified directory
    os.chdir(directory)
    
    # Start the HTTP server
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

def download_file_with_resume(url, output_filename, timeout=300, chunk_size=8192):
    """Download a file with resume capability and extended timeout"""
    temp_filename = output_filename + '.part'
    resume_from = 0
    
    # Check if we can resume download
    if os.path.exists(temp_filename):
        resume_from = os.path.getsize(temp_filename)
        print(f"Resuming download from {resume_from / (1024*1024):.2f} MB")
    
    # Set socket timeout
    socket.setdefaulttimeout(timeout)
    
    start_time = time.time()
    total_size = 0
    
    try:
        # Parse URL
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
            
        print(f"Downloading {url}")
        print(f"Timeout set to {timeout} seconds")
        print(f"Output file: {output_filename}")
        
        # Create request with Range header if resuming
        request = urllib.request.Request(url)
        if resume_from > 0:
            request.add_header('Range', f'bytes={resume_from}-')
        
        with urllib.request.urlopen(request) as response:
            # Get file size if available
            if 'Content-Length' in response.headers:
                file_size = int(response.headers['Content-Length'])
                if resume_from > 0:
                    file_size += resume_from  # Adjust for resumed download
                print(f"Total file size: {file_size / (1024*1024):.2f} MB")
            else:
                file_size = 0
            
            # Open file for writing or appending
            with open(temp_filename, 'ab' if resume_from > 0 else 'wb') as out_file:
                downloaded = resume_from
                
                # Download in chunks
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    
                    out_file.write(chunk)
                    downloaded += len(chunk)
                    total_size += len(chunk)
                    
                    # Print progress
                    elapsed = time.time() - start_time
                    if file_size > 0:
                        percent = downloaded * 100 / file_size
                        print(f"\rProgress: {percent:.1f}% - {downloaded / (1024*1024):.2f} MB - {elapsed:.1f}s", end="", flush=True)
                    else:
                        print(f"\rDownloaded: {downloaded / (1024*1024):.2f} MB - {elapsed:.1f}s", end="", flush=True)
        
        # Rename the temp file to the final filename
        if os.path.exists(output_filename):
            os.remove(output_filename)
        os.rename(temp_filename, output_filename)
        
        print(f"\nDownload complete: {output_filename}")
        print(f"Total size: {(resume_from + total_size) / (1024*1024):.2f} MB")
        print(f"Time elapsed: {time.time() - start_time:.1f} seconds")
        return True
        
    except Exception as e:
        print(f"\nDownload failed: {e}")
        print("You can resume the download by running the command again.")
        return False

def download_chunked(host, path, output_file, timeout=300, chunk_size=1024*1024):
    """Download a file using chunked download with timeout and resume capability"""
    start_time = time.time()
    total_size = 0
    resume_from = 0
    
    # Check if partial file exists and get size for resume
    temp_file = output_file + '.part'
    if os.path.exists(temp_file):
        resume_from = os.path.getsize(temp_file)
        print(f"Resuming from {resume_from / (1024*1024):.2f} MB")
    
    try:
        with open(temp_file, 'ab') as f:
            # Get file size first
            conn = HTTPConnection(host, timeout=timeout)
            conn.request("HEAD", path)
            response = conn.getresponse()
            
            if response.status == 200 and 'content-length' in response.headers:
                file_size = int(response.headers['content-length'])
                print(f"Total file size: {file_size / (1024*1024):.2f} MB")
            else:
                file_size = 0
                print("Unable to determine file size")
            conn.close()
            
            # Download in chunks
            while True:
                # Create a new connection for each chunk (helps with timeouts)
                conn = HTTPConnection(host, timeout=timeout)
                
                # Set range header to request next chunk
                headers = {}
                if resume_from > 0:
                    end_byte = min(resume_from + chunk_size - 1, file_size - 1) if file_size > 0 else resume_from + chunk_size - 1
                    headers['Range'] = f'bytes={resume_from}-{end_byte}'
                
                try:
                    print(f"\rRequesting bytes {resume_from}-{resume_from + chunk_size - 1}", end="", flush=True)
                    conn.request("GET", path, headers=headers)
                    response = conn.getresponse()
                    
                    # If we get a 200 or 206 (partial content) response
                    if response.status in [200, 206]:
                        # Read the data
                        data = response.read()
                        if not data:
                            print("\nDownload complete (server sent no more data)")
                            break
                            
                        # Write chunk to file
                        f.write(data)
                        chunk_actual_size = len(data)
                        resume_from += chunk_actual_size
                        total_size += chunk_actual_size
                        
                        # Print progress
                        elapsed = time.time() - start_time
                        if file_size > 0:
                            percent = resume_from * 100 / file_size
                            print(f"\rProgress: {percent:.1f}% - {resume_from / (1024*1024):.2f} MB - {elapsed:.1f}s", end="", flush=True)
                        else:
                            print(f"\rDownloaded: {resume_from / (1024*1024):.2f} MB - {elapsed:.1f}s", end="", flush=True)
                        
                        # If we got less data than requested, we're done
                        if chunk_actual_size < chunk_size or (file_size > 0 and resume_from >= file_size):
                            print("\nDownload complete!")
                            break
                    else:
                        print(f"\nServer returned error: {response.status} {response.reason}")
                        if response.status == 416:  # Range Not Satisfiable - file fully downloaded
                            print("Download appears to be complete (server says requested range is invalid)")
                            break
                        else:
                            return False
                            
                except Exception as e:
                    print(f"\nConnection error: {e}. Retrying in 3 seconds...")
                    time.sleep(3)
                    continue
                finally:
                    conn.close()
        
        # Rename the temp file to the final filename
        if os.path.exists(output_file):
            os.remove(output_file)
        os.rename(temp_file, output_file)
        
        print(f"\nDownload complete: {output_file}")
        print(f"Total size: {resume_from / (1024*1024):.2f} MB")
        print(f"Time elapsed: {time.time() - start_time:.1f} seconds")
        return True
        
    except Exception as e:
        print(f"\nDownload failed: {e}")
        print("You can resume the download by running the command again.")
        return False

def server_mode():
    """Run in server mode - create backup and start HTTP server"""
    # Find the database file
    db_paths = [
        "./db.sqlite3",
        "./db_production.sqlite3",
        "/home/golfplex/golfplex/db.sqlite3",
        "/home/golfplex/golfplex/db_production.sqlite3"
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if db_path is None:
        print("Error: Could not find the database file")
        print("Please specify the path to the database file")
        return False
    
    print(f"Found database at: {db_path}")
    
    # Create a backup
    backup_file = create_backup(db_path)
    if not backup_file:
        print("Backup failed, but we can still serve the original file")
    
    # Start HTTP server
    try:
        start_http_server(port=8000, directory=".")
    except KeyboardInterrupt:
        print("\nServer stopped")
    
    return True

def download_mode(url, output_file, timeout=600):
    """Run in download mode - download the database from server"""
    if ":" in url and "/" not in url:
        # Format is host:port, need to add path
        host = url
        path = "/db_download.sqlite3"
        return download_chunked(host, path, output_file, timeout)
    elif "://" not in url:
        url = "http://" + url
    
    return download_file_with_resume(url, output_file, timeout)

def main():
    parser = argparse.ArgumentParser(description="Database Backup and Download Utility")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--server", action="store_true", help="Run in server mode (backup and serve)")
    group.add_argument("--download", nargs=2, metavar=('URL', 'OUTPUT_FILE'), 
                       help="Run in download mode (download from server)")
    parser.add_argument("--timeout", type=int, default=600, 
                       help="Timeout in seconds (default: 600)")
    
    args = parser.parse_args()
    
    if args.server:
        return server_mode()
    elif args.download:
        url, output_file = args.download
        return download_mode(url, output_file, args.timeout)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
