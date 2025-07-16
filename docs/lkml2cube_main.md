# Table of Contents

* [lkml2cube.main](#lkml2cube.main)
  * [callback](#lkml2cube.main.callback)
  * [cubes](#lkml2cube.main.cubes)
  * [views](#lkml2cube.main.views)
  * [explores](#lkml2cube.main.explores)

<a id="lkml2cube.main"></a>

# lkml2cube.main

Main CLI module for lkml2cube - LookML to Cube bidirectional converter.

This module provides the command-line interface for lkml2cube, offering three main commands:
- cubes: Convert LookML views to Cube definitions
- views: Convert LookML explores to Cube definitions with views
- explores: Generate LookML explores from Cube meta API

The CLI is built using Typer and provides rich console output with proper error handling.
Each command supports various options for parsing, output formatting, and file generation.

<a id="lkml2cube.main.callback"></a>

#### callback

```python
@app.callback()
def callback()
```

Main callback function for the lkml2cube CLI application.

serves as the entry point for the CLI and provides
general information about the tool. It sets up the global context
for all subcommands.

**Notes**:

  is called automatically by Typer when the CLI is invoked.
  It doesn't perform any specific actions but serves as a placeholder
  for global CLI configuration.
  

**Example**:

  $ lkml2cube --help
  # Shows help information for the entire CLI

<a id="lkml2cube.main.cubes"></a>

#### cubes

```python
@app.command()
def cubes(
    file_path: Annotated[str,
                         typer.Argument(help="The path for the file to read")],
    parseonly: Annotated[
        bool,
        typer.Option(help=("When present it will only show the python"
                           " dict read from the lookml file")),
    ] = False,
    outputdir: Annotated[
        str,
        typer.Option(
            help="The path for the output files to be generated")] = ".",
    printonly: Annotated[bool,
                         typer.Option(
                             help="Print to stdout the parsed files")] = False,
    rootdir: Annotated[
        str,
        typer.Option(help="The path to prepend to include paths")] = None)
```

Generate Cube model definitions from LookML view files.

Converts LookML view files into Cube YAML definitions, handling dimensions,
measures, and basic join relationships. This command focuses on generating
cube definitions only (no views).

**Arguments**:

- `file_path` _str_ - Path to the LookML file to process (supports glob patterns).
- `parseonly` _bool, optional_ - If True, only displays the parsed LookML as Python dict. Defaults to False.
- `outputdir` _str, optional_ - Directory where output files will be written. Defaults to ".".
- `printonly` _bool, optional_ - If True, prints YAML to stdout instead of writing files. Defaults to False.
- `rootdir` _str | None, optional_ - Root directory for resolving LookML includes. Defaults to None.
  

**Raises**:

- `typer.Exit` - If no files are found at the specified path.
  

**Example**:

  $ lkml2cube cubes models/orders.view.lkml --outputdir output/
  # Generates cube definitions in output/cubes/
  
  $ lkml2cube cubes models/orders.view.lkml --parseonly
  # Shows parsed LookML structure
  
  $ lkml2cube cubes models/orders.view.lkml --printonly
  # Prints YAML to console

<a id="lkml2cube.main.views"></a>

#### views

```python
@app.command()
def views(
    file_path: Annotated[str,
                         typer.Argument(
                             help="The path for the explore to read")],
    parseonly: Annotated[
        bool,
        typer.Option(help=("When present it will only show the python"
                           " dict read from the lookml file")),
    ] = False,
    outputdir: Annotated[
        str,
        typer.Option(
            help="The path for the output files to be generated")] = ".",
    printonly: Annotated[bool,
                         typer.Option(
                             help="Print to stdout the parsed files")] = False,
    rootdir: Annotated[
        str, typer.Option(help="The path to prepend to include paths")] = None,
    use_explores_name: Annotated[
        bool,
        typer.Option(help="Use explore names for cube view names")] = False)
```

Generate Cube model definitions with views from LookML explore files.

Converts LookML explore files into Cube YAML definitions, creating both
cube definitions and view definitions with join relationships. This command
generates a complete Cube model with views that define how cubes relate to each other.

**Arguments**:

- `file_path` _str_ - Path to the LookML explore file to process (supports glob patterns).
- `parseonly` _bool, optional_ - If True, only displays the parsed LookML as Python dict. Defaults to False.
- `outputdir` _str, optional_ - Directory where output files will be written. Defaults to ".".
- `printonly` _bool, optional_ - If True, prints YAML to stdout instead of writing files. Defaults to False.
- `rootdir` _str | None, optional_ - Root directory for resolving LookML includes. Defaults to None.
- `use_explores_name` _bool, optional_ - If True, uses explore names for cube view names. Defaults to False.
  

**Raises**:

- `typer.Exit` - If no files are found at the specified path.
  

**Example**:

  $ lkml2cube views models/explores.lkml --outputdir output/
  # Generates cubes and views in output/cubes/ and output/views/
  
  $ lkml2cube views models/explores.lkml --use-explores-name
  # Uses explore names for view naming
  
  $ lkml2cube views models/explores.lkml --parseonly
  # Shows parsed LookML structure

<a id="lkml2cube.main.explores"></a>

#### explores

```python
@app.command()
def explores(
    metaurl: Annotated[str,
                       typer.Argument(help="The url for cube meta endpoint")],
    token: Annotated[str, typer.Option(help="JWT token for Cube meta")],
    parseonly: Annotated[
        bool,
        typer.Option(help=("When present it will only show the python"
                           " dict read from the lookml file")),
    ] = False,
    outputdir: Annotated[
        str,
        typer.Option(
            help="The path for the output files to be generated")] = ".",
    printonly: Annotated[
        bool, typer.Option(help="Print to stdout the parsed files")] = False)
```

Generate LookML explores and views from Cube meta API.

Fetches Cube model definitions from the meta API and converts them to
production-ready LookML files. This command correctly maps:
- Cube cubes (with sql_table/sql) → LookML views
- Cube views (with aliasMember joins) → LookML explores

**Arguments**:

- `metaurl` _str_ - URL to the Cube meta API endpoint (e.g., https://api.cube.dev/v1/meta).
- `token` _str_ - JWT authentication token for the Cube meta API.
- `parseonly` _bool, optional_ - If True, only displays the parsed Cube model as Python dict. Defaults to False.
- `outputdir` _str, optional_ - Directory where output files will be written. Defaults to ".".
- `printonly` _bool, optional_ - If True, prints YAML to stdout instead of writing files. Defaults to False.
  

**Raises**:

- `typer.Exit` - If no response is received from the meta API.
- `ValueError` - If the token is invalid or API request fails.
  

**Example**:

  $ lkml2cube explores "https://api.cube.dev/v1/meta" --token "jwt-token" --outputdir lookml/
  # Generates LookML views and explores in lookml/views/ and lookml/explores/
  
  $ lkml2cube explores "https://api.cube.dev/v1/meta" --token "jwt-token" --parseonly
  # Shows parsed Cube model structure
  
  $ lkml2cube explores "https://api.cube.dev/v1/meta" --token "jwt-token" --printonly
  # Prints generated LookML to console

