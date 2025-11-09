from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Betting predictor API is live!"}
