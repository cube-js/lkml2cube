# Table of Contents

* [lkml2cube.converter](#lkml2cube.converter)
  * [LookMLConverter](#lkml2cube.converter.LookMLConverter)
    * [\_\_init\_\_](#lkml2cube.converter.LookMLConverter.__init__)
    * [cubes](#lkml2cube.converter.LookMLConverter.cubes)
    * [views](#lkml2cube.converter.LookMLConverter.views)
    * [explores](#lkml2cube.converter.LookMLConverter.explores)
    * [set\_config](#lkml2cube.converter.LookMLConverter.set_config)
    * [get\_config](#lkml2cube.converter.LookMLConverter.get_config)
    * [validate\_files](#lkml2cube.converter.LookMLConverter.validate_files)
    * [clear\_cache](#lkml2cube.converter.LookMLConverter.clear_cache)
    * [\_\_repr\_\_](#lkml2cube.converter.LookMLConverter.__repr__)

<a id="lkml2cube.converter"></a>

# lkml2cube.converter

Main converter class for lkml2cube providing a Python API for LookML to Cube conversion.

This module provides a high-level interface for converting LookML models to Cube definitions
without requiring CLI usage. It maintains configuration state and provides the same
functionality as the CLI commands.

<a id="lkml2cube.converter.LookMLConverter"></a>

## LookMLConverter Objects

```python
class LookMLConverter()
```

Main converter class for LookML to Cube conversion operations.

This class provides a Python API for converting LookML models to Cube definitions,
maintaining configuration state and providing the same functionality as the CLI commands.

**Attributes**:

- `outputdir` _str_ - Directory where output files will be written.
- `rootdir` _str | None_ - Root directory for resolving LookML includes.
- `parseonly` _bool_ - If True, only parse and return Python dict representation.
- `printonly` _bool_ - If True, print YAML output to stdout instead of writing files.
- `use_explores_name` _bool_ - Whether to use explore names for cube view names.

<a id="lkml2cube.converter.LookMLConverter.__init__"></a>

#### \_\_init\_\_

```python
def __init__(outputdir: str = ".",
             rootdir: Optional[str] = None,
             parseonly: bool = False,
             printonly: bool = False,
             use_explores_name: bool = False)
```

Initialize the LookML converter with configuration options.

**Arguments**:

- `outputdir` _str, optional_ - Directory where output files will be written. Defaults to ".".
- `rootdir` _str | None, optional_ - Root directory for resolving LookML includes. Defaults to None.
- `parseonly` _bool, optional_ - If True, only parse and return Python dict representation. Defaults to False.
- `printonly` _bool, optional_ - If True, print YAML output to stdout instead of writing files. Defaults to False.
- `use_explores_name` _bool, optional_ - Whether to use explore names for cube view names. Defaults to False.
  

**Example**:

  >>> converter = LookMLConverter(outputdir="/tmp/output", rootdir="/lookml/models")
  >>> result = converter.cubes("models/*.lkml")
  >>> print(result['summary']['cubes'][0]['name'])
  'orders'

<a id="lkml2cube.converter.LookMLConverter.cubes"></a>

#### cubes

```python
def cubes(file_path: str) -> Dict[str, Any]
```

Generate cube definitions from LookML views.

Converts LookML views into Cube cube definitions, handling dimensions, measures,
and basic join relationships.

**Arguments**:

- `file_path` _str_ - Path to LookML file(s) to process (supports glob patterns).
  

**Returns**:

- `dict` - Result dictionary containing:
  - 'lookml_model': Parsed LookML model (if parseonly=True)
  - 'cube_def': Generated cube definitions
  - 'yaml_output': YAML string representation (if printonly=True)
  - 'summary': File generation summary (if files written)
  

**Raises**:

- `ValueError` - If no files are found at the specified path.
  

**Example**:

  >>> converter = LookMLConverter()
  >>> result = converter.cubes("models/orders.lkml")
  >>> print(result['cube_def']['cubes'][0]['name'])
  'orders'

<a id="lkml2cube.converter.LookMLConverter.views"></a>

#### views

```python
def views(file_path: str) -> Dict[str, Any]
```

Generate cube definitions with views from LookML explores.

Converts LookML explores into Cube definitions including both cubes and views
with join relationships.

**Arguments**:

- `file_path` _str_ - Path to LookML file(s) to process (supports glob patterns).
  

**Returns**:

- `dict` - Result dictionary containing:
  - 'lookml_model': Parsed LookML model (if parseonly=True)
  - 'cube_def': Generated cube definitions with views
  - 'yaml_output': YAML string representation (if printonly=True)
  - 'summary': File generation summary (if files written)
  

**Raises**:

- `ValueError` - If no files are found at the specified path.
  

**Example**:

  >>> converter = LookMLConverter(use_explores_name=True)
  >>> result = converter.views("models/explores.lkml")
  >>> print(len(result['cube_def']['views']))
  2

<a id="lkml2cube.converter.LookMLConverter.explores"></a>

#### explores

```python
def explores(metaurl: str, token: str) -> Dict[str, Any]
```

Generate LookML explores from Cube meta API.

Fetches Cube model from meta API and converts it to LookML explores,
correctly mapping Cube cubes to LookML views and Cube views to LookML explores.

**Arguments**:

- `metaurl` _str_ - URL to the Cube meta API endpoint.
- `token` _str_ - JWT token for Cube meta API authentication.
  

**Returns**:

- `dict` - Result dictionary containing:
  - 'cube_model': Raw Cube model from meta API (if parseonly=True)
  - 'lookml_model': Converted LookML model
  - 'yaml_output': YAML string representation (if printonly=True)
  - 'summary': File generation summary (if files written)
  

**Raises**:

- `ValueError` - If no response is received from the meta API.
- `Exception` - If API request fails or token is invalid.
  

**Example**:

  >>> converter = LookMLConverter(outputdir="/tmp/lookml")
  >>> result = converter.explores("https://api.cube.dev/v1/meta", "jwt-token")
  >>> print(len(result['lookml_model']['explores']))
  3

<a id="lkml2cube.converter.LookMLConverter.set_config"></a>

#### set\_config

```python
def set_config(outputdir: Optional[str] = None,
               rootdir: Optional[str] = None,
               parseonly: Optional[bool] = None,
               printonly: Optional[bool] = None,
               use_explores_name: Optional[bool] = None) -> None
```

Update converter configuration options.

**Arguments**:

- `outputdir` _str | None, optional_ - Directory where output files will be written.
- `rootdir` _str | None, optional_ - Root directory for resolving LookML includes.
- `parseonly` _bool | None, optional_ - If True, only parse and return Python dict representation.
- `printonly` _bool | None, optional_ - If True, print YAML output to stdout instead of writing files.
- `use_explores_name` _bool | None, optional_ - Whether to use explore names for cube view names.
  

**Example**:

  >>> converter = LookMLConverter()
  >>> converter.set_config(outputdir="/new/path", parseonly=True)
  >>> result = converter.cubes("models/*.lkml")
  # Will now parse only and use the new output directory

<a id="lkml2cube.converter.LookMLConverter.get_config"></a>

#### get\_config

```python
def get_config() -> Dict[str, Any]
```

Get current converter configuration.

**Returns**:

- `dict` - Current configuration settings.
  

**Example**:

  >>> converter = LookMLConverter(outputdir="/tmp")
  >>> config = converter.get_config()
  >>> print(config['outputdir'])
  '/tmp'

<a id="lkml2cube.converter.LookMLConverter.validate_files"></a>

#### validate\_files

```python
def validate_files(file_paths: List[str]) -> Dict[str, bool]
```

Validate that LookML files exist and can be loaded.

**Arguments**:

- `file_paths` _list[str]_ - List of file paths to validate.
  

**Returns**:

- `dict` - Dictionary mapping file paths to validation results.
  

**Example**:

  >>> converter = LookMLConverter()
  >>> results = converter.validate_files(["models/orders.lkml", "models/missing.lkml"])
  >>> print(results["models/orders.lkml"])
  True

<a id="lkml2cube.converter.LookMLConverter.clear_cache"></a>

#### clear\_cache

```python
def clear_cache() -> None
```

Clear the global file loader cache.

clears the visited_path cache used by the file_loader to prevent
circular includes. Useful for ensuring clean state between operations or
in testing scenarios.

**Example**:

  >>> converter = LookMLConverter()
  >>> converter.cubes("models/orders.lkml")  # Populates cache
  >>> converter.clear_cache()  # Clears cache
  >>> converter.cubes("models/orders.lkml")  # Loads fresh from disk

<a id="lkml2cube.converter.LookMLConverter.__repr__"></a>

#### \_\_repr\_\_

```python
def __repr__() -> str
```

Return string representation of the converter.

