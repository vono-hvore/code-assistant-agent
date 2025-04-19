import os
import aiofiles
import aiofiles.os
import aiofiles.ospath
from collections import defaultdict
from pathspec import GitIgnoreSpec
from typing import List, Optional


class Scanner:
    def _read_gitignore(self, gitignore_path: str) -> GitIgnoreSpec:
        try:
            with open(gitignore_path, mode="r") as fh:
                spec = GitIgnoreSpec.from_lines("gitwildmatch", fh)
                return spec
        except Exception as e:
            print(f"Failed to read .gitignore at {gitignore_path}: {e}")
            raise

    async def _filter_ignore_files(
        self, files: list[str], ignore: GitIgnoreSpec
    ) -> list[str]:
        filter_paths = list[str]()

        for path in files:
            if ignore.match_file(path) or ".git" in path:
                continue

            filter_paths.append(path)

        return filter_paths

    async def scan_path(self, root_path: Optional[str] = None) -> List[str]:
        if not root_path:
            raise ValueError("No root path provided")

        paths: List[str] = []
        spec = GitIgnoreSpec.from_lines([])

        try:
            entries = await aiofiles.os.listdir(root_path)
        except Exception as e:
            print(f"Error reading directory {root_path}: {e}")
            return paths

        for entry_name in entries:
            full_path = os.path.join(root_path, entry_name)

            try:
                is_dir = await aiofiles.ospath.isdir(full_path)
            except Exception as e:
                print(f"Error checking if {full_path} is directory: {e}")
                continue

            if ".gitignore" in full_path:
                spec = self._read_gitignore(full_path)

            if is_dir:
                try:
                    sub_files = await self.scan_path(full_path)
                    paths.extend(sub_files)
                except Exception as e:
                    print(f"Error scanning subdirectory {full_path}: {e}")
            else:
                paths.append(full_path)

        paths = await self._filter_ignore_files(paths, spec)
        return paths

    def search_files(self, root: str, name: str = "", content: str = "") -> list:
        matches = []
        try:
            for dirpath, _, filenames in os.walk(root):
                for fname in filenames:
                    full_path = os.path.join(dirpath, fname)

                    if name and name not in fname:
                        continue

                    if content:
                        try:
                            with open(
                                full_path, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                if content not in f.read():
                                    continue
                        except Exception:
                            continue

                    matches.append(full_path)
        except Exception as e:
            raise e

        return matches

    def prettier(self, paths: list[str]) -> str:
        tree = lambda: defaultdict(tree)
        file_tree = tree()
        pretty_str = ""

        for path in paths:
            parts = path.lstrip("./").split("/")
            current = file_tree
            for part in parts:
                current = current[part]

        def make_tree(node, prefix="") -> str:
            pretty_str = ""
            items = sorted(node.items())
            for i, (name, child) in enumerate(items):
                is_last = i == len(items) - 1
                connector = "└── " if is_last else "├── "
                pretty_str += prefix + connector + name + "\n"
                extension = "    " if is_last else "│   "
                pretty_str += make_tree(child, prefix + extension)
            return pretty_str

        pretty_str += make_tree(file_tree)
        return pretty_str
