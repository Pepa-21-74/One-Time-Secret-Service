from pydantic import BaseModel, ConfigDict

class KeyBase(BaseModel):
    key: str 
    password: str | None = None

class KeyAdd(KeyBase):
    pass
