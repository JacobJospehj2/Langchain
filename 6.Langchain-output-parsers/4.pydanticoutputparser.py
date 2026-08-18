from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()

model = ChatOpenAI()


class Facts(BaseModel):
    Fact1: str = Field(description='Random fact of topic')
    Fact2: str = Field(description='Random fact of topic')
    Fact3: str = Field(description='Random fact of topic')


parser = PydanticOutputParser(pydantic_object=Facts)

template = PromptTemplate(
    template='give me 3 facts about {topic} \n {format_instruction}',
    input_variables=['topic'],
    partial_variables={'format_instruction': parser.get_format_instructions()}
)

chain = template | model| parser

result = chain.invoke({'topic': 'love'})

print(result)
