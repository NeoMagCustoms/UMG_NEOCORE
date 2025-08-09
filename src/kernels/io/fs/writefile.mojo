from python import Python

fn io_fs_writefile_kernel(file_path: String, content: String) raises -> Bool:
    """
    Write a text file (UTF-8, create dirs)
    
    Args:
        file_path: Path to file to write
        content: Content to write
        
    Returns:
        True if successful
        
    Raises:
        Error if write fails
    """
    let py = Python.import_module("builtins")
    let pathlib = Python.import_module("pathlib")
    
    try:
        # Create Path object
        let path = pathlib.Path(file_path)
        
        # Create parent directories if they don't exist
        let parent = path.parent
        if not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
        
        # Write content to file
        path.write_text(content, encoding="utf-8")
        
        return True
        
    except e:
        raise Error("Failed to write file: " + str(e))

fn main():
    try:
        # Test writing to a new file
        let success = io_fs_writefile_kernel("test_output/hello.txt", "Hello, Mojo World!\nThis is a test file.")
        if success:
            print("Successfully wrote file!")
            
        # Verify by reading it back
        let py = Python.import_module("pathlib")
        let path = py.Path("test_output/hello.txt")
        if path.exists():
            print("File exists at test_output/hello.txt")
            let content = path.read_text()
            print("Content:", content)
            
    except e:
        print("Error:", e)