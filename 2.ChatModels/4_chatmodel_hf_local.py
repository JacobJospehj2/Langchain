from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from dotenv import load_dotenv
import os

load_dotenv()

# Set your local cache folder
os.environ['HF_HOME'] = r'C:\Users\josr1l\OneDrive - cchmc\Desktop\LangChain'

# Set up the local model pipeline
llm = HuggingFacePipeline.from_model_id(
    model_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    task="text-generation",
    # clean_up_tokenization_spaces=False removes the 3rd warning
    pipeline_kwargs={
        "max_new_tokens": 100, 
        "clean_up_tokenization_spaces": False
    }
) 

model = ChatHuggingFace(llm=llm)

result = model.invoke("How did stock market do yesterday if you were to look at it overall?")

print("\n--- Model Response ---")
print(result.content)