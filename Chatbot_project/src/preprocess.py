# preprocess.py
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.llms.gemini import Gemini
from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker
from llama_parse import LlamaParse
from pathlib import Path
from llama_index.core.prompts import PromptTemplate
from src.config import GOOGLE_API_KEY
from src.config import LLAMA_CLOUD_API_KEY
from src.config import CHATBOT_NAME
import os
os.environ["LLAMA_CLOUD_API_KEY"] = LLAMA_CLOUD_API_KEY

def get_personality_prompt(personality: str):
    """Generate the prompt based on the selected personality."""
    if personality == "Friendly":
        return (
            "You are a " + CHATBOT_NAME + 
            ",friendly and warm AI assistant. You engage in conversations in a cheerful, informal, and approachable tone. Below is the context information you can rely on:\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Please respond to the following query with a friendly and approachable tone. Your response should be clear and user-friendly.\n"
            "Query: {query_str}\n"
            "Answer: "
        )
    elif personality == "Professional":
        return (
            "You are " + CHATBOT_NAME + 
             " a professional AI assistant. You provide concise, clear, and precise responses while maintaining a formal tone. Below is the context information you can rely on:\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Please respond to the following query with a formal tone. Your response should be accurate and helpful.\n"
            "Query: {query_str}\n"
            "Answer: "
        )
    elif personality == "Witty":
        return (
                "You are " + CHATBOT_NAME + 
                "a clever and quick-witted AI assistant. Your responses are sharp, playful, and laced with humor or clever insights while staying relevant and helpful. Use the context below to craft responses that are both amusing and intelligent:\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Please respond to the following query with wit and humor, making your answer both entertaining and insightful:\n"
        "Query: {query_str}\n"
        "Answer:"
        )
    else:
        # Default case
        return (
           "You are " + CHATBOT_NAME + 
            "an AI assistant designed to provide accurate, concise, and helpful responses. Below is the context information you can rely on:\n"
            "---------------------\n"
            "{context_str}\n"
            "---------------------\n"
            "Please respond to the following query using the relevant information from the context provided. Your response should be clear and user-friendly.\n"
            "Query: {query_str}\n"
            "Answer: "
        )

def config_parameters():
    """Configure embedding model and LLM settings."""
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")
    Settings.llm = Gemini(api_key=GOOGLE_API_KEY)

# Setup vector store for PDFs using LanceDB
def setup_vector_store(uri: str):
    """Set up the vector store for storing document embeddings."""
    return LanceDBVectorStore(uri=uri)

# Load PDF data using LlamaParse
def load_pdf_data(pdf_path: str):
    """Load data from a PDF using LlamaParse."""
    return LlamaParse(result_type="markdown").load_data(pdf_path)

def iterate_data(directory_path: str):
    # Path to the folder containing files
    folder_path = Path(directory_path)
    print(folder_path)
    documents = []
    # Iterate over all files in the folder
    for file in folder_path.iterdir():
        print(file)
        # Check if the path is a file (not a directory)
        if file.is_file():
            documents = documents + load_pdf_data(file)
    return documents


# Create vector store index from documents
def create_vector_store_index(documents, vector_store_uri: str):
    """Create a vector store index from documents."""
    vector_store = setup_vector_store(vector_store_uri)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_documents(documents, storage_context=storage_context)

# Create reranker for query processing
def create_reranker():
    """Create a FlagEmbeddingReranker for post-processing queries."""
    return FlagEmbeddingReranker(top_n=5, model="BAAI/bge-reranker-large")

# Set up the query engine
def setup_query_engine(index, reranker, personality="Friendly"):
    """Setup query engine for making queries, dynamically changing the prompt based on personality."""
    # Get the updated prompt based on the selected personality
    print(personality)
    prompt_str = get_personality_prompt(personality)
    return index.as_query_engine(similarity_top_k=10, node_postprocessors=[reranker],text_qa_template = PromptTemplate(prompt_str))

# Query execution function
def execute_query(query: str, query_engine):
    """Execute a query using the query engine."""
    return query_engine.query(query)
