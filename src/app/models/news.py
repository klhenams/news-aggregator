from dataclasses import dataclass


@dataclass
class News:
    headline: str
    link: str
    source: str