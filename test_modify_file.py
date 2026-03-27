#!/usr/bin/env python3
"""
Test script for modify_file.py functions
Tests edge cases and verifies functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modify_file import (
    replace_text, 
    replace_all, 
    insert_after_marker, 
    insert_before_marker,
    read_file,
    write_file,
    backup_file
)

def test_replace_text():
    """Test replace_text function"""
    print("\n" + "="*60)
    print("TEST 1: replace_text() - Single occurrence")
    print("="*60)
    
    content = "Hello world\nThis is a test\nHello again"
    old = "world"
    new = "universe"
    result = replace_text(content, old, new, "Test single replacement")
    assert "universe" in result, "Should replace single occurrence"
    assert result.count("universe") == 1, "Should only replace once"
    print("✅ PASSED: Single replacement works")
    
    print("\n" + "="*60)
    print("TEST 2: replace_text() - No occurrence")
    print("="*60)
    
    content = "Hello world"
    old = "notfound"
    new = "replacement"
    result = replace_text(content, old, new, "Test no match")
    assert result == content, "Should return original when no match"
    print("✅ PASSED: No match returns original")
    
    print("\n" + "="*60)
    print("TEST 3: replace_text() - Multiple occurrences (default behavior)")
    print("="*60)
    
    content = "test test test"
    old = "test"
    new = "passed"
    result = replace_text(content, old, new, "Test multiple without allow_multiple", allow_multiple=False)
    assert result == content, "Should not replace when multiple found and allow_multiple=False"
    print("✅ PASSED: Multiple occurrences blocked without allow_multiple flag")
    
    print("\n" + "="*60)
    print("TEST 4: replace_text() - Multiple occurrences with allow_multiple=True")
    print("="*60)
    
    content = "test test test"
    old = "test"
    new = "passed"
    result = replace_text(content, old, new, "Test multiple with flag", allow_multiple=True)
    assert result.count("passed") == 3, "Should replace all when allow_multiple=True"
    print("✅ PASSED: Multiple occurrences replaced with allow_multiple=True")
    

def test_replace_all():
    """Test replace_all function"""
    print("\n" + "="*60)
    print("TEST 5: replace_all() - Replace all occurrences")
    print("="*60)
    
    content = "foo bar foo bar foo"
    old = "foo"
    new = "baz"
    result = replace_all(content, old, new, "Test replace all")
    assert result.count("baz") == 3, "Should replace all occurrences"
    print("✅ PASSED: replace_all replaces all occurrences")
    
    print("\n" + "="*60)
    print("TEST 6: replace_all() - No occurrences")
    print("="*60)
    
    content = "hello world"
    old = "notfound"
    new = "replacement"
    result = replace_all(content, old, new, "Test no match")
    assert result == content, "Should return original when no match"
    print("✅ PASSED: replace_all returns original when no match")


def test_insert_after_marker():
    """Test insert_after_marker function"""
    print("\n" + "="*60)
    print("TEST 7: insert_after_marker() - Marker found")
    print("="*60)
    
    content = "line1\nline2\nline3"
    marker = "line2"
    insert_text = "inserted"
    result = insert_after_marker(content, marker, insert_text, strict=True)
    assert "inserted" in result, "Should insert text after marker"
    lines = result.split('\n')
    assert lines[1] == "line2", "Marker should remain in place"
    assert lines[2] == "inserted", "Text should be inserted after marker"
    print("✅ PASSED: Insert after marker works")
    
    print("\n" + "="*60)
    print("TEST 8: insert_after_marker() - Marker not found (strict=True)")
    print("="*60)
    
    content = "line1\nline2"
    marker = "notfound"
    insert_text = "inserted"
    result = insert_after_marker(content, marker, insert_text, strict=True)
    assert result == content, "Should return original when marker not found in strict mode"
    print("✅ PASSED: Strict mode returns original when marker not found")
    
    print("\n" + "="*60)
    print("TEST 9: insert_after_marker() - Marker not found (strict=False)")
    print("="*60)
    
    content = "line1\nline2"
    marker = "notfound"
    insert_text = "inserted"
    result = insert_after_marker(content, marker, insert_text, strict=False)
    assert "inserted" in result, "Should append to end when marker not found in non-strict mode"
    print("✅ PASSED: Non-strict mode appends to end")


def test_insert_before_marker():
    """Test insert_before_marker function"""
    print("\n" + "="*60)
    print("TEST 10: insert_before_marker() - Marker found")
    print("="*60)
    
    content = "line1\nline2\nline3"
    marker = "line2"
    insert_text = "inserted"
    result = insert_before_marker(content, marker, insert_text, strict=True)
    assert "inserted" in result, "Should insert text before marker"
    lines = result.split('\n')
    assert lines[1] == "inserted", "Text should be inserted before marker"
    assert lines[2] == "line2", "Marker should remain in place"
    print("✅ PASSED: Insert before marker works")
    
    print("\n" + "="*60)
    print("TEST 11: insert_before_marker() - Marker not found (strict=True)")
    print("="*60)
    
    content = "line1\nline2"
    marker = "notfound"
    insert_text = "inserted"
    result = insert_before_marker(content, marker, insert_text, strict=True)
    assert result == content, "Should return original when marker not found in strict mode"
    print("✅ PASSED: Strict mode returns original when marker not found")
    
    print("\n" + "="*60)
    print("TEST 12: insert_before_marker() - Marker not found (strict=False)")
    print("="*60)
    
    content = "line1\nline2"
    marker = "notfound"
    insert_text = "inserted"
    result = insert_before_marker(content, marker, insert_text, strict=False)
    assert "inserted" in result, "Should append to end when marker not found in non-strict mode"
    print("✅ PASSED: Non-strict mode appends to end")


def test_with_real_file():
    """Test modifications on a real temporary file"""
    print("\n" + "="*60)
    print("TEST 13: Real file modification test")
    print("="*60)
    
    # Create a test file
    test_file = "test_temp_file.txt"
    original_content = """# Test File
def hello():
    print("Hello")

def goodbye():
    print("Goodbye")
"""
    
    # Write test file
    with open(test_file, 'w') as f:
        f.write(original_content)
    print(f"✅ Created test file: {test_file}")
    
    # Read and modify
    content = read_file(test_file)
    backup_file(test_file)  # Create backup
    
    # Test 1: Replace text
    content = replace_text(content, 'print("Hello")', 'print("Hello World!")', "Update hello function")
    assert 'print("Hello World!")' in content, "Should update hello function"
    
    # Test 2: Insert after marker
    content = insert_after_marker(content, 'def hello():', '    # This is the hello function', strict=True)
    assert '# This is the hello function' in content, "Should insert comment after def"
    
    # Test 3: Insert before marker
    content = insert_before_marker(content, 'def goodbye():', '\ndef new_function():\n    print("New")', strict=True)
    assert 'def new_function()' in content, "Should insert new function before goodbye"
    
    # Write modified content
    write_file(test_file, content)
    
    # Verify changes
    final_content = read_file(test_file)
    assert 'print("Hello World!")' in final_content, "Final file should have updated hello"
    assert '# This is the hello function' in final_content, "Final file should have inserted comment"
    assert 'def new_function()' in final_content, "Final file should have new function"
    
    # Clean up
    os.remove(test_file)
    os.remove(test_file + ".backup")
    print("✅ PASSED: Real file modification test")
    print("✅ Cleaned up test files")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 MODIFY_FILE.PY TEST SUITE")
    print("="*60)
    
    try:
        # Run all tests
        test_replace_text()
        test_replace_all()
        test_insert_after_marker()
        test_insert_before_marker()
        test_with_real_file()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nSummary:")
        print("  • replace_text() - Works correctly with exact matching")
        print("  • replace_all() - Replaces all occurrences as expected")
        print("  • insert_after_marker() - Inserts at correct position")
        print("  • insert_before_marker() - Inserts at correct position")
        print("  • File I/O operations - Working properly")
        print("\nThe modify_file.py tool is ready to use!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
