# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **🚨 IMPORTANT**: Always check `docs/lkml2cube_*.md` files BEFORE reading source code. Update docstrings and run `python scripts/generate_docs.py` after any code changes.

## Project Overview

lkml2cube is a Python CLI tool that converts LookML models into Cube data models. It uses the `lkml` library to parse LookML files and generates YAML-based Cube definitions.

## 📚 Documentation-First Development

**CRITICAL**: Before reading source code, always consult the generated documentation:

1. **Primary Reference**: Check `docs/lkml2cube_*.md` files first
2. **Implementation Details**: Read source code only if docs are insufficient
3. **Always Update**: Maintain docstrings and regenerate docs for any changes

📖 **Documentation Files**:
- `docs/lkml2cube_main.md` - CLI commands and usage
- `docs/lkml2cube_converter.md` - LookMLConverter Python API  
- `docs/lkml2cube_parser.md` - Parser module functions and classes

⚠️ **Required Workflow**: When modifying code → Update docstrings → Run `python scripts/generate_docs.py`

## Development Commands

### Environment Setup
- This project uses PDM for dependency management
- Install dependencies: `pdm install`
- Run tests: `pdm run pytest` or `pytest`

### Testing
- Tests are located in `tests/` directory
- Main test files: `tests/test_e2e.py`, `tests/test_converter.py`, `tests/test_explores_command.py`
- Test samples are in `tests/samples/` with both `lkml/` and `cubeml/` subdirectories
- Tests compare generated output against expected YAML files
- `test_converter.py` provides comprehensive unit tests for the `LookMLConverter` class

### Documentation Generation
- **Generate docs**: `python scripts/generate_docs.py`
- **MANDATORY**: Run after any function/method changes
- **Output**: Updates `docs/lkml2cube_*.md` files
- **Fallback**: Uses manual generation if pydoc-markdown fails
- **Optimization**: Optimizes output for LLM consumption

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

#### Main Entry Points
- `main.py` - Typer-based CLI with three commands: cubes, views, explores
- `converter.py` - Python API class `LookMLConverter` for programmatic usage
- Uses Rich for console output formatting

### Key Concepts
- **Cubes vs Views**: The `cubes` command only generates Cube model definitions, while `views` creates both cubes and views with join relationships
- **Explores**: LookML explores define join relationships equivalent to Cube's view definitions
- **Include Resolution**: Uses `--rootdir` parameter to resolve LookML `include:` statements
- **Cube API Mapping**: 
  - Cube cubes (with `sql_table`/`sql`) → LookML views
  - Cube views (with `aliasMember` joins) → LookML explores with join definitions
- **LookML Enhancement**: Generates production-ready LookML with includes, proper joins, primary keys, and drill fields

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

## Python API Usage

### LookMLConverter Class
The `LookMLConverter` class provides a Python API for programmatic usage without requiring CLI interaction:

```python
from lkml2cube.converter import LookMLConverter

# Initialize with configuration
converter = LookMLConverter(
    outputdir="/tmp/output",
    rootdir="/lookml/models",
    parseonly=False,
    printonly=False,
    use_explores_name=False
)

# Convert LookML views to Cube definitions
result = converter.cubes("models/orders.lkml")

# Convert LookML explores to Cube definitions with views
result = converter.views("models/explores.lkml")

# Generate LookML explores from Cube meta API
result = converter.explores("https://api.cube.dev/v1/meta", "jwt-token")
```

#### Key Methods
- `cubes(file_path)` - Equivalent to `lkml2cube cubes` command
- `views(file_path)` - Equivalent to `lkml2cube views` command  
- `explores(metaurl, token)` - Equivalent to `lkml2cube explores` command
- `set_config(**kwargs)` - Update configuration options
- `get_config()` - Get current configuration
- `validate_files(file_paths)` - Validate that files can be loaded

#### Configuration Management
The converter maintains state and can be reconfigured:

```python
# Update configuration
converter.set_config(parseonly=True, outputdir="/new/path")

# Get current configuration
config = converter.get_config()
```

#### Return Values
All methods return a dictionary with relevant data:
- `parseonly=True`: Returns parsed model structure
- `printonly=True`: Returns YAML output string
- Default: Returns file generation summary

## Documentation and Code Guidelines

### Documentation-First Approach

**IMPORTANT**: Always refer to the generated documentation in the `docs/` directory before reading source code:

1. **First**: Check `docs/lkml2cube_*.md` files for API documentation
2. **Second**: If implementation details are needed, then read the source code
3. **Always**: Maintain and update documentation when making changes

### Documentation Files

The project maintains auto-generated documentation:
- `docs/lkml2cube_main.md` - CLI commands and usage
- `docs/lkml2cube_converter.md` - LookMLConverter Python API
- `docs/lkml2cube_parser.md` - Parser module functions and classes

### Documentation Maintenance Workflow

**MANDATORY**: When adding new functions or modifying existing ones:

1. **Add/Update Google-style Docstrings**:
   ```python
   def my_function(param1: str, param2: int = 5) -> dict:
       """Brief one-line description.
       
       Detailed description if needed.
       
       Args:
           param1 (str): Description of param1.
           param2 (int, optional): Description of param2. Defaults to 5.
       
       Returns:
           dict: Description of return value.
       
       Raises:
           ValueError: Description of when this is raised.
       
       Example:
           >>> result = my_function("test", 10)
           >>> print(result['key'])
           'value'
       """
   ```

2. **Run Documentation Generation**:
   ```bash
   python scripts/generate_docs.py
   ```

3. **Verify Documentation**:
   - Check that `docs/` files are updated
   - Ensure docstrings are properly formatted
   - Verify examples work correctly

### Google-style Docstring Requirements

All public functions, methods, and classes MUST have Google-style docstrings including:
- **Clear one-line description**
- **Complete parameter documentation with types**
- **Return value descriptions**
- **Raised exceptions**
- **Simple usage examples**

### Documentation Generation Script

The `scripts/generate_docs.py` script:
- Automatically extracts docstrings from source code
- Generates markdown files in `docs/` directory
- Uses pydoc-markdown with manual fallback
- Optimizes output for LLM consumption
- Must be run after any function signature changes

### When to Update Documentation

Run `python scripts/generate_docs.py` when:
- Adding new functions or methods
- Modifying function signatures
- Changing parameter types or defaults
- Adding or removing classes
- Updating docstrings for clarity

### Code Review Checklist

Before committing changes:
- [ ] All new functions have Google-style docstrings
- [ ] Documentation generation script has been run
- [ ] Generated docs reflect the changes
- [ ] Examples in docstrings are accurate
- [ ] Parameter types and descriptions are correct

## 🔒 Enforcement Rules

**MANDATORY REQUIREMENTS**:

1. **Documentation First**: NEVER read source code without first checking the generated documentation in `docs/`
2. **Google-style Docstrings**: ALL public functions, methods, and classes MUST have complete Google-style docstrings
3. **Documentation Generation**: ALWAYS run `python scripts/generate_docs.py` after any code changes
4. **No Exceptions**: These rules apply to ALL code changes, no matter how small

**VIOLATION CONSEQUENCES**:
- Code changes without proper docstrings will be rejected
- Failure to generate documentation will result in incomplete assistance
- Not following documentation-first approach will lead to suboptimal code understanding

**COMPLIANCE VERIFICATION**:
- Check that `docs/` files are updated after changes
- Verify docstrings follow Google-style format exactly
- Ensure examples in docstrings are working and accurate
- Confirm all parameters and return values are documented

---

## 📝 Quick Reference

**Documentation Workflow**:
1. 📖 Check `docs/lkml2cube_*.md` first
2. 📝 Add/update Google-style docstrings 
3. 🔄 Run `python scripts/generate_docs.py`
4. ✅ Verify documentation is updated

**Key Files**:
- `docs/lkml2cube_main.md` - CLI documentation
- `docs/lkml2cube_converter.md` - Python API documentation
- `docs/lkml2cube_parser.md` - Parser module documentation
- `scripts/generate_docs.py` - Documentation generation script

**Remember**: Documentation first, code second. Always maintain docstrings!