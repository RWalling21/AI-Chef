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
import json
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

summary_prompt = ChatPromptTemplate.from_template(SUMMARY_PROMPT)

search_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "user",
            "Write 3 unique google search queries to search online that form an "
            "objective opinion from the following: {question}\n"
            "Your Output MUST BE IN PROPER JSON FORMAT as it will be read by a json.loads()"
            "You must respond with a list of strings in the following format: "
            '["query 1", "query 2", "query 3"].',
        ),
    ]
)

# Function to scrape text of given website 
def scrape_text(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text(separator=" ", strip=True)
            return page_text
    except Exception as E:
        print(E)
        return f"Failed to retrieve the webpage: Status Code {response.status_code}"
    
url = "https://docs.pydantic.dev/latest/"

#  Chain definition

# Chain to scrape page data and summarize using a ChaptGPT Model
scrape_and_summarize_chain = RunnablePassthrough.assign(
    # Scrape the first 10000 lines of text from the given url.
    text=lambda page_content: (page_content, scrape_text(page_content["url"]))[1][:10000]
) | summary_prompt | ChatOpenAI(model="gpt-3.5-turbo-1106") | StrOutputParser() 

# Chain to search for external information using user input
web_search_chain = RunnablePassthrough.assign(
    urls = lambda input: web_searcher(input["question"])
) | (lambda input: [{"question": input["question"], "url": u} for u in input["urls"]]) | scrape_and_summarize_chain.map()

# Chain to generate search queries for the given question
search_question_chain = search_prompt | ChatOpenAI(temperature=1) | StrOutputParser() | (lambda response: json.loads(response))

# Main chain 
chain = search_question_chain | (lambda input: [{"question": q} for q in input]) | web_search_chain.map()

# Invoke the chain
response = chain.invoke(
    {
        "question": "What is the difference between special, and general relativity",
    }
)

# Print Output
print(response[0])
