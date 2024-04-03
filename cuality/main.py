import click
import os

from cuality.feature_delivery import main as feature_delivery


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


if __name__ == "__main__":
    cli()
