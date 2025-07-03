import urllib.request
import socket
import sys
import os
from urllib.error import URLError
import time

def download_file(url, output_filename, timeout=300, chunk_size=8192):
    """
    Download a file from URL with specified timeout
    
    Args:
        url (str): URL to download from
        output_filename (str): Local filename to save to
        timeout (int): Timeout in seconds (default: 300 seconds / 5 minutes)
        chunk_size (int): Size of chunks to download (default: 8KB)
    """
    temp_filename = output_filename + '.part'
    
    # Set socket timeout for the entire session
    socket.setdefaulttimeout(timeout)
    
    start_time = time.time()
    total_size = 0
    
    try:
        print(f"Downloading {url}")
        print(f"Timeout set to {timeout} seconds")
        
        with urllib.request.urlopen(url) as response:
            file_size = int(response.info().get('Content-Length', 0))
            if file_size > 0:
                print(f"Total file size: {file_size / (1024*1024):.2f} MB")
            
            with open(temp_filename, 'wb') as out_file:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    total_size += len(chunk)
                    
                    # Print progress
                    elapsed = time.time() - start_time
                    if file_size > 0:
                        percent = total_size * 100 / file_size
                        print(f"\rProgress: {percent:.1f}% - {total_size / (1024*1024):.2f} MB - {elapsed:.1f}s", end="", flush=True)
                    else:
                        print(f"\rDownloaded: {total_size / (1024*1024):.2f} MB - {elapsed:.1f}s", end="", flush=True)
        
        # Rename the temp file to the final filename
        if os.path.exists(output_filename):
            os.remove(output_filename)
        os.rename(temp_filename, output_filename)
        
        print(f"\nDownload complete: {output_filename}")
        print(f"Total size: {total_size / (1024*1024):.2f} MB")
        print(f"Time elapsed: {time.time() - start_time:.1f} seconds")
        return True
    
    except URLError as e:
        print(f"\nDownload failed: {e}")
        if hasattr(e, 'reason'):
            print(f"Reason: {e.reason}")
        return False
    except Exception as e:
        print(f"\nDownload failed: {e}")
        return False
    finally:
        # Clean up temp file if it exists
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except:
                pass

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python download_with_timeout.py <url> <output_filename> [timeout_seconds]")
        sys.exit(1)
    
    url = sys.argv[1]
    output_filename = sys.argv[2]
    timeout = 300  # Default: 5 minutes
    
    if len(sys.argv) >= 4:
        try:
            timeout = int(sys.argv[3])
        except ValueError:
            print(f"Invalid timeout value: {sys.argv[3]}. Using default: 300 seconds.")
    
    success = download_file(url, output_filename, timeout)
    sys.exit(0 if success else 1)
