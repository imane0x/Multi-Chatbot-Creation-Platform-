# main.py

from src.preprocess import config_parameters, iterate_data, create_vector_store_index, create_reranker, setup_query_engine, execute_query
from pathlib import Path


def load_and_index_pdf(directory_path: str, vector_store_uri: str):
    """Load PDF documents and create the vector store index."""
    pdf_documents = iterate_data(directory_path)
    index = create_vector_store_index(pdf_documents, vector_store_uri)
    return index

def setup_reranker_and_query_engine(index, reranker,personality):
    """Set up reranker and query engine."""
    query_engine = setup_query_engine(index, reranker,personality)
    return query_engine

def execute_query_on_engine(query: str, query_engine):
    """Execute the query and return the response."""
    response = execute_query(query, query_engine)
    return response

def chat(directory_path: str, query: str,personality):
    """Main function to process PDF and execute queries."""
    # Configuring settings
    config_parameters()
    
    # Load and index PDF data
    vector_store_uri = "/tmp/lancedb_parser"

    index = load_and_index_pdf(directory_path, vector_store_uri)
   
    # Set up reranker and query engine
    reranker = create_reranker()
 
    query_engine = setup_reranker_and_query_engine(index, reranker,personality)
   
    # Execute the query
    response = execute_query_on_engine(query, query_engine)
    print(response)
    return response




# Example usage
if __name__ == "__main__":
    query_example = "what is Adjusted EBITDA 2021 vs 2022 ? what is interest expense"
    directory_path_example = "data"
    chat(directory_path_example, query_example)
