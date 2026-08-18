from langchain_huggingface import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

text = "how did stock market do yesterday if you were to look at it overall?"

result = embedding.embed_query(text)

print(result);