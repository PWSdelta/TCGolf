import os
import sys
import shutil
import http.server
import socketserver
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Simple HTTP server for downloading the SQLite database")
    parser.add_argument('--db-path', type=str, default='/path/to/db.sqlite3',
                        help='Path to the SQLite database file')
    parser.add_argument('--port', type=int, default=8000, 
                        help='Port to run the HTTP server on')
    parser.add_argument('--backup', action='store_true',
                        help='Create a backup of the database before serving')
    args = parser.parse_args()
    
    db_path = Path(args.db_path)
    
    if not db_path.exists():
        print(f"Error: Database file not found at {db_path}", file=sys.stderr)
        return 1
    
    # Create a temporary directory to serve files from
    temp_dir = Path("./temp_download")
    temp_dir.mkdir(exist_ok=True)
    
    # If backup requested, create one using SQLite's backup command
    if args.backup:
        backup_path = temp_dir / "db_backup.sqlite3"
        print(f"Creating backup at {backup_path}...")
        os.system(f"sqlite3 {db_path} '.backup {backup_path}'")
        serve_file = backup_path
        print(f"Backup created successfully!")
    else:
        # Copy the database to the temp directory to avoid serving the live DB directly
        serve_file = temp_dir / db_path.name
        print(f"Copying database to {serve_file}...")
        shutil.copy2(db_path, serve_file)
        print("Copy completed!")
    
    # Change to the temp directory
    os.chdir(temp_dir)
    
    # Set up the HTTP server
    handler = http.server.SimpleHTTPRequestHandler
    port = args.port
    
    # Try to start the server
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"\n--- SERVER RUNNING ---")
            print(f"Your database is available at: http://YOUR_SERVER_IP:{port}/{serve_file.name}")
            print(f"Access this URL from your local browser to download the file.")
            print("Press Ctrl+C to stop the server when done.")
            print(f"SECURITY WARNING: Anyone who knows this URL can download your database.")
            print("Remember to delete the temporary files when finished!")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        return 1
    
    print("\nRemember to delete the temporary directory when you're done!")
    print(f"Run: rm -rf {temp_dir}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
