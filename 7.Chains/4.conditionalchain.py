from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import RunnableParallel,RunnableBranch,RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel,Field
from typing import Literal

load_dotenv()

model = ChatOpenAI()

parser =  StrOutputParser()

class Feedback(BaseModel):
    sentiment: Literal["positive", "negative"] = Field(
        description="Classify the sentiment of the supplied text."
    )

parser2 = PydanticOutputParser(pydantic_object=Feedback)

prompt1 = PromptTemplate(
    template=(
        "Classify the sentiment of the following user input.\n\n"
        "User input: {input}\n\n"
        "{format_instructions}"
    ),
    input_variables=["input"],
    partial_variables={
        "format_instructions": parser2.get_format_instructions()
    },
)

chain = prompt1|model|parser2

#feedback = chain.invoke({'this is so bad'}).sentiment

prompt2 = PromptTemplate.from_template(
    """
The user said: {text}

Their sentiment is positive.
Write a friendly and relevant response.
"""
)

prompt3 = PromptTemplate.from_template(
    """
The user said: {text}

Their sentiment is negative.
Write an empathetic and relevant response.
"""
)

branch_chain = RunnableBranch(
    (lambda x:x.sentiment == 'positive', prompt2|model|parser),
    (lambda x:x.sentiment == 'negative', prompt3|model|parser),
    RunnableLambda(lambda x: "Could not find sentiment")
)

chain_final = chain | branch_chain

output = chain_final.invoke(
    {"input": "Supergirl movie was so ass"}
)

print(output)