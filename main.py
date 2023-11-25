from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langserve import add_routes
#import uvicorn
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Setup for web searcher 
RESULTS_PER_QUESTION = 3
search = DuckDuckGoSearchAPIWrapper()

# Search the web for a given query num_results times
def web_searcher(query: str, num_results: int = RESULTS_PER_QUESTION): 
    results = search.results(query, num_results)
    return [r["link"] for r in results]

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

# Function to scrape text of given website 
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

# Chain to scrape page data and summarize using a ChaptGPT Model
scrape_and_summarize_chain = RunnablePassthrough.assign(
    # Scrape the first 10000 lines of text from the given url.
    text=lambda page_content: scrape_text(page_content["url"])[:10000]
) | prompt | ChatOpenAI(model="gpt-3.5-turbo-1106") | StrOutputParser() 

# Chain to search for external information using user input
chain = RunnablePassthrough.assign(
    urls = lambda x: web_searcher(x["question"])
) | (lambda x: [{"question": x["question"], "url": u} for u in x["urls"]]) | scrape_and_summarize_chain.map()

# Invoke the chain
response = chain.invoke(
    {
        "question": "What is Pydantic?",
    }
)

print(response)
