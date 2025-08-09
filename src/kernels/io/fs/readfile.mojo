from python import Python

fn io_fs_readfile_kernel(file_path: String) raises -> String:
    """
    Read a text file (UTF-8)
    
    Args:
        file_path: Path to file to read
        
    Returns:
        File contents as UTF-8 string
        
    Raises:
        Error if file cannot be read
    """
    let py = Python.import_module("builtins")
    let pathlib = Python.import_module("pathlib")
    
    try:
        # Create Path object
        let path = pathlib.Path(file_path)
        
        # Check if file exists
        if not path.exists():
            raise Error("File not found: " + file_path)
        
        # Read file contents
        let content = path.read_text(encoding="utf-8")
        
        # Convert Python string to Mojo String
        return String(content)
        
    except e:
        raise Error("Failed to read file: " + str(e))

fn main():
    try:
        # Try to read an existing file
        let content = io_fs_readfile_kernel("pyproject.toml")
        print("Successfully read file!")
        print("First 100 chars:", content[:100])
    except e:
        print("Error:", e)
    
    try:
        # Try to read a non-existent file
        let content = io_fs_readfile_kernel("non_existent.txt")
    except e:
        print("Expected error:", e)