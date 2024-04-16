from pathlib import Path
from unittest.mock import MagicMock

import pytest

from cuality.lint_ignores import IgnoreLinesStat, IgnoreLinesInFile


def test_add_ignores():
    ignore_lines_stat = IgnoreLinesStat()

    assert ignore_lines_stat.total_ignores == 0
    assert ignore_lines_stat.total_lines == 0
    assert not ignore_lines_stat.ignore_by_file

    ignore_lines_stat.add_ignores(IgnoreLinesInFile(Path("foo"), 10, 1))
    assert ignore_lines_stat.total_ignores == 1
    assert ignore_lines_stat.total_lines == 10
    assert ignore_lines_stat.ignore_by_file

    ignore_lines_stat.add_ignores(IgnoreLinesInFile(Path("baz"), 15, 2))
    assert ignore_lines_stat.total_ignores == 3
    assert ignore_lines_stat.total_lines == 25


def test_python_files(tmp_path, python_files):
    ignore_lines_stat = IgnoreLinesStat()
    py_files = set(ignore_lines_stat.python_files(tmp_path))
    assert py_files == python_files


@pytest.fixture
def python_files(tmp_path):
    # Adds python files
    python_files = {
        add_file(tmp_path, "root.py"),
        add_file(tmp_path / "subfolder", "file1.py"),
        add_file(tmp_path / "subfolder", "file2.py"),
        add_file(tmp_path / "subfolder" / "sub", "file3.py"),
    }

    # Add not Python files
    add_file(tmp_path, "Dockerfile")
    add_file(tmp_path / "subfolder", "foo.csv")
    add_file(tmp_path / "subfolder" / "sub", "file4.txt")
    add_file(tmp_path / "resources", "random.md")
    yield python_files


def add_file(folder: Path, name: str) -> Path:
    folder.mkdir(exist_ok=True)
    file = folder / name
    file.touch(exist_ok=True)
    return file


def test_ignore_lines_in_file_parsing(python_test_file):
    stat = IgnoreLinesInFile.from_file(python_test_file)
    assert stat.total_lines == 5
    assert stat.total_ignores == 1
    assert stat.file is python_test_file


@pytest.fixture
def python_test_file(tmp_path):
    file = tmp_path / "root.py"
    with open(file, "w") as f:
        f.write("import sys\n")
        f.write("import os\n\n\n")
        f.write("def main():\n")
        f.write("    print('Hello World!')\n")
        f.write("    sys.exit(0)    # type: ignore\n")
    yield file


@pytest.mark.parametrize(
    "line",
    (
        "def main():    # type: ignore\n",
        "import foo  # noqa: foo\n",
        'import foo  # mypy: disable-error-code="empty-body"\n',
        "import foo  # pylint: disable=no-member\n",
        "# pylint: disable=no-member\n",
        "import foo  # nosec B602, B607\n",
        "import foo  # pragma: no cover\n",
    ),
)
def test_parse_lines_with_ignore(line):
    stat = IgnoreLinesInFile(MagicMock(spec=Path))
    stat.parse_line(line)
    assert stat.total_ignores == 1


@pytest.mark.parametrize(
    "line",
    (
        "# some comment\n",
        "\n",
        "    \n",
        " ",
    ),
)
def test_empty_lines_and_comments_only_ignored(line):
    stat = IgnoreLinesInFile(MagicMock(spec=Path))
    stat.parse_line(line)
    assert stat.total_lines == 0
    assert stat.total_ignores == 0
