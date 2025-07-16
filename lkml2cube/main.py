"""
Main CLI module for lkml2cube - LookML to Cube bidirectional converter.

This module provides the command-line interface for lkml2cube, offering three main commands:
- cubes: Convert LookML views to Cube definitions
- views: Convert LookML explores to Cube definitions with views
- explores: Generate LookML explores from Cube meta API

The CLI is built using Typer and provides rich console output with proper error handling.
Each command supports various options for parsing, output formatting, and file generation.
"""

import pprint
import rich
import typer
import yaml

from lkml2cube.parser.cube_api import meta_loader, parse_meta
from lkml2cube.parser.explores import parse_explores, generate_cube_joins
from lkml2cube.parser.loader import file_loader, write_files, write_lookml_files, print_summary
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
    """Main callback function for the lkml2cube CLI application.
    
    This function serves as the entry point for the CLI and provides
    general information about the tool. It sets up the global context
    for all subcommands.
    
    Note:
        This function is called automatically by Typer when the CLI is invoked.
        It doesn't perform any specific actions but serves as a placeholder
        for global CLI configuration.
    
    Example:
        $ lkml2cube --help
        # Shows help information for the entire CLI
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
    """Generate Cube model definitions from LookML view files.
    
    Converts LookML view files into Cube YAML definitions, handling dimensions,
    measures, and basic join relationships. This command focuses on generating
    cube definitions only (no views).
    
    Args:
        file_path (str): Path to the LookML file to process (supports glob patterns).
        parseonly (bool, optional): If True, only displays the parsed LookML as Python dict. Defaults to False.
        outputdir (str, optional): Directory where output files will be written. Defaults to ".".
        printonly (bool, optional): If True, prints YAML to stdout instead of writing files. Defaults to False.
        rootdir (str | None, optional): Root directory for resolving LookML includes. Defaults to None.
    
    Raises:
        typer.Exit: If no files are found at the specified path.
    
    Example:
        $ lkml2cube cubes models/orders.view.lkml --outputdir output/
        # Generates cube definitions in output/cubes/
        
        $ lkml2cube cubes models/orders.view.lkml --parseonly
        # Shows parsed LookML structure
        
        $ lkml2cube cubes models/orders.view.lkml --printonly
        # Prints YAML to console
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
    """Generate Cube model definitions with views from LookML explore files.
    
    Converts LookML explore files into Cube YAML definitions, creating both
    cube definitions and view definitions with join relationships. This command
    generates a complete Cube model with views that define how cubes relate to each other.
    
    Args:
        file_path (str): Path to the LookML explore file to process (supports glob patterns).
        parseonly (bool, optional): If True, only displays the parsed LookML as Python dict. Defaults to False.
        outputdir (str, optional): Directory where output files will be written. Defaults to ".".
        printonly (bool, optional): If True, prints YAML to stdout instead of writing files. Defaults to False.
        rootdir (str | None, optional): Root directory for resolving LookML includes. Defaults to None.
        use_explores_name (bool, optional): If True, uses explore names for cube view names. Defaults to False.
    
    Raises:
        typer.Exit: If no files are found at the specified path.
    
    Example:
        $ lkml2cube views models/explores.lkml --outputdir output/
        # Generates cubes and views in output/cubes/ and output/views/
        
        $ lkml2cube views models/explores.lkml --use-explores-name
        # Uses explore names for view naming
        
        $ lkml2cube views models/explores.lkml --parseonly
        # Shows parsed LookML structure
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


@app.command()
def explores(
    metaurl: Annotated[str, typer.Argument(help="The url for cube meta endpoint")],
    token: Annotated[str, typer.Option(help="JWT token for Cube meta")],
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
):
    """Generate LookML explores and views from Cube meta API.
    
    Fetches Cube model definitions from the meta API and converts them to
    production-ready LookML files. This command correctly maps:
    - Cube cubes (with sql_table/sql) → LookML views
    - Cube views (with aliasMember joins) → LookML explores
    
    Args:
        metaurl (str): URL to the Cube meta API endpoint (e.g., https://api.cube.dev/v1/meta).
        token (str): JWT authentication token for the Cube meta API.
        parseonly (bool, optional): If True, only displays the parsed Cube model as Python dict. Defaults to False.
        outputdir (str, optional): Directory where output files will be written. Defaults to ".".
        printonly (bool, optional): If True, prints YAML to stdout instead of writing files. Defaults to False.
    
    Raises:
        typer.Exit: If no response is received from the meta API.
        ValueError: If the token is invalid or API request fails.
    
    Example:
        $ lkml2cube explores "https://api.cube.dev/v1/meta" --token "jwt-token" --outputdir lookml/
        # Generates LookML views and explores in lookml/views/ and lookml/explores/
        
        $ lkml2cube explores "https://api.cube.dev/v1/meta" --token "jwt-token" --parseonly
        # Shows parsed Cube model structure
        
        $ lkml2cube explores "https://api.cube.dev/v1/meta" --token "jwt-token" --printonly
        # Prints generated LookML to console
    """

    cube_model = meta_loader(
        meta_url=metaurl,
        token=token,
    )

    if cube_model is None:
        console.print(f"No response received from: {metaurl}", style="bold red")
        raise typer.Exit()

    if parseonly:
        console.print(pprint.pformat(cube_model))
        return

    lookml_model = parse_meta(cube_model)

    if printonly:
        console.print(yaml.dump(lookml_model, allow_unicode=True))
        return

    summary = write_lookml_files(lookml_model, outputdir=outputdir)
    print_summary(summary)


if __name__ == "__main__":
    """Entry point for the CLI application when run as a script.
    
    This block is executed when the module is run directly (not imported).
    It starts the Typer application which handles command parsing and routing.
    """
    app()
