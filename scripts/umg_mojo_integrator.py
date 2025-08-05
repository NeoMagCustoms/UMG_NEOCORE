import json
import pathlib
import re
from typing import Dict, List, Optional, Any
import textwrap

class UMGMojoIntegrator:
    """Integrates Mojo implementations with UMG block JSON structure"""
    
    def __init__(self, umg_neocore_path: str, website_builder_path: str):
        self.umg_root = pathlib.Path(umg_neocore_path)
        self.wb_root = pathlib.Path(website_builder_path)
        self.kernels_dir = self.umg_root / "neocore" / "src" / "kernels"
        
        # Load UMG block templates from WEBSITE BUILDER
        self.block_templates = self._load_block_templates()
        
    def _load_block_templates(self) -> Dict[str, Any]:
        """Load all block JSON templates from WEBSITE BUILDER"""
        templates = {}
        
        # Load from extracted directories
        extracted_dir = self.wb_root / "extracted_analytics"
        if extracted_dir.exists():
            for json_file in extracted_dir.glob("*.json"):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    block_id = data.get('block_id', '')
                    templates[block_id] = data
                    
        # Also try to load from the main JSON files
        json_files = [
            "analytics_blocks_jsons.json",
            "auth_blocks_jsons.json",
            "deploy_blocks_jsons.json",
            "i18n_blocks_jsons.json",
            "math_blocks_jsons.json",
            "notification_blocks_jsons.json",
            "payments_blocks_jsons.json",
            "pwa_blocks_jsons.json",
            "security_blocks_jsons.json",
            "seo_blocks_jsons.json",
            "state_blocks_jsons.json",
            "testing_blocks_jsons.json"
        ]
        
        for json_file in json_files:
            file_path = self.wb_root / json_file
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    templates.update(data)
                    
        return templates
    
    def generate_mojo_kernel(self, block_name: str, block_template: Dict) -> str:
        """Generate Mojo kernel code based on block template and type"""
        
        parts = block_name.split('.')
        if len(parts) < 3:
            return None
            
        domain, subdomain, action = parts[:3]
        
        # Get metadata from template
        molt_type = block_template.get('molt_type', 'Instruction')
        category = block_template.get('category', subdomain)
        cantocore = block_template.get('cantocore', '')
        
        # Parse cantocore for operation hints
        operation = self._parse_cantocore(cantocore)
        
        # Generate struct name
        struct_name = ''.join(word.capitalize() for word in action.split('_'))
        
        # Generate implementation based on molt_type and operation
        implementation = self._generate_implementation(
            domain, subdomain, action, molt_type, operation
        )
        
        # Build complete kernel
        kernel = f'''
from memory import memset_zero, memcpy
from python import Python
from utils.variant import Variant

@compiler.register("{block_name}")
struct {struct_name}:
    """
    {block_template.get('description', 'No description')}
    Category: {category}
    Type: {molt_type}
    """
    
    var config: Dict[String, Variant]
    var state: Dict[String, Variant]
    
    fn __init__(inout self):
        self.config = Dict[String, Variant]()
        self.state = Dict[String, Variant]()
    
    @staticmethod
    fn execute(inout self, input: Variant) -> Variant:
        """Execute the {action} operation"""
        {implementation}
        
    fn configure(inout self, config: Dict[String, Variant]):
        """Configure the block with given parameters"""
        self.config = config
        
    fn get_state(self) -> Dict[String, Variant]:
        """Get current block state"""
        return self.state
'''
        
        return kernel.strip()
    
    def _parse_cantocore(self, cantocore: str) -> str:
        """Parse cantocore notation to extract operation type"""
        # Example: "INSTRUCTION:GA[EVENT]" -> "EVENT"
        match = re.search(r'\[(.+?)\]', cantocore)
        if match:
            return match.group(1)
        return ""
    
    def _generate_implementation(self, domain: str, subdomain: str, action: str, 
                                molt_type: str, operation: str) -> str:
        """Generate implementation based on domain, action, and molt type"""
        
        # Analytics implementations
        if domain == "analytics":
            if action == "track" or operation == "EVENT":
                return '''
        # Analytics event tracking
        try:
            let event_name = input.get_string("event")
            let properties = input.get_dict("properties")
            
            # Send to analytics service
            let analytics = Python.import_module("analytics")
            analytics.track(event_name, properties)
            
            # Update state
            self.state["last_event"] = Variant(event_name)
            self.state["event_count"] = Variant(self.state.get("event_count", 0) + 1)
            
            return Variant(True)
        except:
            return Variant(False)'''
            
            elif action == "pageview":
                return '''
        # Track page view
        try:
            let page_url = input.get_string("url")
            let page_title = input.get_string("title", "")
            
            # Send pageview event
            let analytics = Python.import_module("analytics")
            analytics.page(page_url, {"title": page_title})
            
            return Variant(True)
        except:
            return Variant(False)'''
        
        # Auth implementations
        elif domain == "auth":
            if action == "login":
                return '''
        # Handle user login
        try:
            let username = input.get_string("username")
            let password = input.get_string("password")
            
            # Hash password
            let hasher = Python.import_module("hashlib")
            let hashed = hasher.sha256(password.encode()).hexdigest()
            
            # Verify credentials (simplified)
            if self._verify_credentials(username, hashed):
                # Create session
                let session_id = self._generate_session_id()
                self.state["session_id"] = Variant(session_id)
                self.state["user"] = Variant(username)
                
                return Variant({"success": True, "session_id": session_id})
            else:
                return Variant({"success": False, "error": "Invalid credentials"})
        except e:
            return Variant({"success": False, "error": str(e)})'''
            
            elif action == "verify":
                return '''
        # Verify authentication
        try:
            let token = input.get_string("token")
            
            # Verify JWT token
            let jwt = Python.import_module("jwt")
            let payload = jwt.decode(token, self.config.get("secret"), algorithms=["HS256"])
            
            return Variant({"valid": True, "payload": payload})
        except:
            return Variant({"valid": False})'''
        
        # Component implementations
        elif domain == "component":
            if subdomain == "modal":
                if action == "open":
                    return '''
        # Open modal component
        let modal_id = input.get_string("id", "modal")
        let content = input.get_string("content", "")
        
        # Set modal state
        self.state["open"] = Variant(True)
        self.state["content"] = Variant(content)
        self.state["id"] = Variant(modal_id)
        
        # Return render data
        return Variant({
            "html": self._render_modal(modal_id, content),
            "open": True
        })'''
                elif action == "close":
                    return '''
        # Close modal component
        self.state["open"] = Variant(False)
        self.state["content"] = Variant("")
        
        return Variant({"open": False})'''
        
        # Cache implementations
        elif domain == "cache":
            if action == "get":
                return '''
        # Get from cache
        let key = input.get_string("key")
        
        if key in self.state:
            let entry = self.state[key]
            # Check if expired
            let expiry = entry.get_int("expiry", 0)
            let now = self._get_timestamp()
            
            if expiry == 0 or now < expiry:
                return entry.get("value")
                
        return Variant(None)'''
            
            elif action == "set":
                return '''
        # Set cache value
        let key = input.get_string("key")
        let value = input.get("value")
        let ttl = input.get_int("ttl", 0)
        
        let expiry = 0
        if ttl > 0:
            expiry = self._get_timestamp() + ttl
            
        self.state[key] = Variant({
            "value": value,
            "expiry": expiry
        })
        
        return Variant(True)'''
        
        # Default implementation
        else:
            return '''
        # Default implementation
        # TODO: Implement {action} for {domain}.{subdomain}
        return Variant(None)'''.format(action=action, domain=domain, subdomain=subdomain)
    
    def update_kernel_with_umg_structure(self, block_name: str) -> bool:
        """Update a kernel file with UMG structure and Mojo implementation"""
        
        # Find the kernel file
        parts = block_name.split('.')
        if len(parts) < 3:
            return False
            
        domain, subdomain, action = parts[:3]
        kernel_path = self.kernels_dir / domain / subdomain / f"{action}.mojo"
        
        if not kernel_path.exists():
            print(f"Kernel file not found: {kernel_path}")
            return False
        
        # Get template if available
        template = self.block_templates.get(block_name, {})
        if not template:
            # Create minimal template
            template = {
                'block_id': block_name,
                'molt_type': 'Instruction',
                'category': subdomain,
                'description': f"Implements {action} for {subdomain}"
            }
        
        # Generate new kernel
        new_kernel = self.generate_mojo_kernel(block_name, template)
        
        # Write the updated kernel
        kernel_path.write_text(new_kernel)
        print(f"Updated: {kernel_path}")
        
        # Also save the UMG metadata
        metadata_path = kernel_path.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(template, f, indent=2)
            
        return True
    
    def batch_update_domain(self, domain: str, dry_run: bool = True):
        """Update all kernels in a domain"""
        domain_dir = self.kernels_dir / domain
        if not domain_dir.exists():
            print(f"Domain directory not found: {domain_dir}")
            return
            
        updated = 0
        for kernel_file in domain_dir.rglob("*.mojo"):
            # Extract block name from file path
            relative_path = kernel_file.relative_to(self.kernels_dir)
            parts = list(relative_path.parts)
            parts[-1] = parts[-1].replace('.mojo', '')
            block_name = '.'.join(parts)
            
            if dry_run:
                print(f"Would update: {block_name}")
            else:
                if self.update_kernel_with_umg_structure(block_name):
                    updated += 1
                    
        print(f"\nTotal updated: {updated}")
        
    def create_mojo_examples_reference(self):
        """Create a reference file with Mojo code examples"""
        examples = '''
# Mojo Language Examples Reference

## Basic Types and Variables
```mojo
let immutable_value: Int = 42
var mutable_value: String = "Hello"
let float_val: Float64 = 3.14159
let bool_val: Bool = True
```

## Functions
```mojo
fn add(x: Int, y: Int) -> Int:
    return x + y

fn greet(name: String) -> String:
    return "Hello, " + name + "!"
    
# Generic function
fn swap[T](inout a: T, inout b: T):
    let temp = a
    a = b
    b = temp
```

## Structs
```mojo
struct Point:
    var x: Float64
    var y: Float64
    
    fn __init__(inout self, x: Float64, y: Float64):
        self.x = x
        self.y = y
        
    fn distance(self, other: Point) -> Float64:
        let dx = self.x - other.x
        let dy = self.y - other.y
        return sqrt(dx * dx + dy * dy)
```

## Collections
```mojo
# Dynamic Vector
var vec = DynamicVector[Int]()
vec.append(1)
vec.append(2)
vec.append(3)

# Dictionary
var dict = Dict[String, Int]()
dict["one"] = 1
dict["two"] = 2

# Iteration
for i in range(len(vec)):
    print(vec[i])
```

## Error Handling
```mojo
fn divide(a: Float64, b: Float64) raises -> Float64:
    if b == 0:
        raise Error("Division by zero")
    return a / b

try:
    let result = divide(10, 0)
except e:
    print("Error:", e)
```

## Memory Management
```mojo
# Manual memory allocation
let ptr = Pointer[Int].alloc(10)
for i in range(10):
    ptr.store(i, i * i)
    
# Don't forget to free
ptr.free()

# RAII pattern with structs
struct Buffer:
    var data: Pointer[UInt8]
    var size: Int
    
    fn __init__(inout self, size: Int):
        self.data = Pointer[UInt8].alloc(size)
        self.size = size
        
    fn __del__(owned self):
        self.data.free()
```

## SIMD Operations
```mojo
from math import sqrt
from algorithm import vectorize

fn euclidean_distance(x: DynamicVector[Float32], y: DynamicVector[Float32]) -> Float32:
    var sum: Float32 = 0.0
    
    @parameter
    fn vector_dist[simd_width: Int](idx: Int):
        let diff = x.load[width=simd_width](idx) - y.load[width=simd_width](idx)
        sum += (diff * diff).reduce_add()
        
    vectorize[vector_dist, 16](len(x))
    return sqrt(sum)
```

## Python Interop
```mojo
from python import Python

fn use_numpy():
    let np = Python.import_module("numpy")
    let array = np.array([1, 2, 3, 4, 5])
    let mean = np.mean(array)
    print("Mean:", mean)
    
fn use_requests():
    let requests = Python.import_module("requests")
    let response = requests.get("https://api.example.com/data")
    let data = response.json()
    return data
```

## Async/Parallel
```mojo
from algorithm import parallelize

fn parallel_compute(data: DynamicVector[Float64]) -> Float64:
    var results = DynamicVector[Float64](len(data))
    
    @parameter
    fn compute_chunk(idx: Int):
        results[idx] = expensive_computation(data[idx])
        
    parallelize[compute_chunk](len(data))
    
    # Reduce results
    var total = 0.0
    for r in results:
        total += r
    return total
```

## Pattern Matching (Future)
```mojo
# Note: Pattern matching syntax may evolve
fn process_value(val: Variant) -> String:
    match val:
        case Int(x):
            return "Integer: " + str(x)
        case String(s):
            return "String: " + s
        case Float64(f):
            return "Float: " + str(f)
        case _:
            return "Unknown type"
```
'''
        
        ref_path = self.umg_root / "docs" / "mojo_examples_reference.md"
        ref_path.parent.mkdir(exist_ok=True)
        ref_path.write_text(examples)
        print(f"Created Mojo examples reference at: {ref_path}")

def main():
    # Initialize integrator
    integrator = UMGMojoIntegrator(
        "C:\\Users\\Magne\\OneDrive\\Desktop\\UMG_NEOCORE",
        "C:\\WEBSITE BUILDER"
    )
    
    # Create reference documentation
    integrator.create_mojo_examples_reference()
    
    # Example: Update specific blocks
    example_blocks = [
        "analytics.event.track",
        "auth.session.login",
        "cache.memory.get",
        "component.modal.open"
    ]
    
    print("\nUpdating example blocks with UMG structure and Mojo implementations:")
    for block in example_blocks:
        integrator.update_kernel_with_umg_structure(block)
    
    print("\nTo batch update entire domains, use:")
    print('integrator.batch_update_domain("analytics", dry_run=False)')

if __name__ == "__main__":
    main()