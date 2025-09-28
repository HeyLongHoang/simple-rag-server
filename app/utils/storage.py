import os

from app.config import settings

def ensure_index_storage_dir(index_name: str):
    index_dir = os.path.join(settings.storage_dir, index_name)
    os.makedirs(index_dir, exist_ok=True)
    return index_dir

def get_index_storage_dir(index_name: str) -> str:
    return os.path.join(settings.storage_dir, index_name)

def is_valid_index_dir(index_dir: str) -> bool:
    """Check if the directory contains necessary files for a valid index."""
    required_files = ["docstore.json", "index_store.json"]
    
    # Check for any vector store file (could be default__vector_store.json or vector_store.json)
    has_vector_store = any(
        f.endswith("vector_store.json") 
        for f in os.listdir(index_dir) 
        if os.path.isfile(os.path.join(index_dir, f))
    )
    
    # Check required files exist
    has_required_files = all(
        os.path.exists(os.path.join(index_dir, file)) 
        for file in required_files
    )
    
    return has_required_files and has_vector_store