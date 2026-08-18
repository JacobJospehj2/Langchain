from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate, prompt
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain.schema.runnable import RunnableSequence

load_dotenv()

prompt  = PromptTemplate(
    template= 'Tell me a joke about {topic}'
    input_types= ['topic']
    )

model = ChatOpenAI()

parser = StrOutputParser()

chain = RunnableSequence(prompt,model,parser)

print(chain.invoke({'topic:Trump'}))
