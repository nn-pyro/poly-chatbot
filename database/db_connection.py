import os
from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
load_dotenv()


embeddings = HuggingFaceEmbeddings(
    model_name = "./models/halong_embedding"
)

connection = os.getenv("CONNECTION_STR")
collection_name = "pyro_collection"

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)

def get_vector_db():
    return vector_store