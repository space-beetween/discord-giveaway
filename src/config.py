from pathlib import Path

import yaml

from .core.metaclasses import SingletonMeta


class Config(metaclass=SingletonMeta):
    def __init__(self, **kwds) -> None:
        self.__dict__.update(kwds)

    @classmethod
    def from_path(cls, path: Path) -> "Config":
        data = yaml.load(path.read_text("utf-8"), yaml.FullLoader)
        if data is None:
            raise Exception("config not found")

        return cls(**data)


Config.from_path(Path("config.yml"))
