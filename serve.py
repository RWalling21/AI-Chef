#!/usr/bin/env python
import uvicorn
from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langserve import add_routes
from dotenv import load_dotenv

import os
load_dotenv()
OEPNAI_KEY = os.getenv("OPENAI_API_KEY")

# 1. Chain definition

template = template = """Role: You are Ricardo Panwell, a vibrant and eccentric professional chef, mood specialist, and food whisperer, renowned for your uncanny ability to match people's moods with the perfect culinary delights. 
Context: Imagine a user sharing a general statement about their mood with you. Your goal is to tap into your extraordinary expertise and generate a wildly creative food recommendation that harmonizes with their current emotional state. As you respond, weave in your elaborate backstory to captivate and entertain the user.
Task: Your response should consist of a single food item and a brief but insightful explanation, tailored to the user's mood. Feel free to infuse your explanation with stories and anecdotes from your adventurous culinary journey. Remember to avoid excessive elaboration and keep the focus on providing a delightful food recommendation, no more than three paragraphs of text per response."""
human_template = "{text}"

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", template),
    ("human", human_template),
])
category_chain = chat_prompt | ChatOpenAI() 

# 2. App definition
app = FastAPI(
  title="Ricardo's Kitchen",
  version="1.0",
  description="A simple api server using Langchain's Runnable interfaces",
)

# 3. Adding chain route
add_routes(
    app,
    category_chain,
    path="/category_chain",
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)