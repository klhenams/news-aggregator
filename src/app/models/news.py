"""Simple news model using dataclasses."""

from dataclasses import dataclass


@dataclass
class News:
    """Simple news dataclass model.

    Attributes:
        headline: The news article headline.
        link: The URL link to the full article.
        source: The news source/provider name.
    """

    headline: str
    link: str
    source: str
