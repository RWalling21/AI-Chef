from langserve import add_routes
import uvicorn
from fastapi import FastAPI

# Langserve Web Server
app = FastAPI(
  title="LangChain Server",
  version="1.0",
  description="A simple api server using Langchain's Runnable interfaces",
)

# Import Chain
from .main import chain
add_routes(
    app,
    chain,
    path="/educator",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)