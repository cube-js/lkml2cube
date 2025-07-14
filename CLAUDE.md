# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

lkml2cube is a Python CLI tool that converts LookML models into Cube data models. It uses the `lkml` library to parse LookML files and generates YAML-based Cube definitions.

## Development Commands

### Environment Setup
- This project uses PDM for dependency management
- Install dependencies: `pdm install`
- Run tests: `pdm run pytest` or `pytest`

### Testing
- Tests are located in `tests/` directory
- Main test file: `tests/test_e2e.py`
- Test samples are in `tests/samples/` with both `lkml/` and `cubeml/` subdirectories
- Tests compare generated output against expected YAML files

### CLI Usage
The tool provides three main commands:
- `lkml2cube cubes` - Converts LookML views to Cube definitions (cubes only)
- `lkml2cube views` - Converts LookML explores to Cube definitions (cubes + views)
- `lkml2cube explores` - Generates LookML explores from Cube meta API (correctly maps Cube cubes→LookML views, Cube views→LookML explores)

## Architecture

### Core Components

#### Parser Module (`lkml2cube/parser/`)
- `loader.py` - File loading, writing, and summary utilities (includes LookML generation)
- `views.py` - Converts LookML views to Cube definitions
- `explores.py` - Handles explore parsing and join generation
- `cube_api.py` - Interfaces with Cube meta API, correctly separates cubes vs views
- `types.py` - Custom YAML types for proper formatting

#### Main Entry Point
- `main.py` - Typer-based CLI with three commands: cubes, views, explores
- Uses Rich for console output formatting

### Key Concepts
- **Cubes vs Views**: The `cubes` command only generates Cube model definitions, while `views` creates both cubes and views with join relationships
- **Explores**: LookML explores define join relationships equivalent to Cube's view definitions
- **Include Resolution**: Uses `--rootdir` parameter to resolve LookML `include:` statements
- **Cube API Mapping**: 
  - Cube cubes (with `sql_table`/`sql`) → LookML views
  - Cube views (with `aliasMember` joins) → LookML explores with join definitions

### File Structure
- `examples/` - Contains sample output files (cubes and views)
- `tests/samples/` - Test fixtures with both LookML input and expected Cube output
- `lkml2cube/` - Main source code
- `dist/` - Built distribution files

## Development Notes

### YAML Formatting
The tool uses custom YAML representers for proper formatting:
- `folded_unicode` and `literal_unicode` types for multi-line strings
- Configured in `main.py` with `yaml.add_representer()`

### CLI Options
Common options across commands:
- `--parseonly` - Shows parsed LookML as Python dict
- `--printonly` - Prints generated YAML to stdout
- `--outputdir` - Directory for output files
- `--rootdir` - Base path for resolving includes