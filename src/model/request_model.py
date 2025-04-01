from pydantic import BaseModel,EmailStr

class QueryRequest(BaseModel):
    query: str

class EmailSchema(BaseModel):
    recipient: EmailStr
    subject: str
    body: str