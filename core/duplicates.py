import os
import hashlib
import shutil
import time


class DuplicateHandler:
    """
    A class to scan a directory for duplicate files (based on content)
    and move duplicates to a 'duplicates' subfolder. Keeps internal logs
    and returns full results on request.
    """

    def __init__(self, target_folder: str, debug: bool = False):
        """
        Initialize the handler with the target folder and optional debug mode.

        Args:
            target_folder (str): Path to the folder to scan.
            debug (bool): Whether to print logs during execution. Default is False.
        """
        self.folder = os.path.abspath(target_folder)
        self.duplicates_folder = os.path.join(self.folder, "duplicates")
        os.makedirs(self.duplicates_folder, exist_ok=True)

        self.hashes = {}
        self.duplicates_moved = []
        self.files_processed = 0
        self.debug = debug
        self.start_time = None
        self.end_time = None

    def _log(self, message: str) -> None:
        """
        Print log messages only if debug is enabled.

        Args:
            message (str): The message to print.
        """
        if self.debug:
            print(message)

    def _compute_file_hash(self, file_path: str, block_size: int = 65536) -> str | None:
        """
        Compute the SHA-256 hash of a file.

        Args:
            file_path (str): Full path to the file.
            block_size (int): Block size to read the file in bytes.

        Returns:
            str | None: The hash as hex string, or None on failure.
        """
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(block_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self._log(f"Error reading {file_path}: {e}")
            return None

    def scan_and_move_duplicates(self) -> None:
        """
        Main method to scan the target folder, detect duplicates,
        and move them to the 'duplicates' folder.
        """
        self.start_time = time.time()

        for dirpath, _, files in os.walk(self.folder):
            if self.duplicates_folder in dirpath:
                continue  # Skip the duplicates folder itself

            for filename in files:
                full_path = os.path.join(dirpath, filename)
                file_hash = self._compute_file_hash(full_path)

                if not file_hash:
                    continue

                self.files_processed += 1

                if file_hash in self.hashes:
                    original = self.hashes[file_hash]
                    self._log(f"[Duplicate] {full_path} is a duplicate of {original}")
                    self._move_to_duplicates(full_path)
                    self.duplicates_moved.append(full_path)
                else:
                    self.hashes[file_hash] = full_path

        self.end_time = time.time()

    def _move_to_duplicates(self, file_path: str) -> None:
        """
        Move a duplicate file to the 'duplicates' folder, renaming if needed.

        Args:
            file_path (str): Full path of the file to move.
        """
        filename = os.path.basename(file_path)
        destination = os.path.join(self.duplicates_folder, filename)

        counter = 1
        while os.path.exists(destination):
            base_name, extension = os.path.splitext(filename)
            new_name = f"{base_name}_{counter}{extension}"
            destination = os.path.join(self.duplicates_folder, new_name)
            counter += 1

        shutil.move(file_path, destination)

    def _get_results(self) -> dict:
        """
        Return a dictionary with summary of the operation.

        Returns:
            dict: Contains:
                - total_time (float): Time in seconds.
                - total_files (int): Number of files processed.
                - unique_files (int): Number of unique files.
                - duplicate_files (int): Number of files moved as duplicates.
                - duplicates_list (list): List of moved duplicate file paths.
        """
        total_time = (
            (self.end_time - self.start_time)
            if self.start_time and self.end_time
            else None
        )

        return {
            "total_time": total_time,
            "total_files": self.files_processed,
            "unique_files": len(self.hashes),
            "duplicate_files": len(self.duplicates_moved),
            "duplicates_list": self.duplicates_moved.copy(),
        }
