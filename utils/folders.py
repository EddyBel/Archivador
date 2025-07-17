import tkinter as tk
from tkinter import filedialog
from rich.console import Console


def seleccionar_carpeta():
    # Inicializa ventana oculta de Tk
    root = tk.Tk()
    root.withdraw()

    # Lanza selector gráfico de carpetas
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta a organizar")

    # Devuelve ruta seleccionada (cadena vacía si se cancela)
    return carpeta


console = Console()

ruta = seleccionar_carpeta()
if not ruta:
    console.print("[red]No se seleccionó ninguna carpeta.[/red]")
    exit()
else:
    console.print(f"[green]Carpeta seleccionada:[/green] {ruta}")
