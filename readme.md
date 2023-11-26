# WisdomWeaver

## Overview

WisdomWeaver is an advanced Language Learning Model (LLM) chain designed for academic excellence. It offers in-depth, cited insights on complex topics with up-to-date information, leveraging the LangChain framework and OpenAI's models.

## Features

- **Adaptive Learning Algorithms**: Uses ChatOpenAI models for dynamic content delivery.
- **Custom Web Scraping**: Implements methods to gather current information from the web.
- **Interactive Prompts**: Bespoke prompt templates for tailored educational experiences.
- **Comprehensive Summarization**: In-depth summaries with citations for accuracy and relevance.

## Installation

Clone the repository:
```bash
git clone https://github.com/RWalling21/WisdomWeaver.git
cd WisdomWeaver
```

Install necessary packages:
```bash
pip install langchain
pip install fastapi
pip install uvicorn
pip install python-dotenv
pip install requests
pip install beautifulsoup4
```

## Usage 
1. Set your OpenAI API Key in a .env file:
```mkfile 
OPENAI_API_KEY=your_api_key_here
```

2. Start the server:
```bash
cd /src
python serve.py
```
3. The server will run on localhost:8000. Use the /educator/playground endpoint to interact with the system.

## License
This project is under the MIT License.