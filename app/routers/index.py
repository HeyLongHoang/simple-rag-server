import os
import shutil
import tempfile
from typing import List

from llama_index.core import SimpleDirectoryReader
from fastapi import APIRouter, HTTPException, File, UploadFile

from app.state import app_state
from app.utils.faiss import build_faiss_index_from_documents
from app.utils.storage import (
    ensure_index_storage_dir,
    get_index_storage_dir,
)
from app.utils.index import validate_index_name
from app.routers.schema import (
    IndexStatusResponse, 
    BuildIndexRequest,
    BuildIndexResponse,
)

router = APIRouter(tags=["Build index"])

@router.post("/build", response_model=BuildIndexResponse)
def build_index(request: BuildIndexRequest):
    """Create a vector index from documents in a directory"""

    # Validate index name
    validate_index_name(request.index_name)

    try:
        # Check if documents path exists
        if not os.path.exists(request.documents_path):
            raise HTTPException(status_code=404, detail="Documents path does not exist.")
        
        # Load documents  
        documents = SimpleDirectoryReader(request.documents_path).load_data()
        if not documents:
            raise HTTPException(
                status_code=400, 
                detail="No documents found in the specified path."
            )
        
        # Create Faiss index
        index, storage_context = build_faiss_index_from_documents(documents)

        # Persist index
        ensure_index_storage_dir(request.index_name)
        index.storage_context.persist(persist_dir=get_index_storage_dir(request.index_name))
        
        # Store in global state
        app_state.set_index(
            index_name=request.index_name,
            index=index,
            storage_context=storage_context
        )

        return BuildIndexResponse(
            index_name=request.index_name,
            status="success",
            message=f"Index built and persisted successfully from {len(documents)} documents.",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building index: {str(e)}")

@router.post("/upload-build/{index_name}", response_model=BuildIndexResponse)
def upload_documents(index_name: str, files: List[UploadFile] = File(...)):
    """Upload documents and create/update vector index"""

    # Validate index name
    validate_index_name(index_name)

    try:
        # Create a temporary directory to save uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            for file in files:
                if not file.filename:
                    raise HTTPException(
                        status_code=400, 
                        detail="Uploaded file is missing a filename."
                    )
                
                # Currently only supporting .txt and .md files
                if not file.filename.endswith((".txt", ".md")):
                    raise HTTPException(
                        status_code=400, 
                        detail="Only .txt and .md files are supported."
                    )
                
                # Save the uploaded file to the temporary directory
                file_path = os.path.join(temp_dir, file.filename)
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)

            # Load documents from the temporary directory
            documents = SimpleDirectoryReader(temp_dir).load_data()
            if not documents:
                raise HTTPException(
                    status_code=400, 
                    detail="No valid documents found in the uploaded files."
                )
            
            # Create Faiss index
            index, storage_context = build_faiss_index_from_documents(documents)

            # Persist index
            ensure_index_storage_dir(index_name)
            index.storage_context.persist(persist_dir=get_index_storage_dir(index_name))

            # Store in global state
            app_state.set_index(
                index_name=index_name, 
                index=index, 
                storage_context=storage_context
            )

            return BuildIndexResponse(
                index_name=index_name,
                status="success",
                message=f"Uploaded and indexed {len(documents)} documents successfully.",
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading documents: {str(e)}")

@router.get("/status/{index_name}", response_model=IndexStatusResponse)
def get_index_status(index_name: str):
    """Get the status of a vector index"""

    # Validate index name
    validate_index_name(index_name)

    if index_name not in app_state.available_indexes:
        raise HTTPException(status_code=404, detail="Index not found.")
    
    metadata = app_state.available_indexes[index_name]
    return IndexStatusResponse(
        index_name=index_name,
        loaded=metadata["loaded"],
        last_accessed=metadata["last_accessed"],
        storage_path=get_index_storage_dir(index_name)
    )

@router.get("/list_available_indexes", response_model=List[str])
def list_available_indexes():
    """List all available indexes"""
    return app_state.list_available_indexes()

@router.get("/list_loaded_indexes", response_model=List[str])
def list_loaded_indexes():
    """List only currently loaded indexes"""
    return app_state.list_loaded_indexes()