from fastapi import APIRouter, HTTPException

from app.state import app_state
from app.llm import get_llm
from app.utils.index import validate_index_name
from app.routers.schema import QueryIndexRequest, QueryIndexResponse

router = APIRouter(tags=["Query index"])

@router.post("/query", response_model=QueryIndexResponse)
def query_index(request: QueryIndexRequest):
    """Query a specific vector index"""

    # Validate index name
    validate_index_name(request.index_name)
    
    try:
        # Get the index from global state
        index = app_state.get_index(request.index_name)
        if index is None:
            raise HTTPException(status_code=404, detail="Index not found.")
        
        # Query the index 
        query_engine = index.as_query_engine(
            similarity_top_k=request.similarity_top_k,
            llm=get_llm()
        )
        response = query_engine.query(request.query)
        
        # Extract source information if available
        sources = []
        if hasattr(response, 'source_nodes') and response.source_nodes:
            sources = [
                node.node.get_content() 
                for node in response.source_nodes
            ]
        
        return QueryIndexResponse(
            response=str(response),
            sources=sources
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying index: {str(e)}")