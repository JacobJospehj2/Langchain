from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct", 
    task="text-generation",
    max_new_tokens=256
)

model = ChatHuggingFace(llm=llm)

result = model.invoke("How did stock market do yesterday if you were to look at it overal?")

print(result.content)