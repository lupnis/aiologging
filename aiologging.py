# -*- coding: utf-8 -*-
import aiofiles
from copy import deepcopy
import datetime
import os
import sys
import re
from asyncio import Lock
from filelock import AsyncFileLock
from typing import Any, Dict, Union, List


class Styles(object):
    """ANSI escape codes for styling terminal output."""
    CLEAR = 0
    BOLD = 1
    BOLD_RESET = 22
    FAINT = 2
    FAINT_RESET = 22
    ITALIC = 3
    ITALIC_RESET = 23
    UNDERLINE = 4
    UNDERLINE_RESET = 24
    BLINK = 5
    BLINK_RESET = 25
    REVERSE = 7
    REVERSE_RESET = 27
    INVISIBLE = 8
    INVISIBLE_RESET = 28
    STRIKE = 9
    STRIKE_RESET = 29
    DEFAULT = 39
    DEFAULT_BG = 49
    BLACK = 30
    BLACK_BG = 40
    RED = 31
    RED_BG = 41
    GREEN = 32
    GREEN_BG = 42
    YELLOW = 33
    YELLOW_BG = 43
    BLUE = 34
    BLUE_BG = 44
    MAGENTA = 35
    MAGENTA_BG = 45
    CYAN = 36
    CYAN_BG = 46
    WHITE = 37
    WHITE_BG = 47
    BRIGHT_BLACK = 90
    BRIGHT_BLACK_BG = 100
    BRIGHT_RED = 91
    BRIGHT_RED_BG = 101
    BRIGHT_GREEN = 92
    BRIGHT_GREEN_BG = 102
    BRIGHT_YELLOW = 93
    BRIGHT_YELLOW_BG = 103
    BRIGHT_BLUE = 94
    BRIGHT_BLUE_BG = 104
    BRIGHT_MAGENTA = 95
    BRIGHT_MAGENTA_BG = 105
    BRIGHT_CYAN = 96
    BRIGHT_CYAN_BG = 106
    BRIGHT_WHITE = 97
    BRIGHT_WHITE_BG = 107

    @staticmethod
    def ID_COLOR(id):
        """Generate ANSI escape code for 256-color mode.

        :param id: Color ID (0-255)
        :return: ANSI escape code for the color
        """

        return f"38;5;{id}"

    @staticmethod
    def ID_COLOR_BG(id):
        """Generate ANSI escape code for 256-color mode background.

        :param id: Color ID (0-255)
        :return: ANSI escape code for the background color
        """

        return f"48;5;{id}"

    @staticmethod
    def RGB_COLOR(r, g, b):
        """Generate ANSI escape code for RGB color.

        :param r: Red component (0-255)
        :param g: Green component (0-255)
        :param b: Blue component (0-255)
        :return: ANSI escape code for the RGB color
        """

        return f"38;2;{r};{g};{b}"

    @staticmethod
    def RGB_COLOR_BG(r, g, b):
        """Generate ANSI escape code for RGB color background.

        :param r: Red component (0-255)
        :param g: Green component (0-255)
        :param b: Blue component (0-255)
        :return: ANSI escape code for the background RGB color
        """

        return f"48;2;{r};{g};{b}"

    @staticmethod
    def make_color_prefix(code):
        """Generate ANSI escape code prefix.

        :param code: ANSI escape code
        :return: String with ANSI escape code prefix
        """

        return f"\x1b[{code}m"

    @staticmethod
    def make_colors_prefix(codes: List[Any] = []):
        """Generate ANSI escape codes for multiple styles.

        :param codes: List of ANSI escape codes
        :return: String with ANSI escape codes
        """
        return ''.join([Styles.make_color_prefix(code) for code in codes])


class Styled(object):
    """Styled class to handle styled strings."""

    def __init__(self, data: Any = "", *styles: Any):
        """Styled class to handle styled strings.

        :param data: Data to be styled, can be a string or any other type
        :param styles: Styles to be applied to the string
        """

        self.plain_str = data.plain_str if isinstance(
            data, Styled) else str(data)
        splited_str = re.split(r'(\{\{*[\w\W]*?\}*\})', str(data))
        self.styled_str = Styles.make_color_prefix(Styles.CLEAR) + ''.join([(Styles.make_colors_prefix(
            styles) + s) if i % 2 == 0 else s for i, s in enumerate(splited_str)]) + Styles.make_color_prefix(Styles.CLEAR)

    def __add__(self, other):
        """Concatenate two Styled objects or a Styled object with a string.

        :param other: Other Styled object or string to be concatenated
        :return: New Styled object with concatenated strings
        """

        generated_style = Styled()
        if isinstance(other, Styled):
            generated_style.plain_str = self.plain_str + other.plain_str
            generated_style.styled_str = self.styled_str + other.styled_str
        else:
            generated_style.plain_str = self.plain_str + str(other)
            generated_style.styled_str = self.styled_str + str(other)
        return generated_style

    def __radd__(self, other):
        """Concatenate a string with a Styled object.

        :param other: String to be concatenated with Styled object
        :return: New Styled object with concatenated strings
        """

        generated_styled = Styled()
        if isinstance(other, Styled):
            generated_styled.plain_str = other.plain_str + self.plain_str
            generated_styled.styled_str = other.styled_str + self.styled_str
        else:
            generated_styled.plain_str = str(other) + self.plain_str
            generated_styled.styled_str = str(other) + self.styled_str
        return generated_styled

    def __iadd__(self, other):
        """In-place concatenation of Styled object with another Styled object or string.

        :param other: Other Styled object or string to be concatenated
        :return: Self, with concatenated strings
        """

        if isinstance(other, Styled):
            self.plain_str += other.plain_str
            self.styled_str += other.styled_str
        else:
            self.plain_str += str(other)
            self.styled_str += str(other)
        return self

    @property
    def plain(self) -> str:
        """Get the plain string representation of the Styled object.

        :return: Plain string representation
        """

        return self.plain_str

    @property
    def styled(self) -> str:
        """Get the styled string representation of the Styled object.

        :return: Styled string representation
        """

        return self.styled_str

    def __str__(self) -> str:
        """Get the string representation of the Styled object.

        :return: Styled string representation
        """

        return self.styled_str

    def format(self, *args, **kwargs):
        """Format the styled string with given arguments.

        :param args: Positional arguments for formatting
        :param kwargs: Keyword arguments for formatting
        :return: Formatted Styled object
        """

        generated_styled = Styled()
        args_plain = [arg.plain if isinstance(
            arg, Styled) else str(arg) for arg in args]
        kwargs_plain = {k: v.plain if isinstance(
            v, Styled) else str(v) for k, v in kwargs.items()}
        args_styled = [arg.styled if isinstance(
            arg, Styled) else str(arg) for arg in args]
        kwargs_styled = {k: v.styled if isinstance(
            v, Styled) else str(v) for k, v in kwargs.items()}
        generated_styled.plain_str = self.plain_str.format(
            *args_plain, **kwargs_plain)
        generated_styled.styled_str = self.styled_str.format(
            *args_styled, **kwargs_styled)
        return generated_styled


class Levels(object):
    DEBUG = 0
    INFO = 1
    NOTICE = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


class LoggerConfig(object):
    DEFAULT_CONFIG = {
        "print": {
            "enabled": True,
            "colored": True,
            "log_level": Levels.DEBUG,
            "time": {
                "enabled": True,
                "time_format": "%Y-%m-%d %H:%M:%S",
                "time_styles": [Styles.BRIGHT_BLACK],
                "time_quote_format": "[{}]",
                "time_quote_styles": []
            },
            "level": {
                "enabled": True,
                "levels": {
                    str(Levels.DEBUG): {
                        "text": "D",
                        "styles": [Styles.BRIGHT_BLACK]
                    },
                    str(Levels.INFO): {
                        "text": "I",
                        "styles": []
                    },
                    str(Levels.NOTICE): {
                        "text": "N",
                        "styles": [Styles.BOLD]
                    },
                    str(Levels.WARNING): {
                        "text": "W",
                        "styles": [Styles.YELLOW]
                    },
                    str(Levels.ERROR): {
                        "text": "E",
                        "styles": [Styles.RED]
                    },
                    str(Levels.CRITICAL): {
                        "text": "C",
                        "styles": [Styles.RED, Styles.BOLD, Styles.BLINK]
                    }
                }
            }
        },
        "file": {
            "enabled": True,
            "colored": False,
            "log_level": Levels.DEBUG,
            "log_root_path": "./logs",
            "log_name": "log.",
            "log_suffix": "txt",
            "log_append_time": True,
            "log_time_format": "%Y-%m-%d",
            "flush_every_n_logs": 0,
            "time": {
                "enabled": True,
                "time_format": "%Y-%m-%d %H:%M:%S",
                "time_styles": [Styles.BRIGHT_BLACK],
                "time_quote_format": "[{}]",
                "time_quote_styles": []
            },
            "level": {
                "enabled": True,
                "levels": {
                    str(Levels.DEBUG): {
                        "text": "DEBUG",
                        "styles": [Styles.BRIGHT_BLACK]
                    },
                    str(Levels.INFO): {
                        "text": "INFO",
                        "styles": []
                    },
                    str(Levels.NOTICE): {
                        "text": "NOTICE",
                        "styles": [Styles.BOLD]
                    },
                    str(Levels.WARNING): {
                        "text": "WARN",
                        "styles": [Styles.YELLOW]
                    },
                    str(Levels.ERROR): {
                        "text": "ERROR",
                        "styles": [Styles.RED]
                    },
                    str(Levels.CRITICAL): {
                        "text": "CRIT",
                        "styles": [Styles.RED, Styles.BOLD, Styles.BLINK]
                    }
                }
            }
        }
    }


class Logger(object):
    """Logger class to handle logging to console and file."""

    def __init__(self, config: Dict[str, Any] = LoggerConfig.DEFAULT_CONFIG, **kwargs):
        """Initialize the Logger class with given configuration.

        :param config: Configuration for the logger, default is LoggerConfig.DEFAULT_CONFIG
        :param kwargs: Additional configuration options
        """

        self.config = {**deepcopy(config), **kwargs}
        if self.config.get("file", {}).get("enabled", False):
            os.makedirs(self.config["file"].get(
                "log_root_path", "./logs"), exist_ok=True)
        self.log_buffer = []
        self._lock = Lock()
        self._filelock = AsyncFileLock("{}/{}{}.lock".format(
            self.config["file"]["log_root_path"],
            self.config["file"]["log_name"],
            datetime.datetime.now().strftime(
                self.config["file"]["log_time_format"]) if self.config["file"]["log_append_time"] else ''
        ), timeout=10)

    async def log(self, level: Levels, text: Union[Styled, Any], *args, **kwargs):
        """Log a message with the given level and text.

        :param level: Logging level (DEBUG, INFO, NOTICE, WARNING, ERROR, CRITICAL)
        :param text: Text to be logged, can be a Styled object or any other type
        :param args: Positional arguments for formatting the text
        :param kwargs: Keyword arguments for formatting the text
        """

        text = Styled(text)
        if len(args) or len(kwargs):
            text = text.format(*args, **kwargs)
        if self.config["print"]["enabled"] and level >= self.config["print"]["log_level"]:
            prefix = self._make_prefix_s(level, "print")
            ostr = "{}{}".format(
                str(prefix) if self.config["print"]["colored"] else prefix.plain,
                str(text) if self.config["print"]["colored"] else text.plain
            )
            if level < Levels.ERROR:
                sys.stdout.write(ostr + "\n")
                sys.stdout.flush()
            else:
                sys.stderr.write(ostr + "\n")
                sys.stderr.flush()

        if self.config["file"]["enabled"] and level >= self.config["file"]["log_level"]:
            prefix = self._make_prefix_s(level, "file")
            ostr = "{}{}".format(
                str(prefix) if self.config["file"]["colored"] else prefix.plain,
                str(text) if self.config["file"]["colored"] else text.plain
            )
            async with self._lock:
                self.log_buffer.append(ostr)
                await self._check_flush()

    async def debug(self, text: Union[Styled, Any], *args, **kwargs):
        """Log a debug message.

        :param text: Text to be logged, can be a Styled object or any other type
        :param args: Positional arguments for formatting the text
        :param kwargs: Keyword arguments for formatting the text
        """

        await self.log(Levels.DEBUG, text, *args, **kwargs)

    async def info(self, text: Union[Styled, Any], *args, **kwargs):
        """Log an info message.

        :param text: Text to be logged, can be a Styled object or any other type
        :param args: Positional arguments for formatting the text
        :param kwargs: Keyword arguments for formatting the text
        """

        await self.log(Levels.INFO, text, *args, **kwargs)

    async def notice(self, text: Union[Styled, Any], *args, **kwargs):
        """Log a notice message.

        :param text: Text to be logged, can be a Styled object or any other type
        :param args: Positional arguments for formatting the text
        :param kwargs: Keyword arguments for formatting the text
        """

        await self.log(Levels.NOTICE, text, *args, **kwargs)

    async def warning(self, text: Union[Styled, Any], *args, **kwargs):
        """Log a warning message.

        :param text: Text to be logged, can be a Styled object or any other type
        :param args: Positional arguments for formatting the text
        :param kwargs: Keyword arguments for formatting the text
        """

        await self.log(Levels.WARNING, text, *args, **kwargs)

    async def error(self, text: Union[Styled, Any], *args, **kwargs):
        """Log an error message.

        :param text: Text to be logged, can be a Styled object or any other type
        :param args: Positional arguments for formatting the text
        :param kwargs: Keyword arguments for formatting the text
        """

        await self.log(Levels.ERROR, text, *args, **kwargs)

    async def critical(self, text: Union[Styled, Any], *args, **kwargs):
        """Log a critical message.

        :param text: Text to be logged, can be a Styled object or any other type
        :param args: Positional arguments for formatting the text
        :param kwargs: Keyword arguments for formatting the text
        """

        await self.log(Levels.CRITICAL, text, *args, **kwargs)

    def _make_time_s(self, source="print"):
        return Styled(self.config[source]["time"]["time_quote_format"], *self.config[source]["time"]["time_quote_styles"]).format(
            Styled(datetime.datetime.now().strftime(
                self.config[source]["time"]["time_format"]), *self.config[source]["time"]["time_styles"])
        )

    def _make_level_s(self, level, source="print"):
        return Styled(self.config[source]["level"]["levels"][str(level)]["text"], *self.config[source]["level"]["levels"][str(level)]["styles"])

    def _make_prefix_s(self, level, source="print", sep=" "):
        return Styled("{}{}{}{}").format(
            self._make_time_s(source) if self.config[source]["time"]["enabled"] else '', sep, self._make_level_s(
                level, source) if self.config[source]["level"]["enabled"] else '', sep
        )

    async def _check_flush(self):
        if len(self.log_buffer) > self.config["file"]["flush_every_n_logs"]:
            await self._flush_now()

    async def _flush_now(self):
        fpath = "{}/{}{}.{}".format(
            self.config["file"]["log_root_path"],
            self.config["file"]["log_name"],
            datetime.datetime.now().strftime(
                self.config["file"]["log_time_format"]) if self.config["file"]["log_append_time"] else '',
            self.config["file"]["log_suffix"]
        )
        try:
            async with self._filelock:
                async with aiofiles.open(fpath, "a", encoding="utf-8") as f:
                    for log in self.log_buffer:
                        await f.write(f"{log}\n")
                self.log_buffer.clear()
        except Exception as e:
            sys.stderr.write(
                f"Errors occurred while attempting to flush logs to file {fpath} : {e}"
            )
            raise RuntimeError(
                f"Errors occurred while attempting to flush logs to file {fpath} : {e}"
            ) from e
