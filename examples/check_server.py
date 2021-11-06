"""
A tutorial on the use of commands.

This example is based on the
[second bubbletea tutorial](https://github.com/charmbracelet/bubbletea/tree/master/tutorials/commands).
"""


from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from typing import Optional, Text

import requests

import kay

URL = "https://httpstat.us/418"


@dataclass
class StatusMessage(kay.Message):
    """A message that indicates the status of the server."""

    status: int
    reason: Text


@dataclass
class ErrorMessage(kay.Message, Exception):
    """A message that indicates an error."""

    error: Exception


def check_server() -> Optional[kay.Message]:
    """
    Make a request to the server and report the status code.

    This function is a command that can be executed by kay. A command is any function
    that performs some action and returns an optional message about its result.
    Returning `None` is also OK and means that the command has silently finished
    (useful when notifying back is not necessary).

    We return a message representing the error instead of raising it, because this way
    we ensure that the error is reported to the user through our UI.
    """
    try:
        res = requests.get(URL)
    except Exception as error:
        return ErrorMessage(error=error)
    return StatusMessage(status=res.status_code, reason=res.reason)


@dataclass
class Model(kay.Model):
    """
    Make an HTTP request to a server and reports the status code of the response.

    We need to store the status code of the HTTP response and a possible error.
    """

    status: Optional[int] = None
    reason: Optional[Text] = None
    error: Optional[Exception] = None

    def init(self) -> Optional[kay.Command]:
        """
        Initialize the model.

        This function is called when the application starts. It returns the command we
        made earlier. **We don't call it, just return it.**
        """
        return check_server

    def update(self, message: kay.Message) -> Optional[kay.Command]:
        """
        Update the model.

        Commands are executed asynchronously and the messages they return are passed to
        this function for handling.
        """
        if isinstance(message, StatusMessage):
            self.status = message.status
            self.reason = message.reason
        elif isinstance(message, ErrorMessage):
            self.error = message.error
            return kay.quit
        elif isinstance(message, kay.KeyMessage):
            if Text(message) in {"ctrl+c", "q"}:
                return kay.quit
        return None

    def view(self) -> Text:
        """Look at the current model and build a string accordingly."""
        if self.error:
            return f"\nWe had some trouble: {self.error}\n\n"
        s = f"Checking {URL} ... "
        if self.status is not None:
            s += f"{self.status} {self.reason}!"
        return s


async def main() -> None:
    """
    Run the application.

    This creates a new application that receives our initial model and starts the
    event loop.
    """
    p = kay.Program(Model())
    try:
        await p.start()
    except Exception as err:
        print(f"Uh oh, there was an error: {err}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())