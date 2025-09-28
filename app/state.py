import os
from datetime import datetime
from typing import Optional, Dict, List
from llama_index.core import VectorStoreIndex, StorageContext

from app.config import settings
from app.utils.storage import is_valid_index_dir
from app.utils.faiss import load_faiss_index_from_storage

class GlobalState:
    """Singleton class to manage global application state."""
    
    _instance: Optional['GlobalState'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.loaded_indexes: Dict[str, VectorStoreIndex] = {}
            self.storage_contexts: Dict[str, StorageContext] = {}
            self.available_indexes: Dict[str, dict] = {}  # Metadata only

            self._initialized = True

    def discover_persisted_indexes(self):
        """Discover and register persisted indexes from storage directory."""
        if not os.path.exists(settings.storage_dir):
            return
        
        # Scan the storage directory for valid indexes
        for item in os.listdir(settings.storage_dir):
            index_dir = os.path.join(settings.storage_dir, item)
            if os.path.isdir(index_dir) and is_valid_index_dir(index_dir):
                self.register_index(item)

    def register_index(self, index_name: str):
        """Register an index without loading it."""
        self.available_indexes[index_name] = {
            "loaded": False,
            "last_accessed": None
        }
    
    def set_index(self, 
                  index_name: str,
                  index: VectorStoreIndex, 
                  storage_context: StorageContext
                  ):
        """Set the current index and storage context."""
        self.loaded_indexes[index_name] = index
        self.storage_contexts[index_name] = storage_context
        self.available_indexes[index_name] = {
            "loaded": True,
            "last_accessed": datetime.now()
        }

    def get_index(self, index_name: str) -> Optional[VectorStoreIndex]:
        """Get the current index and do lazy loading if necessary."""
        # If the index is already loaded, return it
        if index_name in self.loaded_indexes:
            self.available_indexes[index_name]["last_accessed"] = datetime.now()
            return self.loaded_indexes[index_name]
        
        # If the index is registered but not loaded, load it
        if index_name in self.available_indexes:
            index, storage_context = load_faiss_index_from_storage(index_name)
            self.loaded_indexes[index_name] = index
            self.storage_contexts[index_name] = storage_context
            self.available_indexes[index_name]["loaded"] = True
            self.available_indexes[index_name]["last_accessed"] = datetime.now()
            return index
        
    def get_storage_context(self, index_name: str) -> Optional[StorageContext]:
        """Get the current storage context."""
        return self.storage_contexts.get(index_name)

    def is_index_ready(self, index_name: str) -> bool:
        """Check if the index is ready for queries."""
        return self.loaded_indexes.get(index_name) is not None
    
    def list_available_indexes(self) -> List[str]:
        """List all available indexes (both loaded and unloaded)."""
        return list(self.available_indexes.keys())

    def list_loaded_indexes(self) -> List[str]:
        """List only currently loaded indexes."""
        return list(self.loaded_indexes.keys())

    def delete_index(self, index_name: str):
        self.loaded_indexes.pop(index_name, None)
        self.storage_contexts.pop(index_name, None)


# Global instance
app_state = GlobalState()