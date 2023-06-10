from pydantic import BaseModel


class LoginForm(BaseModel):
    username: str
    email: str
    password: str


class RegisterForm(BaseModel):
    username: str
    email: str
    password: str
    confirmPassword: str
    code: str
