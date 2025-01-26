from pydantic import BaseModel


class UploadResponse(BaseModel):
    message: str
    data: dict


class QueryRequest(BaseModel):
    query: str
    user_id: int
