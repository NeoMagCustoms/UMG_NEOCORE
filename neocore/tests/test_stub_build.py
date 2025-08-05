import os
import pathlib
import pytest

def test_all_mojo_stubs_generated():
    """Test that all Mojo stub files have been generated."""
    root = pathlib.Path(__file__).parent.parent
    kernels_dir = root / "src" / "kernels"
    
    # Count .mojo files
    mojo_files = list(kernels_dir.rglob("*.mojo"))
    
    # Should have at least 1500 files
    assert len(mojo_files) >= 1500, f"Expected at least 1500 Mojo files, found {len(mojo_files)}"
    
    # Check that files have basic structure
    sample_files = mojo_files[:10]  # Check first 10 files
    for mojo_file in sample_files:
        content = mojo_file.read_text()
        assert "@compiler.register" in content, f"Missing @compiler.register in {mojo_file}"
        assert "struct" in content, f"Missing struct definition in {mojo_file}"
        assert "fn execute()" in content, f"Missing execute function in {mojo_file}"
        
def test_directory_structure():
    """Test that directory structure follows domain/subdomain pattern."""
    root = pathlib.Path(__file__).parent.parent
    kernels_dir = root / "src" / "kernels"
    
    # Check some expected domains exist
    expected_domains = ["accessibility", "analytics", "api", "auth", "cache", "component"]
    
    for domain in expected_domains:
        domain_dir = kernels_dir / domain
        assert domain_dir.exists(), f"Missing domain directory: {domain}"
        assert domain_dir.is_dir(), f"{domain} should be a directory"
        
        # Check that domain has subdirectories
        subdirs = list(domain_dir.iterdir())
        assert len(subdirs) > 0, f"Domain {domain} has no subdirectories"