from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENVIRONMENT")

# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)
index_name = "loubbyai-index"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-west1-aws")
    )
index = pc.Index(index_name)
print(f"Pinecone index '{index_name}' is ready!")

# Initialize Sentence Transformer
embedder = SentenceTransformer("all-MiniLM-L6-v2")
print("Sentence Transformer embedder initialized!")

# Load custom data
data_dir = "data/"
documents = []
for filename in os.listdir(data_dir):
    file_path = os.path.join(data_dir, filename)
    if filename.endswith(".txt"):
        loader = TextLoader(file_path)
    elif filename.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        continue
    docs = loader.load()
    documents.extend(docs)

# Chunk documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunked_documents = text_splitter.split_documents(documents)
print(f"Loaded and chunked {len(chunked_documents)} document segments!")

# Embed and store in Pinecone
vector_store = PineconeVectorStore.from_documents(
    documents=chunked_documents,
    embedding=embedder,
    index_name=index_name,
    pinecone_api_key=pinecone_api_key
)
print("Custom data successfully embedded and stored in Pinecone!")

# Optional: Test retrieval
query = "What is in my custom data?"
query_embedding = embedder.encode(query).tolist()
results = index.query(vector=query_embedding, top_k=2, include_metadata=True)
for match in results["matches"]:
    print(f"Score: {match['score']}, Text: {match['metadata']['text'][:100]}...")