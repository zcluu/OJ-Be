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


class ProblemForm(BaseModel):
    title: str
    description: str
    inputs: str
    outputs: str
    samples: str
    hints: str
    source: str
    is_spj: str
    test_id: str
    time_limit: str
    memory_limit: str
    io_mode: str
    status: str


class JudgeForm(BaseModel):
    problem_id: str
    language: str
    source_code: str
