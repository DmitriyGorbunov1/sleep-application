from pydantic import BaseModel

class StatisticsModel(BaseModel):
    sleep_hours: str
    wakeup_time: str
    bedtime: str
    fastsleep_time: str
    slowsleep_time: str
    gotobed_time: str
    sleep_quality: int