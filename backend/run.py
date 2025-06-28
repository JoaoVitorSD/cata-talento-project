import os
import subprocess
import sys

from dotenv import load_dotenv


def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get configuration from environment with defaults
    host = os.getenv('HOST', '0.0.0.0')
    port = os.getenv('PORT', '8000')
    reload = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Construct the uvicorn command
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', host,
        '--port', port
    ]
    
    if reload:
        cmd.append('--reload')
    
    # Run uvicorn with the specified configuration
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)

if __name__ == '__main__':
    main() 