# import pydantic models
from pydantic import BaseModel
app={
    "name": "app",
    "versions":[{
        "version": "v1",
        "description": "AI Base Project v1 - Health Check Test",
        "author": "Your Name",
        "dependencies": [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "pydantic",
            "psutil",
            "requests"
        ],
        "status": "active"
    }]

}

class Version(BaseModel):
    major: int = 1
    minor: int = 0
    patch: int = 0

class App(BaseModel):
    name: str = "app"
    versions: list[Version]
    description: str = "Generic application for testing purposes"