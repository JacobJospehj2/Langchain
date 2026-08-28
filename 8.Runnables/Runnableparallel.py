from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_core.runnables import RunnableParallel

load_dotenv()

prompt = PromptTemplate(
    template="Generate a tweet about {topic}",
    input_variables=["topic"]
)

model = ChatGroq(
    model="openai/gpt-oss-120b"
)

parser = StrOutputParser()

prompt2 = PromptTemplate(
    template="Generate a LinkedIn post about {topic}",
    input_variables=["topic"]
)
parallel_chain = RunnableParallel(
    {
        "tweet": prompt | model | parser,
        "linkedin": prompt2 | model | parser
    }
)

print(parallel_chain.invoke({"topic": "The weather in London"}))