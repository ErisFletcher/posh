from json import dump, load
from pathlib import Path
from typing import Any, Self

from loguru import logger

from ..colours import TextStyle, add_styles


class ColourConfig:
    def __init__(
        self,
        time: str | None = None,
        current_path: str | None = None,
        user_name: str | None = None,
        directory_path: str | None = None,
        file_path: str | None = None,
        errors: str | None = None,
    ) -> None:
        # if anything is None it should use the default
        defaults = self.get_defaults()
        self.time = self.parse_string(time) or defaults[0]
        self.current_path = self.parse_string(current_path) or defaults[1]
        self.username = self.parse_string(user_name) or defaults[2]
        self.directory_path = self.parse_string(directory_path) or defaults[3]
        self.file_path = self.parse_string(file_path) or defaults[4]
        self.errors = self.parse_string(errors) or defaults[5]

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.time}, {self.current_path}, {self.username}, "
            f"{self.directory_path}, {self.file_path}, {self.errors}"
        )

    @staticmethod
    def get_defaults() -> (
        tuple[TextStyle, TextStyle, TextStyle, TextStyle, TextStyle, TextStyle]
    ):
        # define all default colours here
        return (
            TextStyle.WHITE,
            TextStyle.LIGHT_BLUE,
            TextStyle.WHITE,
            TextStyle.LIGHT_CYAN,
            TextStyle.GREEN,
            TextStyle.LIGHT_RED,
        )

    def set_default(self) -> None:
        (
            self.time,
            self.current_path,
            self.username,
            self.directory_path,
            self.file_path,
            self.errors,
        ) = self.get_defaults()

    def parse_string(self, string: str | None) -> TextStyle | None:
        if string is None:
            return None

        if not hasattr(TextStyle, string):
            print(add_styles(f"Error: invalid colour {string!r}", self.errors))
            return None

        return getattr(TextStyle, string)


class Config:
    def __init__(
        self,
        path: Path | None = None,
        show_time: bool | None = None,
        show_username: bool | None = None,
        record_history: bool | None = None,
        shorten_path: bool | None = None,
        shortened_path_length: int | None = None,
        colours: dict[str, str] | None = None,
        aliases: dict[str, str] | None = None,
    ) -> None:
        # if anything is None it should use the default
        defaults = self.get_defaults()
        self.path = path
        self.show_time = show_time if show_time is not None else defaults[0]
        self.show_username = show_username if show_username is not None else defaults[1]
        self.record_history = (
            record_history if record_history is not None else defaults[2]
        )
        self.shorten_path = shorten_path if shorten_path is not None else defaults[3]
        self.shortened_path_length = shortened_path_length or defaults[4]
        self.colours = ColourConfig(**colours) if colours is not None else defaults[5]
        self.aliases = aliases if aliases is not None else defaults[6]

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.path!r}, {self.show_time}, {self.show_username}, "
            f"{self.record_history}, {self.shorten_path}, {self.shortened_path_length}, "
            f"{self.colours!r}, {self.aliases!r})"
        )

    @classmethod
    def from_json(cls, path: Path) -> Self:
        try:
            with open(path, "r", encoding="utf8") as file:
                data: dict[Any, Any] = load(file)
        except OSError as err:
            logger.error(f"failed to open config file @ {path!r}, {err=!r}")
            return cls(path)

        try:
            return cls(path, **data)
        except TypeError as err:
            self = cls(path)
            logger.error(f"failed to create config with {data!r}, {err=!r}")
            print(add_styles("Error: invalid config", self.colours.errors))
            return self

    @staticmethod
    def get_defaults() -> (
        tuple[bool, bool, bool, bool, int, ColourConfig, dict[str, str]]
    ):
        # define all defaults for this class here
        return (True, True, True, True, 40, ColourConfig(), {})

    def set_defaults(self) -> None:
        (
            self.show_time,
            self.show_username,
            self.record_history,
            self.shorten_path,
            self.shortened_path_length,
            self.colours,
            self.aliases,
        ) = self.get_defaults()

    def as_dict(self) -> dict[str, Any]:
        return {
            "show_time": self.show_time,
            "show_username": self.show_username,
            "record_history": self.record_history,
            "shorten_path": self.shorten_path,
            "shortened_path_length": self.shortened_path_length,
            "colours": {
                "time": self.colours.time.name,
                "current_path": self.colours.current_path.name,
                "user_name": self.colours.username.name,
                "directory_path": self.colours.directory_path.name,
                "file_path": self.colours.file_path.name,
                "errors": self.colours.errors.name,
            },
            "aliases": {**self.aliases},
        }

    def write_to_json(self) -> None:
        if self.path is None:
            return

        try:
            with open(self.path, "w", encoding="utf8") as file:
                dump(self.as_dict(), file, indent=4)
        except OSError as err:
            logger.error(f"failed to save config, {err}")
            print(add_styles("failed to save config", self.colours.errors))
