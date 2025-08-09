# Documentation

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
