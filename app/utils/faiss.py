import faiss
from typing import List, Tuple
from llama_index.core import (
    VectorStoreIndex, 
    StorageContext, 
    Document,
    load_index_from_storage
)
from llama_index.vector_stores.faiss import FaissVectorStore
from fastapi import HTTPException

from app.config import settings
from app.embed_model import get_embed_model
from app.utils.index import validate_index_name
from app.utils.storage import get_index_storage_dir

def create_faiss_index() -> faiss.IndexFlatL2:
    return faiss.IndexFlatL2(settings.openai_embed_dim)

def build_faiss_index_from_documents(documents: List[Document]) \
-> Tuple[VectorStoreIndex, StorageContext]:
    """Helper function to build a Faiss index from documents."""
    try:
        if not documents:
            raise ValueError("Documents list cannot be empty")
        
        faiss_index = create_faiss_index()
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents, 
            embed_model=get_embed_model(),
            storage_context=storage_context
        )
        return index, storage_context
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to build FAISS index: {str(e)}"
        )
    
def load_faiss_index_from_storage(index_name: str) \
-> Tuple[VectorStoreIndex, StorageContext]:
    """Helper function to load a Faiss index from storage."""
    
    # Validate index name
    validate_index_name(index_name)

    try:
        index_storage_dir = get_index_storage_dir(index_name)
        if not index_storage_dir:
            raise HTTPException(status_code=404, detail="Index storage directory does not exist.")
        
        # Load the Faiss index from the index persistence directory
        vector_store = FaissVectorStore.from_persist_dir(index_storage_dir)
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
            persist_dir=index_storage_dir,
        )
        loaded_index = load_index_from_storage(
            storage_context=storage_context,
            embed_model=get_embed_model()
        )
        
        # Cast to VectorStoreIndex (we know it's a VectorStoreIndex from our build process)
        if isinstance(loaded_index, VectorStoreIndex):
            index = loaded_index
        else:
            raise HTTPException(status_code=500, detail="Loaded index is not a VectorStoreIndex")
        
        return index, storage_context

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to load FAISS index: {str(e)}"
        )