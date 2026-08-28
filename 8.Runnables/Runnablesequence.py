from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_core.runnables import RunnableSequence

load_dotenv()

prompt = PromptTemplate(
    template="Tell me a joke about {topic}",
    input_variables=["topic"]
)

model = ChatGroq(
    model="openai/gpt-oss-120b"
)

prompt2 = PromptTemplate(
    template="Explain the joke in detail {text}",
    input_variables=["text"]
)

parser = StrOutputParser()

chain = RunnableSequence(prompt,model,parser,prompt2,model,parser)

print(chain.invoke({"topic": "Mr President"}))