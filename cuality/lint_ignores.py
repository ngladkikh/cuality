import csv
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterator


IGNORE_PATTERN = re.compile(
    r"(.+)?#\s*(noqa:|pylint:|type:\s*ignore|nosec|mypy:|pragma:)"
)


@dataclass
class IgnoreLinesInFile:
    file: Path
    total_lines: int = 0
    total_ignores: int = 0

    def set_root(self, root_path: Path) -> None:
        self.file = self.file.resolve().relative_to(root_path.resolve())

    def parse_line(self, line: str) -> None:
        line = line.strip()
        if line in ("", "\n"):
            return
        if not line.startswith("#"):
            self.total_lines += 1
        if IGNORE_PATTERN.match(line):
            self.total_ignores += 1

    @classmethod
    def from_file(
        cls, file: Path, root_folder: Path | None = None
    ) -> "IgnoreLinesInFile":
        file_stat = IgnoreLinesInFile(file)
        file_stat.set_root(root_folder)
        with file.open() as f:
            while True:
                line = f.readline()
                if not line:
                    break
                file_stat.parse_line(line)
        return file_stat


@dataclass
class IgnoreLinesStat:
    total_lines: int = 0
    total_ignores: int = 0
    ignore_by_file: list[IgnoreLinesInFile] = field(default_factory=list)

    def add_ignores(self, file_stat: IgnoreLinesInFile) -> None:
        if file_stat.file not in self.ignore_by_file:
            self.ignore_by_file.append(file_stat)
            self.total_lines += file_stat.total_lines
            self.total_ignores += file_stat.total_ignores

    def parse_project_folder(self, path: Path) -> None:
        for python_file in self.python_files(path):
            file_stat = IgnoreLinesInFile.from_file(python_file, path)
            self.add_ignores(file_stat)

    def save_stat_to_csv(self, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as output_file:
            writer = csv.DictWriter(
                output_file, fieldnames=["file", "total_lines", "total_ignores"]
            )
            writer.writeheader()
            for file_stat in self.ignore_by_file:
                writer.writerow(asdict(file_stat))

    def python_files(self, path: Path) -> Iterator[Path]:
        for path_object in path.iterdir():
            if path_object.is_dir():
                yield from self.python_files(path_object)
            elif self._is_python_file(path_object):
                yield path_object

    @staticmethod
    def _is_python_file(path_object: Path) -> bool:
        return path_object.suffixes and path_object.suffixes[-1] == ".py"


def lint_ignores(code_folder: Path, output_file: Path) -> None:
    stat = IgnoreLinesStat()
    stat.parse_project_folder(code_folder)
    stat.save_stat_to_csv(output_file)


if __name__ == "__main__":
    lint_ignores(Path(sys.argv[1]), Path(sys.argv[2]))
