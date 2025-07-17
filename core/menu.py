from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import track
from rich.text import Text
from rich.table import Table
import time
import json

# ASCII title
ASCII_TITLE = """

 ▄▄▄       ██▀███   ▄████▄   ██░ ██  ██▓ ██▒   █▓ ▄▄▄      ▓█████▄  ▒█████   ██▀███  
▒████▄    ▓██ ▒ ██▒▒██▀ ▀█  ▓██░ ██▒▓██▒▓██░   █▒▒████▄    ▒██▀ ██▌▒██▒  ██▒▓██ ▒ ██▒
▒██  ▀█▄  ▓██ ░▄█ ▒▒▓█    ▄ ▒██▀▀██░▒██▒ ▓██  █▒░▒██  ▀█▄  ░██   █▌▒██░  ██▒▓██ ░▄█ ▒
░██▄▄▄▄██ ▒██▀▀█▄  ▒▓▓▄ ▄██▒░▓█ ░██ ░██░  ▒██ █░░░██▄▄▄▄██ ░▓█▄   ▌▒██   ██░▒██▀▀█▄  
 ▓█   ▓██▒░██▓ ▒██▒▒ ▓███▀ ░░▓█▒░██▓░██░   ▒▀█░   ▓█   ▓██▒░▒████▓ ░ ████▓▒░░██▓ ▒██▒
 ▒▒   ▓▒█░░ ▒▓ ░▒▓░░ ░▒ ▒  ░ ▒ ░░▒░▒░▓     ░ ▐░   ▒▒   ▓▒█░ ▒▒▓  ▒ ░ ▒░▒░▒░ ░ ▒▓ ░▒▓░
  ▒   ▒▒ ░  ░▒ ░ ▒░  ░  ▒    ▒ ░▒░ ░ ▒ ░   ░ ░░    ▒   ▒▒ ░ ░ ▒  ▒   ░ ▒ ▒░   ░▒ ░ ▒░
  ░   ▒     ░░   ░ ░         ░  ░░ ░ ▒ ░     ░░    ░   ▒    ░ ░  ░ ░ ░ ░ ▒    ░░   ░ 
      ░  ░   ░     ░ ░       ░  ░  ░ ░        ░        ░  ░   ░        ░ ░     ░     
                   ░                         ░              ░                        
                             Archivador de archivos
"""

console = Console()


def show_ascii_title():
    console.print(Text(ASCII_TITLE, style="bold blue"))


def show_main_menu():
    console.print("\n[bold underline]¿Qué deseas hacer?[/]\n")
    console.print("1. Separar archivos duplicados")
    console.print("2. Clasificar archivos por extensión")
    console.print("3. Clasificar archivos por fecha")
    console.print("4. Realizar todo (duplicados + clasificación)")
    console.print("5. Salir")

    choice = Prompt.ask("\nSelecciona una opción", choices=["1", "2", "3", "4", "5"])
    return choice


def ask_extension_config(default_config: dict) -> dict:
    console.rule("[bold]Configuración de extensiones")
    console.print("[green]Configuración por defecto:[/green]")
    console.print_json(json.dumps(default_config, indent=2))
    use_default = Confirm.ask("\n¿Quieres usar esta configuración por defecto?")
    if use_default:
        return default_config
    else:
        console.print(
            "[yellow]Por ahora solo puedes modificar manualmente desde el archivo de configuración.[/yellow]"
        )
        return default_config


def ask_rename_config(default_config: dict) -> dict:
    console.rule("[bold]Configuración de renombrado")
    console.print("[green]Configuración por defecto:[/green]")
    console.print_json(json.dumps(default_config, indent=2))
    use_default = Confirm.ask("\n¿Quieres usar esta configuración por defecto?")
    if use_default:
        return default_config
    else:
        console.print(
            "[yellow]Por ahora solo puedes modificar manualmente desde el archivo de configuración.[/yellow]"
        )
        return default_config


def ask_date_mode() -> str:
    console.rule("[bold]Modo de clasificación por fecha")
    console.print("1. Por fecha completa (día y hora)")
    console.print("2. Por día")
    console.print("3. Por mes")
    console.print("4. Por año")
    console.print("5. Entre fechas específicas")
    choice = Prompt.ask("\nSelecciona una opción", choices=["1", "2", "3", "4", "5"])
    return {"1": "full", "2": "day", "3": "month", "4": "year", "5": "range"}[choice]


def ask_path() -> str:
    return Prompt.ask("Introduce la ruta de la carpeta a archivar")


def show_config_summary(config: dict):
    console.rule("[bold green]Resumen de configuración seleccionada")
    console.print_json(json.dumps(config, indent=2))


def simulate_progress(task_name: str, seconds: int = 3):
    console.rule(f"[bold blue]{task_name}")
    for _ in track(range(seconds), description=f"[cyan]{task_name}..."):
        time.sleep(1)
