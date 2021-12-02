"""A tutorial on the use of commands."""


from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional, Text

import requests

import cuia

URL = "https://httpstat.us/418"


async def check_server() -> Optional[cuia.Message]:
    """
    Make a request to the server and report the status code.

    This coroutine is a command that can be executed by cuia. A command is any coroutine
    that performs some action and returns an optional message about its result.
    Returning `None` is also OK and means that the command has silently finished
    (useful when notifying back is not necessary).

    We return a message representing the error instead of raising it, because this way
    we ensure that the error is reported to the user through our UI.

    **Note**: what if you need to pass some data to a command? Use a factory function:

    >>> def command_with_arg(id: int) -> Command:
    ...     async def command() -> Optional[cuia.Message]:
    ...         return SomeMessage(id)
    ...     return command

    Then you can call this factory function when you need to get a command.
    """
    try:
        res = requests.get(URL)
        # raise ValueError("This should not happen")
    except Exception as error:
        # It is a good idea to narrow down the error type in production code.
        return ErrorMessage(error=error)
    return StatusMessage(status=res.status_code, reason=res.reason)


@dataclass(frozen=True)
class StatusMessage(cuia.Message):
    """A message that indicates the status of the server."""

    status: int
    reason: Text


@dataclass(frozen=True)
class ErrorMessage(cuia.Message, Exception):
    """A message that indicates an error."""

    error: Exception


@dataclass
class Model(cuia.Model):
    """
    Make an HTTP request to a server and reports the status code of the response.

    We need to store the status code of the HTTP response and a possible error.
    """

    status: Optional[int] = None
    reason: Optional[Text] = None
    error: Optional[Exception] = None

    def start(self) -> Optional[cuia.Command]:
        """
        Initialize the model.

        This function is called when the application starts. It returns the command we
        made earlier. **We don't call it, just return it.**
        """
        return check_server

    def update(self, message: cuia.Message) -> Optional[cuia.Command]:
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
        elif isinstance(message, cuia.Key):
            if Text(message) in {"ctrl+c", "q"}:
                return cuia.quit
        return None

    def view(self) -> Text:
        """Look at the current model and build a string accordingly."""
        if self.error:
            return f"\033[1mWe had some trouble: {self.error}!\033[0m"
        res = f"\033[2mChecking {URL} … \033[0m"
        if self.status is not None:
            res += f"\033[22;1m{self.status}: {self.reason}\033[0m"
        return res


async def main() -> None:
    """
    Run the application.

    This creates a new application that receives our initial model and starts the
    event loop.
    """
    program = cuia.Program(Model())
    await program.start()


if __name__ == "__main__":
    asyncio.run(main())
