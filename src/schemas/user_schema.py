from pydantic import BaseModel

class UserCreateSchema(BaseModel):
    name: str
    email: str
    phone: str
    password: str

    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True