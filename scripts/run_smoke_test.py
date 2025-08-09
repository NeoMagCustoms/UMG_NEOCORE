#!/usr/bin/env python3
"""
Run MAX serve and smoke test
"""

import subprocess
import time
import sys
from pathlib import Path

def main():
    project_root = Path(__file__).parent.parent
    
    # Start the server in background
    print("Starting MAX serve...")
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "neo_umg.max_serve"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(2)
    
    try:
        # Run smoke tests
        print("\nRunning smoke tests...")
        test_result = subprocess.run(
            [sys.executable, "tests/test_openai_api.py"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        print(test_result.stdout)
        if test_result.stderr:
            print("STDERR:", test_result.stderr)
        
        return test_result.returncode
        
    finally:
        # Stop the server
        print("\nStopping server...")
        server_proc.terminate()
        server_proc.wait(timeout=5)

if __name__ == "__main__":
    exit(main())