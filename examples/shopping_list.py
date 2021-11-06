"""
A simple usage example.

This example is based on the
[first bubbletea tutorial](https://github.com/charmbracelet/bubbletea/tree/master/tutorials/basics).
"""


from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass, field
from typing import Optional, Text

import kay


@dataclass
class Model(kay.Model):
    """
    A simple a shopping list.

    It starts with some content by default.
    """

    choices: list[Text] = field(
        default_factory=lambda: ["Buy carrots", "Buy celery", "Buy kohlrabi"]
    )
    cursor: int = 0
    selected: set[Text] = field(default_factory=set)

    def init(self) -> Optional[kay.Command]:
        """
        Do nothing during initialization, please.

        This actually means "no I/O right now, please."
        """
        return None

    def update(self, message: kay.Message) -> Optional[kay.Command]:
        """
        Update the model.

        It is called when "things happen." Its job is to look at what has happened and
        update the model in response.
        """
        if isinstance(message, kay.KeyMessage):
            # The user pressed a key.
            if Text(message) in {"ctrl+c", "q"}:
                # Quit the application.
                return kay.quit

            if Text(message) in {"up", "k"}:
                # Move the cursor up.
                self.cursor = max(0, self.cursor - 1)
            elif Text(message) in {"down", "j"}:
                # Move the cursor down.
                self.cursor = min(len(self.choices) - 1, self.cursor + 1)
            elif Text(message) in {"enter", "space"}:
                # Toggle the selected state of the current choice.
                if (choice := self.choices[self.cursor]) in self.selected:
                    self.selected.remove(choice)
                else:
                    self.selected.add(choice)
        return None

    def view(self) -> Text:
        """
        Render the model.

        It is called when it is time to render our UI. It basically just returns a
        string that will be printed to the screen.
        """
        res = "What should we buy at the market?\n\n"
        for i, choice in enumerate(self.choices):
            cursor = "〉" if i == self.cursor else "  "
            checked = "×" if choice in self.selected else " "
            res += f"{cursor}[{checked}] {choice}\n"
        res += "\nPress q to quit.\n"
        return res


async def main() -> None:
    """
    Run the application.

    This creates a new application that receives our initial model and starts the
    event loop.
    """
    program = kay.Program(Model())
    try:
        await program.start()
    except Exception as err:
        # It is a good idea to narrow down the error type in production code.
        print(f"Alas, there's been an error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
