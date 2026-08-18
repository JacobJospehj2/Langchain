from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate, prompt 
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableParallel

load_dotenv()

model1 = ChatOpenAI()

model2 = ChatOpenAI()

prompt1 = PromptTemplate(
    template='Give me a very short history/information about {topic}',
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template='Analyze the following topic and tell me if this influenced mordern culture and if so list them {text}',
    input_variables=['text']
)

prompt3 = PromptTemplate(
    template = 'Based on the notes and the pointers make a single document {notes} and {pointers}',
    input_variables=['notes','pointers']
)

parser = StrOutputParser()

parallel_chain = RunnableParallel({
    'notes': prompt1|model1,
    'pointers': prompt2|model2
})

merge_chain = prompt3|model1|parser

chain = parallel_chain|merge_chain

result = chain.invoke({'topic': 'Greek Mythology'})

print(result)