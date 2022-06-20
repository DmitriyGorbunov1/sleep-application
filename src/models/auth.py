from pydantic import BaseModel


class UserModel(BaseModel):
    email: str
    name: str
    password: str
    goal: int
    age_group: int
    wakeup_time: str
    bedtime: str
    goodsleep_hours: int
    regime_compliance: bool

class LoginModel(BaseModel):
    email: str
    password: str