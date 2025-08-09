from python import Python
from python.object import PythonObject

struct Route:
    var path: String
    var content: String
    
    fn __init__(inout self, path: String, content: String):
        self.path = path
        self.content = content

fn web_router_map_kernel(routes: PythonObject, request_path: String) -> String:
    """
    Map route -> content (simple dictionary)
    
    Args:
        routes: Dictionary of route mappings
        request_path: Requested path
        
    Returns:
        Content for matching route or 404 message
    """
    let py = Python.import_module("builtins")
    
    # Normalize the request path
    var normalized_path = request_path
    if not normalized_path.startswith("/"):
        normalized_path = "/" + normalized_path
    
    # Remove trailing slashes except for root
    if len(normalized_path) > 1 and normalized_path.endswith("/"):
        normalized_path = normalized_path[:-1]
    
    # Check if exact match exists
    if normalized_path in routes:
        return String(routes[normalized_path])
    
    # Check for wildcard routes (simple implementation)
    # Check if there's a catch-all route
    if "*" in routes:
        return String(routes["*"])
    
    # Return 404 message
    return "<h1>404 Not Found</h1><p>The requested path '" + request_path + "' was not found.</p>"

fn main():
    let py = Python.import_module("builtins")
    
    # Create a dictionary of routes using Python dict
    let routes = py.dict()
    routes["/"] = "<h1>Welcome</h1><p>This is the home page.</p>"
    routes["/about"] = "<h1>About Us</h1><p>Learn more about our project.</p>"
    routes["/contact"] = "<h1>Contact</h1><p>Get in touch with us.</p>"
    routes["*"] = "<h1>Custom 404</h1><p>This page doesn't exist yet.</p>"
    
    # Test various paths
    print("Testing router:")
    print("Path: / ->", web_router_map_kernel(routes, "/"))
    print("\nPath: /about ->", web_router_map_kernel(routes, "/about"))
    print("\nPath: /missing ->", web_router_map_kernel(routes, "/missing"))
    print("\nPath: contact (no slash) ->", web_router_map_kernel(routes, "contact"))