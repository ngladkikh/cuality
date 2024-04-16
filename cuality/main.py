from pathlib import Path

import click
import os

from cuality.feature_delivery import main as feature_delivery
from cuality.analyze import main as analyze
from cuality.lint_ignores import lint_ignores


@click.group()
def cli():
    pass


@cli.command(help="Generate feature delivery statistics")
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True),
    default=os.getcwd(),
    help="Path to the Git repository.",
)
@click.option("--trunk", "-t", default="main", help="Name of the trunk branch.")
def statistics(path: click.Path, trunk: str):
    """Compute and display statistics about feature delivery times."""
    click.echo(
        f"Analyzing feature delivery statistics for repository at {path} targeting trunk branch '{trunk}'..."
    )
    feature_delivery(path, trunk)


@cli.command(help="Parses given project folder to get some useful insides")
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True),
    default=os.getcwd(),
    help="Path to the Git repository.",
)
def analyze(path: click.Path):
    analyze(path)


@cli.command(help="Calculates linters ignore lines stat to overall lines")
@click.argument("project", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", default="ignore_stat.csv", help="Output file name")
def ignore_stat(project: click.Path, output: str) -> None:
    output = Path(output)
    lint_ignores(project, output)


if __name__ == "__main__":
    cli()
