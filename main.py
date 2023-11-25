from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable.passthrough import RunnableAssign 
from langserve import add_routes
import uvicorn
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Set OpenAI API Key 
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# Prompt Definition
SUMMARY_PROMPT  = """{text}

------------

Using the above text, answer in short the following question: 

> {question}

------------
If the question cannot be answered using the text, you MUST simply summarize the text. Include all factual information, numbers, stats etc if available."""

prompt = ChatPromptTemplate.from_template(SUMMARY_PROMPT)

# Function to scrape text
def scrape_text(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text(separator=" ", strip=True)
            return page_text[:10000]
    except Exception as E:
        print(E)
        return f"Failed to retrieve the webpage: Status Code {response.status_code}"
    
url = "https://docs.pydantic.dev/latest/"

# 1. Chain definition
chain = RunnableAssign(
    mapper={
        "text": lambda x: scrape_text(x["url"])[:10000]
    }
) | prompt | ChatOpenAI(model="gpt-3.5-turbo-1106") | StrOutputParser() 

# Invoke the chain
response = chain.invoke(
    {
        "question": "What is Pydantic?",
        "url": url,
    }
)

print(response)
