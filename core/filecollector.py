import os
import shutil
import time
import json
from typing import Optional, Dict, List
from datetime import datetime


class FileCollector:
    """
    Recorre recursivamente una carpeta origen, identifica archivos por tipo (según una configuración JSON),
    y los mueve a una carpeta destino, organizándolos por tipo de archivo.
    Puede excluir archivos por prefijos o extensiones según configuración.
    """

    DEFAULT_EXCLUDED_STARTS = ("~", ".", "$")
    DEFAULT_EXCLUDED_EXTS = ("tmp", "log", "sys", "dll", "ini", "lnk")

    def __init__(
        self,
        source_path: str,
        dest_path: str,
        config: dict,
        excluded_config: Optional[Dict[str, List[str]]] = None,
    ):
        self.source_path = os.path.abspath(source_path)
        self.dest_path = os.path.abspath(dest_path)
        self.config = config
        self.excluded_starts = (
            tuple(excluded_config.get("invalid_starts", self.DEFAULT_EXCLUDED_STARTS))
            if excluded_config
            else self.DEFAULT_EXCLUDED_STARTS
        )
        self.excluded_exts = (
            tuple(excluded_config.get("invalid_exts", self.DEFAULT_EXCLUDED_EXTS))
            if excluded_config
            else self.DEFAULT_EXCLUDED_EXTS
        )

        self.moved_files = {}
        self.errors = []
        self.start_time = None
        self.end_time = None

    def _is_valid_file(self, filename: str) -> bool:
        ext = os.path.splitext(filename)[1][1:].lower()
        # Ignora archivos con prefijos o extensiones excluidos
        if filename.startswith(self.excluded_starts):
            return False
        if ext in self.excluded_exts:
            return False
        return True

    def _match_category(self, ext: str) -> Optional[str]:
        for category, extensions in self.config.items():
            if ext.lower() in extensions:
                return category
        return None

    def _move_file(self, src: str, category: str, filename: str):
        dest_folder = os.path.join(self.dest_path, category)
        os.makedirs(dest_folder, exist_ok=True)

        dst = os.path.join(dest_folder, filename)
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(dst):
            dst = os.path.join(dest_folder, f"{base}_{counter}{ext}")
            counter += 1

        shutil.move(src, dst)
        self.moved_files.setdefault(category, []).append(dst)

    def collect(self):
        self.start_time = time.time()

        for root, _, files in os.walk(self.source_path):
            for file in files:
                if not self._is_valid_file(file):
                    continue

                ext = os.path.splitext(file)[1][1:].lower()
                category = self._match_category(ext)

                if not category:
                    continue

                try:
                    full_path = os.path.join(root, file)
                    self._move_file(full_path, category, file)
                except Exception as e:
                    self.errors.append(f"{file}: {str(e)}")

        self.end_time = time.time()

    def _get_results(self) -> dict:
        return {
            "start_time": (
                datetime.fromtimestamp(self.start_time).isoformat()
                if self.start_time
                else None
            ),
            "end_time": (
                datetime.fromtimestamp(self.end_time).isoformat()
                if self.end_time
                else None
            ),
            "duration_seconds": (
                round(self.end_time - self.start_time, 2)
                if self.start_time and self.end_time
                else None
            ),
            "total_files_moved": sum(len(v) for v in self.moved_files.values()),
            "categories": list(self.moved_files.keys()),
            "files_by_category": self.moved_files,
            "errors": self.errors,
        }
