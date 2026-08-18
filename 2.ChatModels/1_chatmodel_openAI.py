from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(
    model_name='gpt-4',
    temperature=1.0,          # Adjusted for more balanced creativity
    max_tokens=1000             # Corrected parameter name
)

result = model.invoke("Tell me about how tomatoes became a thing in Italy")

print(result.content)
