"""An example of using colors module."""

import asyncio
from typing import Text

import cuia


class ColorfulExample(cuia.Store):
    """A store class that shows how to use colors."""

    def __str__(self) -> Text:
        """Show me some colors."""
        res = "Colors (backgrounds):\n\n"
        res += "\033[40mBlack!\n"
        res += "\033[41mRed!\n"
        res += "\033[42mGreen!\n"
        res += "\033[43mYellow!\n"
        res += "\033[44mBlue!\n"
        res += "\033[45mMagenta!\n"
        res += "\033[46mCyan!\n"
        res += "\033[47mWhite!\n"
        res += "\033[0m\n"
        res += "Colors (foregrounds):\n\n"
        res += "\033[38;5;240mBlack!\n"  # some medium shade of gray
        res += "\033[91mRed!\n"
        res += "\033[92mGreen!\n"
        res += "\033[93mYellow!\n"
        res += "\033[38;2;100;149;237mBlue!\n"  # cornflower blue
        res += "\033[95mMagenta!\n"
        res += "\033[96mCyan!\n"
        res += "\033[97mWhite!\n"
        return res


async def main() -> None:
    """Run the application."""
    program = cuia.Program(ColorfulExample())
    await program.start()


if __name__ == "__main__":
    asyncio.run(main())
