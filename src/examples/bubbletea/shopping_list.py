"""A simple a shopping list."""


from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Optional, Text

import cuia


@dataclass
class Model(cuia.Model):
    """
    A simple a shopping list.

    It starts with some content by default.
    """

    choices: list[Text] = field(
        default_factory=lambda: ["Buy carrots", "Buy celery", "Buy kohlrabi"]
    )
    cursor: int = 0
    selected: set[Text] = field(default_factory=set)

    def update(self, message: cuia.Message) -> Optional[cuia.Command]:
        """
        Update the model.

        It is called when "things happen." Its job is to look at what has happened and
        update the model in response.
        """
        if isinstance(message, cuia.Key):
            # The user pressed a key.
            if Text(message) in {"ctrl+c", "q"}:
                # Quit the application.
                return cuia.quit

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
        res = "\033[1;7mWhat should we buy at the market?\033[0;27m\n\n"
        for i, choice in enumerate(self.choices):
            cursor = "〉" if i == self.cursor else "  "
            checked = "×" if choice in self.selected else " "
            res += f"{cursor}[{checked}] "
            res += (
                f"\033[1m{choice}\033[0;22m"
                if i == self.cursor
                else f"\033[2m{choice}\033[0;22m"
            )
            res += "\n"
        res += "\nPress q to quit.\n"
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
