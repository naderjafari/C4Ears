from pydantic import BaseModel


class TaskRequest(BaseModel):
    task: str


class ResultRequest(BaseModel):
    request_id: str
    result: str
