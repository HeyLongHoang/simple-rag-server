from fastapi import HTTPException

def validate_index_name(index_name: str):
    """Validate index name format"""
    if not index_name or not isinstance(index_name, str):
        raise HTTPException(status_code=400, detail="Index name must be a non-empty string")
    
    # Check for invalid characters that could cause file system issues
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    if any(char in index_name for char in invalid_chars):
        raise HTTPException(
            status_code=400, 
            detail=f"Index name contains invalid characters. Avoid: {', '.join(invalid_chars)}"
        )
    
    if len(index_name) > 100:
        raise HTTPException(status_code=400, detail="Index name must be 100 characters or less")