from langchain_core.prompts import ChatPromptTemplate

chat_template = ChatPromptTemplate([
    ('system','You are a expert in domain of {domain}'),
    ('human','Explain {topic} like I am a 18 year old')
])

promt = chat_template.invoke({'domain':'Wall street','topic':'Bull'})

print(promt)