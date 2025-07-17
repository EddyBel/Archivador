from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.json import JSON
from rich.style import Style
from rich.theme import Theme
from typing import Any


class RichLogger:
    """
    A class for rich, styled logging using the 'rich' library.
    Includes methods for formatted messages, JSON dumps,
    and boxed summaries with color customization.
    """

    def __init__(self, theme: dict[str, str] = None):
        """
        Initialize the logger with an optional custom theme.

        Args:
            theme (dict): A dictionary mapping message types to color names.
        """
        default_theme = {
            "info": "cyan",
            "warning": "yellow",
            "error": "bold red",
            "success": "green",
            "box_border": "bright_blue",
            "json": "white",
        }

        self.theme = theme or default_theme
        self.console = Console(theme=Theme({
            "info": self.theme["info"],
            "warning": self.theme["warning"],
            "error": self.theme["error"],
            "success": self.theme["success"],
            "json": self.theme["json"],
        }))

    def log_info(self, message: str) -> None:
        """Display an informational message."""
        self.console.print(f"[info][INFO][/info] {message}")

    def log_warning(self, message: str) -> None:
        """Display a warning message."""
        self.console.print(f"[warning][WARNING][/warning] {message}")

    def log_error(self, message: str) -> None:
        """Display an error message."""
        self.console.print(f"[error][ERROR][/error] {message}")

    def log_success(self, message: str) -> None:
        """Display a success message."""
        self.console.print(f"[success][SUCCESS][/success] {message}")

    def log_json(self, data: dict | list, title: str = "JSON Data") -> None:
        """
        Pretty-print a dictionary or list as JSON.

        Args:
            data (dict | list): The data to display.
            title (str): Optional title above the JSON output.
        """
        self.console.rule(f"[bold]{title}")
        self.console.print(JSON.from_data(data))

    def show_summary_box(self, title: str, content: dict[str, Any], border_color: str = None) -> None:
        """
        Display a summary in a stylized box panel.

        Args:
            title (str): Title of the box.
            content (dict): Key-value pairs to display inside.
            border_color (str): Optional border color (default from theme).
        """
        border_style = border_color or self.theme["box_border"]
        text_lines = "\n".join(
            f"[bold]{key}:[/bold] {value}" for key, value in content.items()
        )
        panel = Panel(Text(text_lines), title=title, border_style=border_style)
        self.console.print(panel)
