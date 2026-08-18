from unittest import result
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate 
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

prompt = PromptTemplate(
    template= 'Generate a report on {topic}',
    input_variables=['topic']
)

model = ChatOpenAI()

prompt2 =PromptTemplate(
    template='Analyze the report and give me 5 pointers {text}',
    input_variables=['text']
)

parser = StrOutputParser()

chain =prompt|model|parser|prompt2|model|parser

result = chain.invoke({'topic':'Controversy against footballers'})

print(result)

#chain.get_graph().print_ascii()