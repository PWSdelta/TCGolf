import http.client
import sys
import os
import time

def download_chunked(host, path, output_file, timeout=300, chunk_size=8192):
    """
    Download a file using chunked download with timeout and resume capability
    
    Args:
        host (str): Host name (without http://)
        path (str): Path to file on server
        output_file (str): Local file to save to
        timeout (int): Connection timeout in seconds
        chunk_size (int): Size of chunks to request
    """
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
            while True:
                # Create a new connection for each chunk (helps with timeouts)
                conn = http.client.HTTPConnection(host, timeout=timeout)
                
                # Set range header to request next chunk
                headers = {}
                if resume_from > 0:
                    headers['Range'] = f'bytes={resume_from}-{resume_from + chunk_size - 1}'
                
                try:
                    print(f"\rRequesting bytes {resume_from}-{resume_from + chunk_size - 1}", end="", flush=True)
                    conn.request("GET", path, headers=headers)
                    response = conn.getresponse()
                    
                    # If we get a 200 or 206 (partial content) response
                    if response.status in [200, 206]:
                        # Get the file size if available
                        if 'content-length' in response.headers:
                            chunk_length = int(response.headers['content-length'])
                        else:
                            chunk_length = chunk_size
                            
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
                        print(f"\rDownloaded: {total_size / (1024*1024):.2f} MB in {elapsed:.1f}s", end="", flush=True)
                        
                        # If we got less data than requested, we're done
                        if chunk_actual_size < chunk_size:
                            print("\nDownload complete (received less data than requested)")
                            break
                    else:
                        print(f"\nServer returned error: {response.status} {response.reason}")
                        if response.status == 416:  # Range Not Satisfiable - file fully downloaded
                            print("Download appears to be complete (server says requested range is invalid)")
                            break
                        else:
                            return False
                            
                except (http.client.HTTPException, ConnectionError, TimeoutError) as e:
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
        print(f"Total size: {total_size / (1024*1024):.2f} MB")
        print(f"Time elapsed: {time.time() - start_time:.1f} seconds")
        return True
        
    except Exception as e:
        print(f"\nDownload failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python download_db_chunked.py <host> <path> <output_file> [timeout_seconds]")
        print("Example: python download_db_chunked.py 159.223.94.36:8000 /db.sqlite3 ./db_production.sqlite3 600")
        sys.exit(1)
    
    host = sys.argv[1]
    path = sys.argv[2]
    output_file = sys.argv[3]
    timeout = 300  # Default: 5 minutes
    
    if len(sys.argv) >= 5:
        try:
            timeout = int(sys.argv[4])
        except ValueError:
            print(f"Invalid timeout value: {sys.argv[4]}. Using default: 300 seconds.")
    
    success = download_chunked(host, path, output_file, timeout)
    sys.exit(0 if success else 1)
