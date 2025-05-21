from pydantic import BaseModel


class FromAttributes(BaseModel):
    class Config:
        from_attributes = True
