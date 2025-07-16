# lkml2cube.converter

Main converter class for lkml2cube providing a Python API for LookML to Cube conversion.

This module provides a high-level interface for converting LookML models to Cube definitions
without requiring CLI usage. It maintains configuration state and provides the same
functionality as the CLI commands.

#### Classes

##### LookMLConverter
Main converter class for LookML to Cube conversion operations.
    
    This class provides a Python API for converting LookML models to Cube definitions,
    maintaining configuration state and providing the same functionality as the CLI commands.
    
    Attributes:
        outputdir (str): Directory where output files will be written.
        rootdir (str | None): Root directory for resolving LookML includes.
        parseonly (bool): If True, only parse and return Python dict representation.
        printonly (bool): If True, print YAML output to stdout instead of writing files.
        use_explores_name (bool): Whether to use explore names for cube view names.

**Methods:**

- `__init__()`: Initialize the LookML converter with configuration options
- `cubes()`: Generate cube definitions from LookML views
- `explores()`: Generate LookML explores from Cube meta API
- `get_config()`: Get current converter configuration
- `set_config()`: Update converter configuration options
- `validate_files()`: Validate that LookML files exist and can be loaded
- `views()`: Generate cube definitions with views from LookML explores
