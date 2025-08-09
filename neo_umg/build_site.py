#!/usr/bin/env python3
"""
Static Site Builder Orchestrator
Uses Mojo kernels to build a static website
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any

class StaticSiteBuilder:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.build_dir = project_root / "build"
        self.public_dir = project_root / "public"
        self.pages_dir = project_root / "pages"
        
    def clean_build(self):
        """Remove existing build directory"""
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(exist_ok=True)
        
    def copy_static_assets(self):
        """Copy static assets from public to build"""
        if self.public_dir.exists():
            for item in self.public_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, self.build_dir)
                elif item.is_dir():
                    shutil.copytree(item, self.build_dir / item.name)
                    
    def load_page_config(self) -> Dict[str, Any]:
        """Load page configuration"""
        config_path = self.project_root / "site.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            "title": "UMG NeoCore Site",
            "pages": [
                {"path": "/", "file": "index.md", "title": "Home"},
                {"path": "/about", "file": "about.md", "title": "About"},
                {"path": "/docs", "file": "docs.md", "title": "Documentation"}
            ]
        }
    
    def render_page(self, markdown_content: str, page_title: str, site_title: str) -> str:
        """Render a page using Mojo kernels (simulated for now)"""
        # In a real implementation, this would call the Mojo kernels
        # For now, we'll create a simple HTML template
        
        # Simulate markdown to HTML conversion
        html_content = markdown_content.replace("# ", "<h1>").replace("</h1>", "</h1>\n")
        html_content = html_content.replace("## ", "<h2>").replace("</h2>", "</h2>\n")
        html_content = html_content.replace("**", "<strong>").replace("</strong>", "</strong>")
        
        # Create full HTML page
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} - {site_title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            color: #333;
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        nav {{
            background: #ecf0f1;
            padding: 1rem;
            margin-bottom: 2rem;
            border-radius: 8px;
        }}
        nav a {{
            margin-right: 1rem;
            text-decoration: none;
            color: #3498db;
        }}
        nav a:hover {{ text-decoration: underline; }}
        .footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/about.html">About</a>
        <a href="/docs.html">Documentation</a>
    </nav>
    
    <main>
        {html_content}
    </main>
    
    <footer class="footer">
        <p>Built with UMG NeoCore - Powered by Mojo</p>
    </footer>
</body>
</html>"""
    
    def build_pages(self):
        """Build all pages"""
        config = self.load_page_config()
        site_title = config.get("title", "UMG NeoCore")
        
        # Create sample pages if they don't exist
        if not self.pages_dir.exists():
            self.pages_dir.mkdir()
            self.create_sample_pages()
        
        # Build each page
        for page in config.get("pages", []):
            page_file = self.pages_dir / page["file"]
            if page_file.exists():
                content = page_file.read_text()
                html = self.render_page(content, page["title"], site_title)
                
                # Determine output filename
                if page["path"] == "/":
                    output_file = self.build_dir / "index.html"
                else:
                    output_file = self.build_dir / (page["path"].strip("/") + ".html")
                
                output_file.write_text(html)
                print(f"Built: {output_file.relative_to(self.project_root)}")
    
    def create_sample_pages(self):
        """Create sample markdown pages"""
        samples = {
            "index.md": """# Welcome to UMG NeoCore

**UMG NeoCore** is a modular generation engine powered by Mojo kernels.

## Features

- Block-based architecture
- Mojo kernel compilation
- Static site generation
- Hot module reloading

Get started by exploring our documentation!
""",
            "about.md": """# About UMG NeoCore

UMG NeoCore represents the next evolution in modular web development.

## Our Mission

To create a truly composable web platform where:

- Every component is a self-contained block
- Blocks can snap together automatically
- Performance is guaranteed through Mojo compilation
- Creativity is recursive and unlimited

## Technology Stack

- **Mojo**: High-performance kernel implementation
- **Python**: Orchestration and tooling
- **JSON**: Block definitions and configuration
- **WASM**: Runtime execution target
""",
            "docs.md": """# Documentation

## Getting Started

1. Install dependencies with `pixi install`
2. Generate kernels with `python scripts/gen/gen_kernels_from_csv.py`
3. Build the site with `python -m neo_umg.build_site`

## Kernel Development

Each kernel is a Mojo function that performs a specific task:

- **HTML Tag Kernels**: Generate HTML elements
- **Markdown Parser**: Convert markdown to HTML
- **File I/O**: Read and write files
- **Router**: Map URLs to content

## Block System

Blocks are JSON files that define:

- Metadata and display properties
- Snap configurations
- Merge logic
- Associated Mojo kernels

See the README for more details on block anatomy.
"""
        }
        
        for filename, content in samples.items():
            (self.pages_dir / filename).write_text(content)
            print(f"Created sample page: pages/{filename}")
    
    def build(self):
        """Run the complete build process"""
        print("Starting static site build...")
        
        self.clean_build()
        self.copy_static_assets()
        self.build_pages()
        
        print(f"\nBuild complete! Site generated in: {self.build_dir}")
        print("To serve locally, run: python -m http.server 8000 --directory build")

def main():
    """Entry point for the builder"""
    project_root = Path(__file__).parent.parent
    builder = StaticSiteBuilder(project_root)
    builder.build()

if __name__ == "__main__":
    main()