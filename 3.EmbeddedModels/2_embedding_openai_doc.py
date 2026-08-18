from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

documets = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J"
]
embedding_doc = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=32)

result = embedding_doc.embed_documents(documets)
print(result);