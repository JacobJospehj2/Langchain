from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate

load_dotenv()

model = ChatOpenAI()

template1 = PromptTemplate(
    template='Write a detailed report on {topic}',
    input_variables=['topic']
)

template2 = PromptTemplate(
    template='Write a summary on {subject}',
    input_variables=['subject']
)

# Step 1: Generate the report
prompt1 = template1.invoke({'topic': 'solar system'})
result = model.invoke(prompt1)

# Step 2: Generate the summary based on the report
prompt2 = template2.invoke({'subject': result.content})
result1 = model.invoke(prompt2)

print(result1.content)