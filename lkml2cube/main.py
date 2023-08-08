import pprint
import typer

from lkml2cube.parser.loader import file_loader
from lkml2cube.parser.views import parse_view
from typing_extensions import Annotated

app = typer.Typer()

@app.callback()
def callback():
    """
    lkml2cube is a tool to convert LookML models into Cube data models.
    """
    typer.echo(("lkml2cube is a tool to convert LookML models into Cube data models.\n"
                "Use lkml2cube --help to see usage."))

@app.command()
def cubes(
    file_path: Annotated[str, typer.Argument(help="The path for the file to read")],
    parseonly: Annotated[bool, typer.Option(help=("When present it will only show the python"
                                                  " dict read from the lookml file"))] = False
    ):
    """
    Generate cubes-only given a LookML file that contains LookML Views.
    """
    
    lookml_model = file_loader(file_path)
    if parseonly:
        typer.echo(pprint.pformat(lookml_model))
        return
    
    typer.echo(parse_view(lookml_model))

if __name__ == "__main__":
    app()

