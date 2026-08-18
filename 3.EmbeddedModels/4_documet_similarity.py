from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

load_dotenv()

embedding = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=32)

documents = [
    "1234567890",
    "qwertyuiop",
    "!@#$%^&*()",
]

query = "Tell me anout numbers!"

doc_embed = embedding.embed_documents(documents)
query_embed = embedding.embed_query(query)

score = cosine_similarity([query_embed],doc_embed)[0]  #2D inpur for cosine_simialrity

# 1. Find the index of the highest score
index = np.argmax(score)

# 2. Grab the actual highest score using that index
best_score = score[index]

# 3. Print your results!
print("Query:", query)
print("Best Match:", documents[index])
print("Similarity is:", best_score)