import pprint
import rich
import typer
import yaml

from lkml2cube.parser.explores import parse_explores, generate_cube_joins
from lkml2cube.parser.loader import file_loader, write_files, print_summary
from lkml2cube.parser.views import parse_view
from lkml2cube.parser.types import (
    folded_unicode,
    literal_unicode,
    folded_unicode_representer,
    literal_unicode_representer,
)
from typing_extensions import Annotated

app = typer.Typer()
console = rich.console.Console()
yaml.add_representer(folded_unicode, folded_unicode_representer)
yaml.add_representer(literal_unicode, literal_unicode_representer)


@app.callback()
def callback():
    """
    lkml2cube is a tool to convert LookML models into Cube data models.
    """
    # console.print(("lkml2cube is a tool to convert LookML models into Cube data models.\n"
    #             "Use lkml2cube --help to see usage."))
    pass


@app.command()
def cubes(
    file_path: Annotated[str, typer.Argument(help="The path for the file to read")],
    parseonly: Annotated[
        bool,
        typer.Option(
            help=(
                "When present it will only show the python"
                " dict read from the lookml file"
            )
        ),
    ] = False,
    outputdir: Annotated[
        str, typer.Option(help="The path for the output files to be generated")
    ] = ".",
    printonly: Annotated[
        bool, typer.Option(help="Print to stdout the parsed files")
    ] = False,
    rootdir: Annotated[
        str, typer.Option(help="The path to prepend to include paths")
    ] = None,
):
    """
    Generate cubes-only given a LookML file that contains LookML Views.
    """

    lookml_model = file_loader(file_path, rootdir)

    if lookml_model is None:
        console.print(f"No files were found on path: {file_path}", style="bold red")
        raise typer.Exit()

    if parseonly:
        console.print(pprint.pformat(lookml_model))
        return

    cube_def = parse_view(lookml_model)
    cube_def = generate_cube_joins(cube_def, lookml_model)

    if printonly:
        console.print(yaml.dump(cube_def, allow_unicode=True))
        return

    summary = write_files(cube_def, outputdir=outputdir)
    print_summary(summary)


@app.command()
def views(
    file_path: Annotated[str, typer.Argument(help="The path for the explore to read")],
    parseonly: Annotated[
        bool,
        typer.Option(
            help=(
                "When present it will only show the python"
                " dict read from the lookml file"
            )
        ),
    ] = False,
    outputdir: Annotated[
        str, typer.Option(help="The path for the output files to be generated")
    ] = ".",
    printonly: Annotated[
        bool, typer.Option(help="Print to stdout the parsed files")
    ] = False,
    rootdir: Annotated[
        str, typer.Option(help="The path to prepend to include paths")
    ] = None,
    use_explores_name: Annotated[
        bool, typer.Option(help="Use explore names for cube view names")
    ] = False,
):
    """
    Generate cubes-only given a LookML file that contains LookML Views.
    """

    lookml_model = file_loader(file_path, rootdir)

    if lookml_model is None:
        console.print(f"No files were found on path: {file_path}", style="bold red")
        raise typer.Exit()

    if parseonly:
        console.print(pprint.pformat(lookml_model))
        return

    cube_def = parse_explores(lookml_model, use_explores_name)

    if printonly:
        console.print(yaml.dump(cube_def, allow_unicode=True))
        return

    summary = write_files(cube_def, outputdir=outputdir)
    print_summary(summary)


if __name__ == "__main__":
    app()
