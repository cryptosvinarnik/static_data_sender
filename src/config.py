import yaml
from pydantic import BaseModel


class Config(BaseModel):
    CONTRACT: str
    INPUT_DATA: str
    RPC: str
    WORKERS_COUNT: int
    SLEEP_BETWEEN_ACCOUNT_WORK: list[int]
    GAS_TARGET: float | int
    VALUE: int | float


def load_config() -> Config:
    with open("./src/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    return Config.parse_obj(config)
