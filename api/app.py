from fastapi import FastAPI

app = FastAPI(title = "Smart Requirements Engineer Agents");

@app.get("/")
async def root():
    return {"message": "API is running"}
    
