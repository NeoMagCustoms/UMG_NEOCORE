#!/usr/bin/env python3
"""
Generator: CSV → Mojo Kernel Files
Reads baseline_kernels.csv and generates Mojo stub files
"""

import csv
import os
from pathlib import Path
from textwrap import dedent

def sanitize_name(name):
    """Convert dot-notation to safe file/function names"""
    # web.html.tag.div -> web_html_tag_div
    return name.replace('.', '_')

def get_module_path(name):
    """Convert dot-notation to directory structure"""
    # web.html.tag.div -> web/html/tag/div.mojo
    parts = name.split('.')
    if len(parts) > 1:
        dir_path = '/'.join(parts[:-1])
        file_name = parts[-1] + '.mojo'
        return dir_path, file_name
    return '', name + '.mojo'

def generate_kernel_code(name, description):
    """Generate Mojo kernel stub code"""
    safe_name = sanitize_name(name)
    
    # Determine kernel type from name
    if 'tag' in name:
        # HTML tag kernels
        tag_name = name.split('.')[-1]
        return dedent(f'''
        from python import Python
        
        fn {safe_name}_kernel(attributes: String, children: String) -> String:
            """
            {description}
            
            Args:
                attributes: HTML attributes as string
                children: Inner HTML content
                
            Returns:
                Rendered HTML string
            """
            var result = String("<{tag_name}")
            if len(attributes) > 0:
                result += " " + attributes
            result += ">"
            result += children
            result += "</{tag_name}>"
            return result
        
        fn main():
            # Example usage
            let attrs = "class='container' id='main'"
            let content = "Hello, World!"
            let html = {safe_name}_kernel(attrs, content)
            print(html)
        ''').strip()
    
    elif 'markdown' in name:
        # Markdown parser kernel
        return dedent(f'''
        from python import Python
        
        fn {safe_name}_kernel(markdown_text: String) -> String:
            """
            {description}
            
            Args:
                markdown_text: Markdown formatted text
                
            Returns:
                HTML string
            """
            # TODO: Implement markdown parsing
            # For now, return a placeholder
            return "<div class='markdown'>" + markdown_text + "</div>"
        
        fn main():
            let md = "# Hello World\\n\\nThis is **bold** text."
            let html = {safe_name}_kernel(md)
            print(html)
        ''').strip()
    
    elif 'readfile' in name:
        # File reading kernel
        return dedent(f'''
        from python import Python
        
        fn {safe_name}_kernel(file_path: String) -> String:
            """
            {description}
            
            Args:
                file_path: Path to file to read
                
            Returns:
                File contents as UTF-8 string
            """
            # TODO: Implement file reading with proper error handling
            # For now, return a placeholder
            return "File contents: " + file_path
        
        fn main():
            let content = {safe_name}_kernel("test.txt")
            print(content)
        ''').strip()
    
    elif 'writefile' in name:
        # File writing kernel
        return dedent(f'''
        from python import Python
        
        fn {safe_name}_kernel(file_path: String, content: String) -> Bool:
            """
            {description}
            
            Args:
                file_path: Path to file to write
                content: Content to write
                
            Returns:
                True if successful, False otherwise
            """
            # TODO: Implement file writing with directory creation
            # For now, return success
            print("Would write to: " + file_path)
            return True
        
        fn main():
            let success = {safe_name}_kernel("output.txt", "Hello, World!")
            if success:
                print("Write successful")
            else:
                print("Write failed")
        ''').strip()
    
    elif 'router' in name:
        # Router kernel
        return dedent(f'''
        from python import Python
        
        struct Route:
            var path: String
            var content: String
            
            fn __init__(inout self, path: String, content: String):
                self.path = path
                self.content = content
        
        fn {safe_name}_kernel(routes: DynamicVector[Route], request_path: String) -> String:
            """
            {description}
            
            Args:
                routes: List of route mappings
                request_path: Requested path
                
            Returns:
                Content for matching route or 404 message
            """
            # TODO: Implement route matching logic
            # For now, return placeholder
            return "Content for path: " + request_path
        
        fn main():
            var routes = DynamicVector[Route]()
            routes.append(Route("/", "Home page"))
            routes.append(Route("/about", "About page"))
            
            let content = {safe_name}_kernel(routes, "/about")
            print(content)
        ''').strip()
    
    else:
        # Generic kernel template
        return dedent(f'''
        from python import Python
        
        fn {safe_name}_kernel(input: String) -> String:
            """
            {description}
            
            Args:
                input: Input data
                
            Returns:
                Processed output
            """
            # TODO: Implement kernel logic
            return "Processed: " + input
        
        fn main():
            let result = {safe_name}_kernel("test input")
            print(result)
        ''').strip()

def main():
    # Paths
    project_root = Path(__file__).parent.parent.parent
    csv_path = project_root / 'docs' / 'baseline_kernels.csv'
    src_dir = project_root / 'src' / 'kernels'
    
    # Create src/kernels directory if it doesn't exist
    src_dir.mkdir(parents=True, exist_ok=True)
    
    # Read CSV and generate kernels
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        generated_files = []
        
        for row in reader:
            name = row['name']
            description = row['description']
            
            # Get module path
            dir_path, file_name = get_module_path(name)
            
            # Create directory structure
            if dir_path:
                full_dir = src_dir / dir_path
                full_dir.mkdir(parents=True, exist_ok=True)
            else:
                full_dir = src_dir
            
            # Generate kernel code
            code = generate_kernel_code(name, description)
            
            # Write file
            file_path = full_dir / file_name
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            generated_files.append(str(file_path.relative_to(project_root)))
            print(f"Generated: {file_path.relative_to(project_root)}")
    
    # Create __init__.mojo files for each directory
    for root, dirs, files in os.walk(src_dir):
        if any(f.endswith('.mojo') for f in files):
            init_path = Path(root) / '__init__.mojo'
            if not init_path.exists():
                with open(init_path, 'w', encoding='utf-8') as f:
                    f.write('# Package initialization\n')
                print(f"Created: {init_path.relative_to(project_root)}")
    
    print(f"\nSuccessfully generated {len(generated_files)} kernel files!")
    print("\nNext steps:")
    print("1. Review generated Mojo files in src/kernels/")
    print("2. Implement TODO sections with actual logic")
    print("3. Run 'mojo build' to compile kernels")

if __name__ == '__main__':
    main()