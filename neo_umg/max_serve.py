#!/usr/bin/env python3
"""
MAX Serve + OpenAI-compatible API
Serves Mojo kernels via HTTP with OpenAI-compatible endpoints
"""

import json
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class OpenAICompatibleHandler(BaseHTTPRequestHandler):
    """HTTP handler with OpenAI-compatible endpoints"""
    
    def __init__(self, *args, kernels: Dict[str, Any], **kwargs):
        self.kernels = kernels
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == "/v1/models":
            self.handle_list_models()
        elif parsed_path.path == "/health":
            self.handle_health_check()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == "/v1/completions":
            self.handle_completion()
        elif parsed_path.path == "/v1/chat/completions":
            self.handle_chat_completion()
        elif parsed_path.path == "/v1/kernels/execute":
            self.handle_kernel_execution()
        else:
            self.send_error(404, "Not Found")
    
    def handle_list_models(self):
        """List available models/kernels"""
        models = [
            {
                "id": kernel_name,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "umg-neocore",
                "permission": [],
                "root": kernel_name,
                "parent": None
            }
            for kernel_name in self.kernels.keys()
        ]
        
        response = {
            "object": "list",
            "data": models
        }
        
        self.send_json_response(response)
    
    def handle_health_check(self):
        """Health check endpoint"""
        response = {
            "status": "healthy",
            "timestamp": int(time.time()),
            "kernels_loaded": len(self.kernels)
        }
        self.send_json_response(response)
    
    def handle_completion(self):
        """Handle completion requests (OpenAI-compatible)"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            request = json.loads(body)
            model = request.get("model", "web.html.tag.div")
            prompt = request.get("prompt", "")
            
            # Execute kernel based on model name
            if model in self.kernels:
                result = self.execute_kernel(model, prompt)
                
                response = {
                    "id": f"cmpl-{uuid.uuid4().hex[:8]}",
                    "object": "text_completion",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [{
                        "text": result,
                        "index": 0,
                        "logprobs": None,
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": len(prompt.split()),
                        "completion_tokens": len(result.split()),
                        "total_tokens": len(prompt.split()) + len(result.split())
                    }
                }
                
                self.send_json_response(response)
            else:
                self.send_error(400, f"Model '{model}' not found")
                
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_chat_completion(self):
        """Handle chat completion requests (OpenAI-compatible)"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            request = json.loads(body)
            model = request.get("model", "web.router.map")
            messages = request.get("messages", [])
            
            # Extract the last user message as input
            user_input = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_input = msg.get("content", "")
                    break
            
            # Execute kernel
            if model in self.kernels:
                result = self.execute_kernel(model, user_input)
                
                response = {
                    "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": result
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": sum(len(m.get("content", "").split()) for m in messages),
                        "completion_tokens": len(result.split()),
                        "total_tokens": sum(len(m.get("content", "").split()) for m in messages) + len(result.split())
                    }
                }
                
                self.send_json_response(response)
            else:
                self.send_error(400, f"Model '{model}' not found")
                
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_kernel_execution(self):
        """Direct kernel execution endpoint"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            request = json.loads(body)
            kernel = request.get("kernel")
            args = request.get("args", {})
            
            if kernel in self.kernels:
                result = self.kernels[kernel](**args)
                
                response = {
                    "kernel": kernel,
                    "result": result,
                    "timestamp": int(time.time())
                }
                
                self.send_json_response(response)
            else:
                self.send_error(400, f"Kernel '{kernel}' not found")
                
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            self.send_error(500, str(e))
    
    def execute_kernel(self, kernel_name: str, input_data: str) -> str:
        """Execute a kernel with input data"""
        kernel_func = self.kernels.get(kernel_name)
        if kernel_func:
            try:
                # Different kernels expect different inputs
                if "markdown" in kernel_name:
                    return kernel_func(input_data)
                elif "tag" in kernel_name:
                    # Parse attributes and content from input
                    parts = input_data.split("|", 1)
                    attrs = parts[0] if len(parts) > 0 else ""
                    content = parts[1] if len(parts) > 1 else ""
                    return kernel_func(attrs, content)
                elif "router" in kernel_name:
                    # Simple routing simulation
                    return kernel_func({"/": "Home", "/about": "About"}, input_data)
                else:
                    return kernel_func(input_data)
            except Exception as e:
                return f"Error executing kernel: {str(e)}"
        return f"Kernel '{kernel_name}' not found"
    
    def send_json_response(self, data: Dict[str, Any], status: int = 200):
        """Send JSON response"""
        response_body = json.dumps(data, indent=2).encode('utf-8')
        
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response_body)))
        self.end_headers()
        
        self.wfile.write(response_body)

def create_mock_kernels() -> Dict[str, Any]:
    """Create mock kernel functions for testing"""
    
    def div_kernel(attributes: str, children: str) -> str:
        return f'<div {attributes}>{children}</div>'
    
    def span_kernel(attributes: str, children: str) -> str:
        return f'<span {attributes}>{children}</span>'
    
    def markdown_kernel(text: str) -> str:
        # Simple markdown to HTML
        html = text.replace("# ", "<h1>").replace("\n", "</h1>\n", 1)
        html = html.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
        return html
    
    def readfile_kernel(path: str) -> str:
        try:
            return Path(path).read_text()
        except:
            return f"Error reading file: {path}"
    
    def writefile_kernel(path: str, content: str) -> str:
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content)
            return "Success"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    def router_kernel(routes: Dict[str, str], path: str) -> str:
        return routes.get(path, f"404: {path} not found")
    
    return {
        "web.html.tag.div": div_kernel,
        "web.html.tag.span": span_kernel,
        "text.parse.markdown": markdown_kernel,
        "io.fs.readfile": readfile_kernel,
        "io.fs.writefile": writefile_kernel,
        "web.router.map": router_kernel
    }

def serve(host: str = "localhost", port: int = 8080):
    """Start the MAX serve server"""
    kernels = create_mock_kernels()
    
    # Create handler with kernels
    handler = lambda *args, **kwargs: OpenAICompatibleHandler(*args, kernels=kernels, **kwargs)
    
    server = HTTPServer((host, port), handler)
    print(f"MAX Serve running on http://{host}:{port}")
    print(f"Loaded {len(kernels)} kernels: {', '.join(kernels.keys())}")
    print("\nEndpoints:")
    print(f"  GET  http://{host}:{port}/v1/models")
    print(f"  GET  http://{host}:{port}/health")
    print(f"  POST http://{host}:{port}/v1/completions")
    print(f"  POST http://{host}:{port}/v1/chat/completions")
    print(f"  POST http://{host}:{port}/v1/kernels/execute")
    print("\nPress Ctrl+C to stop...")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MAX Serve - OpenAI-compatible API for Mojo kernels")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    
    args = parser.parse_args()
    serve(args.host, args.port)

if __name__ == "__main__":
    main()