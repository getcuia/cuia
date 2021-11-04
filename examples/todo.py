"""A simple usage example."""


from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass, field
from typing import Optional, Text

import kay


@dataclass
class Model(kay.Model):
    """A simple todo model."""

    choices: list[Text] = field(
        default_factory=lambda: ["Buy carrots", "Buy celery", "Buy kohlrabi"]
    )
    cursor: int = 0
    selected: set[Text] = field(default_factory=set)

    def init(self) -> Optional[kay.Command]:
        """Do nothing during initialization, please."""
        return None

    def update(self, message: kay.Message) -> Optional[kay.Command]:
        """Update the model."""
        if isinstance(message, kay.KeyMessage):
            if Text(message) in {"ctrl+c", "q"}:
                return kay.quit
            elif Text(message) in {"up", "k"}:
                self.cursor = max(0, self.cursor - 1)
            elif Text(message) in {"down", "j"}:
                self.cursor = min(len(self.choices) - 1, self.cursor + 1)
            elif Text(message) in {"enter", " "}:
                if (choice := self.choices[self.cursor]) in self.selected:
                    self.selected.remove(choice)
                else:
                    self.selected.add(choice)
        return None

    def view(self) -> Text:
        """Render the model."""
        s = "What should we buy at the market?\n\n"
        for i, choice in enumerate(self.choices):
            cursor = "〉" if i == self.cursor else "  "
            checked = "×" if choice in self.selected else " "
            s += f"{cursor}[{checked}]{choice}\n"
        s += "\nPress q to quit.\n"
        return s


async def main() -> None:
    """Run the application."""
    p = kay.Program(Model())
    try:
        await p.start()
    except Exception as err:
        print(f"Alas, there's been an error: {err}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
