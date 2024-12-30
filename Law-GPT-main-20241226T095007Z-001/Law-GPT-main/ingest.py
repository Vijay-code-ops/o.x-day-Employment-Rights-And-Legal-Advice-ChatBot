from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS

# Define paths
DATASET = r"C:\Users\surya abhiram\OneDrive\Desktop\Law-GPT-main\Law-GPT-main\dataset\A Handbook on Employee Relations and Labour Laws in India - PDF Drive.pdf"
FAISS_INDEX_DIR = r"C:\Users\surya abhiram\OneDrive\Desktop\Law-GPT-main\vectorstore"

# Create Vector Store and Index
def embed_all():
    # Load the PDF document
    loader = PyPDFLoader(DATASET)
    documents = loader.load()

    # Split the documents into smaller chunks for embedding
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    # Use HuggingFace embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create a FAISS vector store and embed the document chunks
    vector_store = FAISS.from_documents(chunks, embeddings)

    # Save the FAISS index to the specified directory
    vector_store.save_local(FAISS_INDEX_DIR)

if __name__ == "__main__":
    embed_all()
