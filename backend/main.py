from fastapi import FastAPI
from routers import snippets, tags, collections

app = FastAPI(title="Pin-Up AI Backend")

app.include_router(snippets.router, prefix="/snippets")
app.include_router(tags.router, prefix="/tags")
app.include_router(collections.router, prefix="/collections")

@app.get("/health")
def health():
    return {"status": "ok"}
