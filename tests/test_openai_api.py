#!/usr/bin/env python3
"""
OpenAI-compatible API Smoke Test
Tests the MAX serve endpoints
"""

import json
import time
import requests
from typing import Dict, Any

class OpenAIAPITester:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
    
    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        print("\n1. Testing health check...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            data = response.json()
            print(f"   ✓ Server is {data['status']}")
            print(f"   ✓ Kernels loaded: {data['kernels_loaded']}")
            return True
        except Exception as e:
            print(f"   ✗ Health check failed: {e}")
            return False
    
    def test_list_models(self) -> bool:
        """Test model listing"""
        print("\n2. Testing model listing...")
        try:
            response = self.session.get(f"{self.base_url}/v1/models")
            response.raise_for_status()
            data = response.json()
            models = data.get("data", [])
            print(f"   ✓ Found {len(models)} models:")
            for model in models:
                print(f"     - {model['id']}")
            return True
        except Exception as e:
            print(f"   ✗ Model listing failed: {e}")
            return False
    
    def test_completion(self) -> bool:
        """Test completion endpoint"""
        print("\n3. Testing completion endpoint...")
        
        test_cases = [
            {
                "model": "web.html.tag.div",
                "prompt": "class='container'|Hello, World!",
                "expected_contains": "<div"
            },
            {
                "model": "text.parse.markdown",
                "prompt": "# Welcome\n\nThis is **bold** text.",
                "expected_contains": "<h1>"
            }
        ]
        
        all_passed = True
        for i, test in enumerate(test_cases):
            try:
                payload = {
                    "model": test["model"],
                    "prompt": test["prompt"],
                    "max_tokens": 100,
                    "temperature": 0
                }
                
                response = self.session.post(
                    f"{self.base_url}/v1/completions",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                result = data["choices"][0]["text"]
                if test["expected_contains"] in result:
                    print(f"   ✓ Test {i+1} passed: {test['model']}")
                    print(f"     Input: {test['prompt'][:50]}...")
                    print(f"     Output: {result[:50]}...")
                else:
                    print(f"   ✗ Test {i+1} failed: expected '{test['expected_contains']}' in output")
                    all_passed = False
                    
            except Exception as e:
                print(f"   ✗ Test {i+1} failed: {e}")
                all_passed = False
        
        return all_passed
    
    def test_chat_completion(self) -> bool:
        """Test chat completion endpoint"""
        print("\n4. Testing chat completion endpoint...")
        
        try:
            payload = {
                "model": "web.router.map",
                "messages": [
                    {"role": "system", "content": "You are a router kernel."},
                    {"role": "user", "content": "/about"}
                ],
                "temperature": 0
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            result = data["choices"][0]["message"]["content"]
            print(f"   ✓ Chat completion successful")
            print(f"     User: /about")
            print(f"     Assistant: {result}")
            return True
            
        except Exception as e:
            print(f"   ✗ Chat completion failed: {e}")
            return False
    
    def test_kernel_execution(self) -> bool:
        """Test direct kernel execution"""
        print("\n5. Testing direct kernel execution...")
        
        test_cases = [
            {
                "kernel": "web.html.tag.span",
                "args": {
                    "attributes": "style='color: red;'",
                    "children": "Important!"
                }
            },
            {
                "kernel": "web.router.map",
                "args": {
                    "routes": {"/": "Home Page", "/contact": "Contact Us"},
                    "path": "/contact"
                }
            }
        ]
        
        all_passed = True
        for i, test in enumerate(test_cases):
            try:
                response = self.session.post(
                    f"{self.base_url}/v1/kernels/execute",
                    json=test
                )
                response.raise_for_status()
                data = response.json()
                
                print(f"   ✓ Kernel {test['kernel']} executed successfully")
                print(f"     Result: {data['result']}")
                
            except Exception as e:
                print(f"   ✗ Kernel execution failed: {e}")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self) -> bool:
        """Run all smoke tests"""
        print("=" * 60)
        print("OpenAI-Compatible API Smoke Test")
        print("=" * 60)
        
        # Wait for server to be ready
        print("Checking server availability...")
        for i in range(5):
            try:
                self.session.get(f"{self.base_url}/health", timeout=1)
                break
            except:
                if i == 4:
                    print("✗ Server not reachable. Is MAX serve running?")
                    print(f"  Try: python -m neo_umg.max_serve")
                    return False
                time.sleep(1)
        
        # Run tests
        tests = [
            self.test_health_check,
            self.test_list_models,
            self.test_completion,
            self.test_chat_completion,
            self.test_kernel_execution
        ]
        
        results = [test() for test in tests]
        
        # Summary
        print("\n" + "=" * 60)
        passed = sum(results)
        total = len(results)
        
        if passed == total:
            print(f"✓ All tests passed! ({passed}/{total})")
        else:
            print(f"✗ Some tests failed: {passed}/{total} passed")
        
        return passed == total

def main():
    """Run smoke tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test OpenAI-compatible API")
    parser.add_argument("--url", default="http://localhost:8080", help="Base URL of MAX serve")
    
    args = parser.parse_args()
    
    tester = OpenAIAPITester(args.url)
    success = tester.run_all_tests()
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()