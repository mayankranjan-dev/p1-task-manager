from fastapi import FastAPI

import models
from database import engine
from routers import auth_router, task_router

# no migrations here, create_all is enough for a project this size
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager", version="0.1.0")

app.include_router(auth_router.router)
app.include_router(task_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}
