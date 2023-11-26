from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langserve import add_routes
import uvicorn
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
import os

# Set OpenAI API Key 
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# Setup for web searcher 
RESULTS_PER_QUESTION = 3
search = DuckDuckGoSearchAPIWrapper()

# Search the web for a given query num_results times
def web_searcher(query: str, num_results: int = RESULTS_PER_QUESTION): 
    results = search.results(query, num_results)
    return [r["link"] for r in results]

# Prompt Definition
# Summary 
SUMMARY_PROMPT  = """{text}

------------

Using the above text, answer in short the following question: 

> {question}

------------
If the question cannot be answered using the text, you MUST simply summarize the text. Include all factual information, numbers, stats etc if available."""

summary_prompt = ChatPromptTemplate.from_template(SUMMARY_PROMPT)

# Search 
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

# Educate 
WRITER_SYSTEM_PROMPT = """You are a helpful AI tutor who is a master of all subjects dedicated to helping students learn and understand various topics in a friendly and focused manner. 
Your sole purpose is to provide well written and clear explanations about a given quest that empower students to grasp complex concepts. 
"""

EDUCATOR_PROMPT = """Information:
------------
{search_summary}
------------

Using the above information, answer the following question or topic: "{question}" in a detailed manor, citing your sources and elaborating on important points. -- \
Your explanation should focus on the answer to the question, should be well structured, informative, in depth, -
with facts and numbers if available and a minimum of 600 words. While your answer should be detailed, it should also be friendly 
and imformative to a wide audience. 

You should strive to write your explanations as long as necessary to cover all relevant and necessary information summarized. 
you MUST write your explanation with markdown syntax.
YOU MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless commentary on the topic. 
Write all used source urls at the end of your explanation, and DO NOT add duplicated sources
Please do your best, this is going into a data sensitive application and is very important to my career
"""

educate_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", WRITER_SYSTEM_PROMPT),
        ("user", EDUCATOR_PROMPT),
    ]
)

# Function to scrape text of given website 
def scrape_text(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text(separator=" ", strip=True)
            if type(page_text) == None:
                raise Exception("No page text scrapable")
            return page_text
    except Exception as E:
        print(E)
        return f"Failed to retrieve the webpage: Status Code {response.status_code}"

# Given a list_of_lists collapse into a single list
def collapse_list_of_lists(list_of_lists):
    content = []
    for l in list_of_lists:
        content.append("\n\n".join(l))
    return "\n\n".join(content)


# Chain definitions
# Chain to scrape page data and summarize using a ChaptGPT Model
scrape_and_summarize_chain = RunnablePassthrough.assign(
    # Summary is the chain below
    summary=RunnablePassthrough.assign(
    # Scrape the first 10000 lines of text from the given url.
    text=lambda page_content: (page_content, scrape_text(page_content["url"]))[1][:10000]
) | summary_prompt | ChatOpenAI(model="gpt-3.5-turbo-1106") | StrOutputParser() 
# Adding the URL to the context makes it easier for the model to cite sources 
) | (lambda input: f"URL: {input['url']}\n\nSUMMARY: {input['summary']}") 

# Chain to search for external information using user input
web_search_chain = RunnablePassthrough.assign(
    urls = lambda input: web_searcher(input["question"])
) | (lambda input: [{"question": input["question"], "url": u} for u in input["urls"]]) | scrape_and_summarize_chain.map()

# Chain to generate search queries for the given question
search_question_chain = search_prompt | ChatOpenAI(temperature=1) | StrOutputParser() | (lambda response: json.loads(response))

# Researches given topic and summarizes based off results 
research_chain = search_question_chain | (lambda input: [{"question": q} for q in input]) | web_search_chain.map()

# Main chain 
chain = RunnablePassthrough.assign(
    search_summary= research_chain | collapse_list_of_lists
) | educate_prompt | ChatOpenAI(model="gpt-3.5-turbo-1106") | StrOutputParser() 

# Langserve Web Server
app = FastAPI(
  title="LangChain Server",
  version="1.0",
  description="A simple api server using Langchain's Runnable interfaces",
)

add_routes(
    app,
    chain,
    path="/educator",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
