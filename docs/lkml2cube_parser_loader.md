# Table of Contents

* [lkml2cube.parser.loader](#lkml2cube.parser.loader)
  * [substitute\_constants](#lkml2cube.parser.loader.substitute_constants)
  * [update\_namespace](#lkml2cube.parser.loader.update_namespace)
  * [file\_loader](#lkml2cube.parser.loader.file_loader)
  * [write\_single\_file](#lkml2cube.parser.loader.write_single_file)
  * [write\_files](#lkml2cube.parser.loader.write_files)
  * [write\_lookml\_files](#lkml2cube.parser.loader.write_lookml_files)
  * [print\_summary](#lkml2cube.parser.loader.print_summary)

<a id="lkml2cube.parser.loader"></a>

# lkml2cube.parser.loader

<a id="lkml2cube.parser.loader.substitute_constants"></a>

#### substitute\_constants

```python
def substitute_constants(obj, constants)
```

Recursively substitute constants in strings using @{constant_name} syntax.

**Arguments**:

- `obj` _any_ - The object to process (can be dict, list, str, or any other type).
- `constants` _dict_ - Dictionary mapping constant names to their values.
  

**Returns**:

- `any` - The processed object with constants substituted.
  

**Example**:

  >>> constants = {'city': 'Tokyo'}
  >>> obj = {'label': '@{city} Users'}
  >>> substitute_constants(obj, constants)
- `{'label'` - 'Tokyo Users'}

<a id="lkml2cube.parser.loader.update_namespace"></a>

#### update\_namespace

```python
def update_namespace(namespace, new_file)
```

Update namespace with new file content, merging lists and handling conflicts.

**Arguments**:

- `namespace` _dict | None_ - Existing namespace dictionary or None.
- `new_file` _dict_ - New file content to merge into namespace.
  

**Returns**:

- `dict` - Updated namespace with merged content.
  

**Example**:

  >>> namespace = {'views': [{'name': 'view1'}]}
  >>> new_file = {'views': [{'name': 'view2'}]}
  >>> update_namespace(namespace, new_file)
- `{'views'` - [{'name': 'view1'}, {'name': 'view2'}]}

<a id="lkml2cube.parser.loader.file_loader"></a>

#### file\_loader

```python
def file_loader(file_path_input, rootdir_param, namespace=None)
```

Load LookML files and resolve includes recursively.

**Arguments**:

- `file_path_input` _str_ - File path pattern to load (supports glob patterns).
- `rootdir_param` _str | None_ - Root directory for resolving includes.
- `namespace` _dict | None_ - Existing namespace to merge content into.
  

**Returns**:

- `dict` - Loaded LookML model with resolved includes.
  

**Raises**:

- `FileNotFoundError` - If specified file path cannot be found.
- `ValueError` - If LookML file cannot be parsed.
  

**Example**:

  >>> namespace = file_loader('models/*.lkml', '/path/to/root')
  >>> print(namespace['views'][0]['name'])
  'my_view'

<a id="lkml2cube.parser.loader.write_single_file"></a>

#### write\_single\_file

```python
def write_single_file(cube_def: dict,
                      outputdir: str,
                      subdir: str = "cubes",
                      file_name: str = "my_cubes.yml")
```

Write a single cube definition to a YAML file.

**Arguments**:

- `cube_def` _dict_ - Cube definition to write.
- `outputdir` _str_ - Output directory path.
- `subdir` _str, optional_ - Subdirectory within output directory. Defaults to "cubes".
- `file_name` _str, optional_ - Name of the output file. Defaults to "my_cubes.yml".
  

**Raises**:

- `OSError` - If output directory cannot be created or file cannot be written.
  

**Example**:

  >>> cube_def = {'cubes': [{'name': 'orders', 'sql_table': 'orders'}]}
  >>> write_single_file(cube_def, '/output', 'cubes', 'orders.yml')

<a id="lkml2cube.parser.loader.write_files"></a>

#### write\_files

```python
def write_files(cube_def, outputdir)
```

Write cube definitions to separate files organized by type.

**Arguments**:

- `cube_def` _dict_ - Cube definitions containing 'cubes' and/or 'views' keys.
- `outputdir` _str_ - Output directory path.
  

**Returns**:

- `dict` - Summary of written files with structure:
- `{'cubes'` - [{'name': str, 'path': str}], 'views': [{'name': str, 'path': str}]}
  

**Raises**:

- `Exception` - If no cube definition is provided.
- `OSError` - If output directory cannot be created or files cannot be written.
  

**Example**:

  >>> cube_def = {'cubes': [{'name': 'orders'}], 'views': [{'name': 'orders_view'}]}
  >>> summary = write_files(cube_def, '/output')
  >>> print(summary['cubes'][0]['name'])
  'orders'

<a id="lkml2cube.parser.loader.write_lookml_files"></a>

#### write\_lookml\_files

```python
def write_lookml_files(lookml_model, outputdir)
```

Write LookML model to files in the output directory.

**Arguments**:

- `lookml_model` _dict_ - LookML model containing 'views' and/or 'explores' keys.
- `outputdir` _str_ - Output directory path.
  

**Returns**:

- `dict` - Summary of written files with structure:
- `{'views'` - [{'name': str, 'path': str}], 'explores': [{'name': str, 'path': str}]}
  

**Raises**:

- `Exception` - If no LookML model is provided.
- `OSError` - If output directory cannot be created or files cannot be written.
  

**Example**:

  >>> lookml_model = {'views': [{'name': 'orders'}], 'explores': [{'name': 'orders_explore'}]}
  >>> summary = write_lookml_files(lookml_model, '/output')
  >>> print(summary['views'][0]['name'])
  'orders'

<a id="lkml2cube.parser.loader.print_summary"></a>

#### print\_summary

```python
def print_summary(summary)
```

Print a formatted summary of generated files using Rich tables.

**Arguments**:

- `summary` _dict_ - Summary dictionary containing file information with keys
  'cubes', 'views', and/or 'explores', each containing lists of
- `{'name'` - str, 'path': str} dictionaries.
  

**Example**:

  >>> summary = {'cubes': [{'name': 'orders', 'path': '/output/cubes/orders.yml'}]}
  >>> print_summary(summary)
  # Displays a formatted table showing the generated files

