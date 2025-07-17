from core.duplicates import DuplicateHandler
from core.file_organizer import FileOrganizer
from core.folder_analyzer import FolderAnalyzer
from core.menu import (
    show_ascii_title,
    show_main_menu,
    ask_extension_config,
    ask_rename_config,
    ask_date_mode,
    ask_path,
    show_config_summary,
    simulate_progress,
)
from configs import extension_config as default_ext_config
from configs import rename_config as default_rename_config
from rich.console import Console
from rich.table import Table
import os


def display_results_table(path, results: dict, title: str):
    console = Console()
    table = Table(title=title)

    table.add_column("Archivo", style="cyan", no_wrap=True)
    table.add_column("Detalles", style="magenta")

    for key, value in results.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    display_path = item.replace(path, "").lstrip(os.sep)
                    table.add_row(display_path, key)
        elif isinstance(value, dict):
            for k, v in value.items():
                display_path = k.replace(path, "").lstrip(os.sep)
                table.add_row(display_path, str(v))
        else:
            table.add_row(str(key), str(value))

    console.print(table)


def main():
    show_ascii_title()

    choice = show_main_menu()

    if choice == "5":
        print("Saliendo del Archivador...")
        return

    config_summary = {}

    # Pedir ruta de carpeta
    path = ask_path()
    config_summary["Ruta"] = path

    # Ejecutar según elección
    do_duplicates = choice in ["1", "4"]
    do_classify_ext = choice in ["2", "4"]
    do_classify_date = choice == "3"

    # Configuración de clasificación por extensión
    ext_config = None
    if do_classify_ext:
        ext_config = ask_extension_config(default_ext_config)
        config_summary["Clasificación por extensión"] = ext_config

    # Configuración de clasificación por fecha
    date_mode = None
    if do_classify_date:
        date_mode = ask_date_mode()
        config_summary["Clasificación por fecha"] = date_mode

    # Configuración de renombrado
    rename_config = ask_rename_config(default_rename_config)
    config_summary["Renombrado"] = rename_config

    # Mostrar resumen
    show_config_summary(config_summary)

    # Ejecutar duplicados
    if do_duplicates:
        simulate_progress("Eliminando duplicados", seconds=2)
        dh = DuplicateHandler(path)
        dh.scan_and_move_duplicates()
        dh_results = dh._get_results()
        display_results_table(path, dh_results, "Archivos Duplicados")

    # Ejecutar organización por extensión/fecha
    if do_classify_ext or do_classify_date:
        simulate_progress("Organizando archivos", seconds=3)
        fo = FileOrganizer(
            path=path,
            extension_config=ext_config if do_classify_ext else None,
            rename_config=rename_config,
            date_mode=date_mode if do_classify_date else None,
        )
        fo.organize()
        fo_results = fo._get_results()
        display_results_table(path, fo_results, "Organización de Archivos")

    # Ejecutar análisis
    simulate_progress("Analizando carpeta final", seconds=2)
    fa = FolderAnalyzer(path)
    fa.analyze()
    fa_results = fa._get_results()
    display_results_table(path, fa_results, "Análisis Final de Carpeta")


if __name__ == "__main__":
    main()
