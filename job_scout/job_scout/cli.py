"""CLI entry point for Job Scout."""

import typer

app = typer.Typer(help="Local-first job application intelligence assistant.")


@app.command()
def status() -> None:
    """Show scaffold status."""
    typer.echo("job-scout scaffold initialized")


if __name__ == "__main__":
    app()
