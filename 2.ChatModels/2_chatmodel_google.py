from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"  # Latest supported model as of now
)

result = model.invoke("Tell me about how tomatoes became a thing in Italy")

print(result.content)
