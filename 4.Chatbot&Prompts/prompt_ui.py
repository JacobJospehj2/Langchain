from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
model = ChatOpenAI(model="gpt-3.5-turbo")
st.header('Genie')

user_input = st.text_input('I can grant you 3 wishes')

if st.button('First wish'):
    result = model.invoke(user_input)
    st.write(result.content)

