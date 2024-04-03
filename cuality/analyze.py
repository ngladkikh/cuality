import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class Args:
    folder: str


@dataclass
class Package:
    path: Path
    migrations: Optional[Path] = None

    def find_migrations(self, path: Optional[Path] = None) -> None:
        path = self.path if path is None else path
        if path.is_dir():
            for folder in filter(lambda x: x.is_dir(), path.iterdir()):
                if folder.name == "migration":
                    self.migrations = folder
                    return
                else:
                    self.find_migrations(folder)


@dataclass
class Project:
    path: Path
    packages: list[Package] = field(default_factory=list)

    def __str__(self) -> str:
        r = f"Project {self.path.name}\n\t{self.path.absolute()}\n"
        if self.packages:
            r += "Packages: \n"
            table = [["Name", "migrations"]]
            for pkg in self.packages:
                table.append(
                    [
                        pkg.path.name,
                        (
                            str(pkg.migrations.relative_to(self.path))
                            if pkg.migrations
                            else ""
                        ),
                    ]
                )

            max_name_length, max_migration_path = 4, 10
            for name, migration_path in table:
                if len(name) > max_name_length:
                    max_name_length = len(name)
                if len(migration_path) > max_migration_path:
                    max_migration_path = len(migration_path)

            format_ = f"| {{:{max_name_length}}} | {{:{max_migration_path}}} |"
            for row in table:
                r += format_.format(*row) + "\n"
        return r


def analyze(folder: Path) -> Optional[Project]:
    if folder.exists():
        if folder.is_dir():
            project = Project(path=folder)
            for sub in filter(lambda x: x.is_dir(), folder.iterdir()):
                if (sub / "setup.py").exists():
                    p = Package(sub)
                    p.find_migrations()
                    project.packages.append(p)
            return project


def main(path: Path) -> None:
    project_folder = Path(args.folder).resolve()
    project = analyze(project_folder)
    print(project)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Python project analyzer",
        description="Parses given project folder to get some useful insides",
    )
    parser.add_argument("folder")
    args = Args()
    main(Path(parser.parse_args(namespace=args).folder).resolve())
