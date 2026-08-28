from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_core.runnables import RunnablePassthrough, RunnableSequence, RunnableParallel

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

joke_chain = RunnableSequence(prompt,model,parser)

parallel_chain = RunnableParallel(
    {
        "joke": RunnablePassthrough(),
        "explanation": prompt2 | model | parser
    }
)
final_chain = RunnableSequence(joke_chain, parallel_chain)

print(final_chain.invoke({"topic": "Mr President"}))