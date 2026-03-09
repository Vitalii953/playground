from pydantic import BaseModel, model_validator
from typing import Literal, get_args


languages = Literal["en", "fr"]


class GameSettings(BaseModel):
    """
    Enforce correct settings at runtime
    low-level, managed MAINLY through a database in high-level functions.
    NOT HERE!!!
    """

    current_language: languages = "en"
    # for pydantic validation only
    available_languages: list[languages] = list(get_args(languages))

    @model_validator(mode="after")
    def ensure_correct_language(self) -> "GameSettings":
        if self.current_language not in self.available_languages:
            raise ValueError(f"{self.current_language} is an invalid language")
        return self
