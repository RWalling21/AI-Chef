#!/usr/bin/env python
import uvicorn
from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough 
from langserve import add_routes
from dotenv import load_dotenv
import os

# Set OpenAI API Key 
load_dotenv()
OEPNAI_KEY = os.getenv("OPENAI_API_KEY")

# Prompt Definition
from langchain.prompts import ChatPromptTemplate
import requests
from bs4 import BeautifulSoup

SUMMARY_PROMPT  = """{text}

------------

Using the above text, answer in short the following question: 

> {question}

------------
If the question cannot be answered useing the text, you MUST simply summarize the text. Include all factual information, numbers, stats etc if available."""

prompt = ChatPromptTemplate.from_template(SUMMARY_PROMPT)

# Handle lookup of content and parsing for use in prompt
def scrape_text(url: str):
    # Send a GET request to the website
    try:
        response = requests.get(url)

        # Check if request was successful 
        if response.status_code == 200:
            # Parse the content of the request with BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract all text from the page
            page_text = soup.get_text(serparator=" ", strip=True)

            #Print the extracted text
            return page_text

    except Exception as E:
        print(E)
        # Handle exception and return the error code of the response
        return f"Failed to retrieve the webpage: Status Code {response.status_code}"
    
    
url = "https://docs.pydantic.dev/latest/"

# 1. Chain definition
chain = RunnablePassthrough( 
    # Scrape the first 10000 characters of the page
    text = lambda page_content: scrape_text(url)[:10000]
 ) | SUMMARY_PROMPT | ChatOpenAI(model="gpt-3.5-turbo-1106") | StrOutputParser() 


chain.invoke(
    {
        "question": "What is Pydantic?",
        "url": url
    }
)

# 2. App definition
app = FastAPI(
  title="Dr. MAC",
  version="1.0",
  description="A simple api server using Langchain's Runnable interfaces",
)

# 3. Adding chain route
add_routes(
    app,
    dr_mac,
    path="/drmac",
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)