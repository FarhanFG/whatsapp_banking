from fastapi import FastAPI

app = FastAPI()

@app.post("/hello")
async def empty_response():
    return {}
