import pprint
import typer
import yaml

from lkml2cube.parser.explores import parse_explores, generate_cube_joins
from lkml2cube.parser.loader import file_loader, write_files
from lkml2cube.parser.views import parse_view
from typing_extensions import Annotated

app = typer.Typer()

@app.callback()
def callback():
    """
    lkml2cube is a tool to convert LookML models into Cube data models.
    """
    # typer.echo(("lkml2cube is a tool to convert LookML models into Cube data models.\n"
    #             "Use lkml2cube --help to see usage."))
    pass

@app.command()
def cubes(
        file_path: Annotated[str, typer.Argument(help="The path for the file to read")],
        parseonly: Annotated[bool, typer.Option(help=("When present it will only show the python"
                                                      " dict read from the lookml file"))] = False,
        outputdir: Annotated[str, typer.Option(help="The path for the output files to be generated")] = '.',
        printonly: Annotated[bool, typer.Option(help="Print to stdout the parsed files")] = False,
    ):
    """
    Generate cubes-only given a LookML file that contains LookML Views.
    """
    
    lookml_model = file_loader(file_path)
    if parseonly:
        typer.echo(pprint.pformat(lookml_model))
        return
    
    cube_def = parse_view(lookml_model)
    cube_def = generate_cube_joins(cube_def, lookml_model)
    
    if printonly:
        typer.echo(yaml.dump(cube_def))
        return
    
    write_files(cube_def, outputdir=outputdir)
    


@app.command()
def views(
        file_path: Annotated[str, typer.Argument(help="The path for the explore to read")],
        parseonly: Annotated[bool, typer.Option(help=("When present it will only show the python"
                                                      " dict read from the lookml file"))] = False,
        outputdir: Annotated[str, typer.Option(help="The path for the output files to be generated")] = '.',
        printonly: Annotated[bool, typer.Option(help="Print to stdout the parsed files")] = False,
    ):
    """
    Generate cubes-only given a LookML file that contains LookML Views.
    """
    
    lookml_model = file_loader(file_path)
    if parseonly:
        typer.echo(pprint.pformat(lookml_model))
        return
    
    cube_def = parse_explores(lookml_model)

    if printonly:
        typer.echo(yaml.dump(cube_def))
        return
    
    write_files(cube_def, outputdir=outputdir)

if __name__ == "__main__":
    app()

