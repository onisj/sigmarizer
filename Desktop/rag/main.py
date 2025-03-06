import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from pinecone import Pinecone, ServerlessSpec

# Step 1: Set up API keys and environment
os.environ["GROQ_API_KEY"] = "your_groq_api_key_here"  # Replace with your Groq API key
os.environ["PINECONE_API_KEY"] = "your_pinecone_api_key_here"  # Replace with your Pinecone API key

# Step 2: Initialize FastAPI app
app = FastAPI(title="LoubbyGuide Chatbot API", description="AI-powered navigation assistant for Loubby")

# Step 3: Initialize embeddings with a more precise model
# Using 'all-mpnet-base-v2' (768 dimensions) for better semantic understanding
embedding_function = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")

# Step 4: Initialize Pinecone
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index_name = "loubbyguide-index"

# Create Pinecone index if it doesn’t exist (updated dimension for all-mpnet-base-v2)
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,  # Matches all-mpnet-base-v2 embeddings 
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Step 5: Load multiple files from a directory
def load_documents_from_directory(directory_path: str):
    # Use DirectoryLoader to load all .txt files from the specified directory
    loader = DirectoryLoader(
        directory_path,
        glob="*.txt",  # Load only .txt files
        loader_cls=TextLoader  # Use TextLoader for .txt files
    )
    documents = loader.load()
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)  # Increased overlap for better context
    split_docs = text_splitter.split_documents(documents)
    return split_docs

# Load and index documents (replace 'docs/' with your directory path)
directory_path = "docs/"  # Directory containing your Loubby documentation files
split_docs = load_documents_from_directory(directory_path)

# Index documents in Pinecone
vector_store = PineconeVectorStore.from_documents(
    documents=split_docs,
    embedding=embedding_function,
    index_name=index_name
)

# Step 6: Initialize Groq LLM
llm = ChatGroq(
    groq_api_key=os.environ["GROQ_API_KEY"],
    model_name="llama3-8b-8192"
)

# Step 7: Define request model for FastAPI
class QueryRequest(BaseModel):
    query: str

# Step 8: RAG function with improved retrieval
def rag_query(query: str) -> str:
    try:
        # Retrieve relevant documents from Pinecone (increased k for more context)
        retrieved_docs = vector_store.similarity_search(query, k=4)  # Increased to 4 for better coverage
        context = "\n".join([doc.page_content for doc in retrieved_docs])

        # Construct a detailed prompt
        prompt = f"""
        You are LoubbyGuide, an AI assistant designed to help users navigate the Loubby platform based on its navigation documentation.
        Use the following context to provide a clear, concise, and step-by-step answer to the query. If the context doesn’t fully cover the query, use your general knowledge to assist, but stay relevant to Loubby navigation.
        Context: {context}
        Query: {query}
        Answer in a friendly tone with numbered steps if applicable, and offer additional help if relevant.
        Answer:
        """
        
        # Generate response
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Step 9: Define API endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to the LoubbyGuide Chatbot API. Use /chat to ask questions about Loubby navigation!"}

@app.post("/chat")
async def chat(request: QueryRequest):
    answer = rag_query(request.query)
    return {"query": request.query, "answer": answer}

# Step 10: Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)