import datetime

from pydantic import BaseModel


class LoginForm(BaseModel):
    username: str
    password: str


class RegisterForm(BaseModel):
    username: str
    email: str
    password: str
    confirmPassword: str
    code: str


class ProblemForm(BaseModel):
    cid: str = ''
    id: int = -1
    title: str
    description: str
    inputs: str
    outputs: str
    samples: list
    language: list
    mode: int
    is_spj: bool
    source: str
    time_limit: int
    memory_limit: int
    hints: str
    test_id: str


class JudgeForm(BaseModel):
    pid: str
    language: str
    source_code: str
    cp_id: str = ''


class ContestForm(BaseModel):
    id: int = -1
    title: str
    description: str
    start_at: str
    end_at: str
    contest_type: int
    password: str
    only_id: str
    rule: int
