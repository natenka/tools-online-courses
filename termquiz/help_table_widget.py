from rich.text import Text

from textual.widget import Widget
from textual.widgets import Footer


class HelpTable(Footer):
    def __init__(self):
        super().__init__()
        self.long_description = False

    def make_key_text(self) -> Text:
        """Create text containing all the keys."""
        text = Text(
            style="black on green",
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
        )
        for binding in self.app.bindings.shown_keys:
            key = binding.key
            key_display = (
                binding.key_display if binding.key_display else binding.description
            )
            description = key_display if self.long_description else binding.description
            hovered = self.highlight_key == binding.key
            key_text = Text.assemble(
                (f" {key} ", "reverse" if hovered else "default on default"),
                f" {description} ",
                meta={"@click": f"app.press('{binding.key}')", "key": binding.key},
            )
            text.append_text(key_text)
        return text

    async def toggle(self):
        self.long_description = not self.long_description
        self._key_text = self.make_key_text()
        self.refresh()

    def render(self):
        if self._key_text is None:
            self._key_text = self.make_key_text()
        return self._key_text
