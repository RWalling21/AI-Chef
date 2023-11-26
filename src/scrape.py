from langchain.utilities import DuckDuckGoSearchAPIWrapper
from bs4 import BeautifulSoup
import requests

# Setup for web searcher 
RESULTS_PER_QUESTION = 3
search = DuckDuckGoSearchAPIWrapper()

def web_searcher(query: str, num_results: int = RESULTS_PER_QUESTION): 
    results = search.results(query, num_results)
    return [r["link"] for r in results]

# Function to scrape text of given website 
def scrape_text(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text(separator=" ", strip=True)[:10000]
            if type(page_text) == None:
                raise Exception("No page text scrapable")
            return page_text
    except Exception as E:
        print(E)
        return f"Failed to retrieve the webpage: Status Code {response.status_code}"