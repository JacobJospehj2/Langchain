from langchain_core import chat_history
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


chat_template = ChatPromptTemplate([
    ('system','You are a customer care agent'),
    MessagesPlaceholder(variable_name='chat_history'),
    ('human','{query}')
])


chat_history = []

with open('4.Chatbot&Prompts/chat_history.txt') as f:
    chat_history.extend(f.readline())

prompt = chat_template.invoke({
    'chat_history': chat_history, 
    'query': 'Where is my refund'
})

print(prompt)