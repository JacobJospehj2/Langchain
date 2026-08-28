from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnableSequence,
    RunnablePassthrough,
)
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv


def word_count(text):
    return len(text.split())


load_dotenv()

runnable_lambda = RunnableLambda(word_count)

prompt = PromptTemplate(
    template="Tell me a joke about {topic}",
    input_variables=["topic"]
)

model = ChatGroq(
    model="openai/gpt-oss-120b"
)

parser = StrOutputParser()

joke = RunnableSequence(
    prompt,
    model,
    parser
)

parallel_chain = RunnableParallel(
    joke=RunnablePassthrough(),
    word_count=runnable_lambda
)

final_chain = RunnableSequence(
    joke,
    parallel_chain
)

print(final_chain.invoke({"topic": "dogs"}))