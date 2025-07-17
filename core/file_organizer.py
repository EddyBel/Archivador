import os
import shutil
import time
from datetime import datetime
from typing import Optional, Callable
import re


class FileOrganizer:
    """
    Organizes and classifies files by extension or date,
    with configurable renaming and logging.
    """

    def __init__(
        self,
        path: str,
        extension_config: Optional[dict] = None,
        rename_config: Optional[dict] = None,
        date_mode: Optional[str] = None,
        date_range: Optional[tuple] = None,
    ):
        """
        Args:
            path (str): Target folder.
            extension_config (dict): Classification structure for file extensions.
            rename_config (dict): Rules for renaming files.
            date_mode (str): 'full', 'day', 'month', 'year', 'range', or None.
            date_range (tuple): (start_date, end_date) for 'range' mode. Format: 'YYYY-MM-DD'
        """
        self.base_path = os.path.abspath(path)
        self.ext_config = extension_config or {}
        self.rename_config = rename_config or {}
        self.date_mode = date_mode
        self.date_range = date_range
        self.errors = []
        self.moved_files = {}
        self.renamed_count = 0
        self.start_time = None
        self.end_time = None

    def _get_creation_date(self, path: str) -> datetime:
        return datetime.fromtimestamp(os.path.getctime(path))

    def _format_date(self, dt: datetime) -> str:
        mode = self.date_mode
        if mode == "full":
            return dt.strftime("%Y-%m-%d_%H-%M")
        elif mode == "day":
            return dt.strftime("%Y-%m-%d")
        elif mode == "month":
            return dt.strftime("%Y-%m")
        elif mode == "year":
            return dt.strftime("%Y")
        return "UnknownDate"

    def _matches_range(self, dt: datetime) -> bool:
        if not self.date_range:
            return False
        start = datetime.strptime(self.date_range[0], "%Y-%m-%d")
        end = datetime.strptime(self.date_range[1], "%Y-%m-%d")
        return start <= dt <= end

    def _clean_name(self, name: str) -> str:
        if self.rename_config.get("clean_windows_duplicates", False):
            name = re.sub(r"\s\(\d+\)", "", name)
        if self.rename_config.get("remove_spaces", False):
            name = name.replace(" ", "")
        elif self.rename_config.get("replace_spaces", False):
            name = name.replace(" ", "_")
        elif self.rename_config.get("camel_case_spaces", False):
            name = re.sub(r" (.)", lambda m: m.group(1).upper(), name).replace(" ", "")
        return name

    def _rename_file(self, filename: str, src_path: str, dt: datetime) -> str:
        name, ext = os.path.splitext(filename)
        original = name
        name = self._clean_name(name)

        prefix = self.rename_config.get("prefix", "")
        add_date = self.rename_config.get("add_date", False)
        use_creation = self.rename_config.get("use_creation_date", True)

        if add_date:
            date_str = dt.strftime("%Y-%m-%d")
            name = f"{prefix}_{date_str}_{name}"
        elif prefix:
            name = f"{prefix}_{name}"

        if name != original:
            self.renamed_count += 1

        return name + ext

    def _move_file(self, src_path: str, dest_folder: str, filename: str):
        os.makedirs(dest_folder, exist_ok=True)
        dst_path = os.path.join(dest_folder, filename)
        counter = 1
        base_name, ext = os.path.splitext(filename)

        while os.path.exists(dst_path):
            filename = f"{base_name}_{counter}{ext}"
            dst_path = os.path.join(dest_folder, filename)
            counter += 1

        shutil.move(src_path, dst_path)
        self.moved_files.setdefault(dest_folder, []).append(dst_path)

    def organize(self):
        self.start_time = time.time()

        for file in os.listdir(self.base_path):
            full_path = os.path.join(self.base_path, file)
            if not os.path.isfile(full_path):
                continue

            try:
                dt = self._get_creation_date(full_path)
                ext = os.path.splitext(file)[1][1:].lower()

                # Decide target folder
                folder = "Otros"

                if self.ext_config:
                    for category, rules in self.ext_config.items():
                        if isinstance(rules, list) and ext in rules:
                            folder = category
                            break
                        elif isinstance(rules, dict):
                            for subfolder, exts in rules.items():
                                if ext in exts:
                                    folder = os.path.join(category, subfolder)
                                    break

                elif self.date_mode:
                    if self.date_mode == "range" and not self._matches_range(dt):
                        continue
                    folder = self._format_date(dt)

                dest_folder = os.path.join(self.base_path, folder)

                new_name = self._rename_file(file, full_path, dt)
                self._move_file(full_path, dest_folder, new_name)

            except Exception as e:
                self.errors.append(f"{file}: {str(e)}")

        self.end_time = time.time()

    def _get_results(self) -> dict:
        return {
            "duration_seconds": (
                round(self.end_time - self.start_time, 2)
                if self.start_time and self.end_time
                else None
            ),
            "total_moved": sum(len(v) for v in self.moved_files.values()),
            "total_renamed": self.renamed_count,
            "folders_created": list(self.moved_files.keys()),
            "moved_files": self.moved_files,
            "errors": self.errors,
        }
