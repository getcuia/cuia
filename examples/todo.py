"""A simple usage example."""


from dataclasses import dataclass, field
from typing import List, Optional, Set
import sys


import kay


@dataclass
class Model(kay.Model[kay.Event]):
    """A simple todo model."""

    choices: List[str] = field(
        default_factory=lambda: ["Buy carrots", "Buy celery", "Buy kohlrabi"]
    )
    cursor: int = 0
    selected: Set[str] = field(default_factory=set)

    def update(self, msg: kay.Event) -> Optional[kay.Command]:
        """Update the model."""
        if isinstance(msg, kay.KeyEvent):
            if str(msg) in {"ctrl+c", "q"}:
                return kay.Quit
            elif str(msg) in {"up", "k"}:
                self.cursor = max(0, self.cursor - 1)
            elif str(msg) in {"down", "j"}:
                self.cursor = min(len(self.choices) - 1, self.cursor + 1)
            elif str(msg) in {"enter", " "}:
                if (choice := self.choices[self.cursor]) in self.selected:
                    self.selected.remove(choice)
                else:
                    self.selected.add(choice)
        return None

    def view(self) -> str:
        """Render the model."""
        s = "What should we buy at the market?\n\n"
        for i, choice in enumerate(self.choices):
            cursor = "〉" if i == self.cursor else "  "
            checked = "×" if choice in self.selected else " "
            s += f"{cursor}[{checked}]{choice}\n"
        s += "\nPress q to quit.\n"
        return s


def main() -> None:
    """Run the application."""
    p = kay.Program(Model())
    try:
        p.start()
    except Exception as err:
        print(f"Alas, there's been an error: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
