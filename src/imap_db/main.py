"""Main module."""

from typing import Annotated

# cli
import typer

app = typer.Typer()
globalState = {"verbose": False}


@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.callback()
def main(verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False):
    if verbose:
        globalState["verbose"] = True


if __name__ == "__main__":
    app()  # pragma: no cover
