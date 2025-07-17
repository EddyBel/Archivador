import os
from typing import Literal, Optional
from collections import defaultdict


class FolderAnalyzer:
    """
    Analyzes a folder and provides detailed info about sizes, counts,
    and structure of files and subfolders.
    """

    def __init__(
        self, path: str, order_by: Literal["asc", "desc"] = "desc", unit: str = "MB"
    ):
        """
        Args:
            path (str): Path to the folder to analyze.
            order_by (str): 'asc' for smallest to largest, 'desc' for largest to smallest.
            unit (str): Unit for display size: B, KB, MB, GB
        """
        self.base_path = os.path.abspath(path)
        self.order = order_by
        self.unit = unit.upper()
        self.unit_divisor = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}.get(
            self.unit, 1024**2
        )

        self.file_data = []  # List of (file_path, size_in_bytes)
        self.folder_data = defaultdict(lambda: {"size": 0, "files": 0, "folders": 0})

    def _get_size(self, path: str) -> int:
        """Returns file size in bytes."""
        try:
            return os.path.getsize(path)
        except Exception:
            return 0

    def _scan(self):
        """Walk through the folder and collect data."""
        for root, dirs, files in os.walk(self.base_path):
            total_size = 0
            file_count = 0
            folder_count = len(dirs)

            for file in files:
                full_path = os.path.join(root, file)
                size = self._get_size(full_path)
                total_size += size
                self.file_data.append((full_path, size))
                file_count += 1

            self.folder_data[root]["size"] = total_size
            self.folder_data[root]["files"] = file_count
            self.folder_data[root]["folders"] = folder_count

    def _convert_size(self, size_bytes: int) -> float:
        return round(size_bytes / self.unit_divisor, 2)

    def analyze(self):
        """Run the folder scan."""
        self._scan()

    def _get_results(self) -> dict:
        """
        Return analysis results as a structured dictionary.

        Returns:
            dict: includes:
                - top_files (list of tuples): [(file, size)]
                - folders_info (dict): {folder: {size, files, folders}}
                - total_files (int)
                - total_size (float, in selected unit)
        """
        sorted_files = sorted(
            self.file_data, key=lambda x: x[1], reverse=self.order == "desc"
        )
        converted_files = [
            (path, self._convert_size(size)) for path, size in sorted_files
        ]

        folder_summary = {
            folder: {
                "size": self._convert_size(data["size"]),
                "files": data["files"],
                "subfolders": data["folders"],
            }
            for folder, data in self.folder_data.items()
        }

        total_size = sum(size for _, size in self.file_data)
        total_files = len(self.file_data)

        return {
            "unit": self.unit,
            "total_size": self._convert_size(total_size),
            "total_files": total_files,
            "top_files": converted_files,
            "folders_info": folder_summary,
        }
