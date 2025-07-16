# Table of Contents

* [lkml2cube.parser.cube\_api](#lkml2cube.parser.cube_api)
  * [meta\_loader](#lkml2cube.parser.cube_api.meta_loader)
  * [parse\_members](#lkml2cube.parser.cube_api.parse_members)
  * [parse\_meta](#lkml2cube.parser.cube_api.parse_meta)

<a id="lkml2cube.parser.cube_api"></a>

# lkml2cube.parser.cube\_api

<a id="lkml2cube.parser.cube_api.meta_loader"></a>

#### meta\_loader

```python
def meta_loader(meta_url: str, token: str) -> dict
```

Load the Cube meta API and return the model as a dictionary.

**Arguments**:

- `meta_url` _str_ - URL to the Cube meta API endpoint.
- `token` _str_ - Authentication token for the API.
  

**Returns**:

- `dict` - Cube model data from the meta API.
  

**Raises**:

- `ValueError` - If no valid token is provided.
- `Exception` - If the API request fails or returns non-200 status.
  

**Example**:

  >>> model = meta_loader('https://api.cube.dev/v1/meta', 'my-token')
  >>> print(model['cubes'][0]['name'])
  'orders'

<a id="lkml2cube.parser.cube_api.parse_members"></a>

#### parse\_members

```python
def parse_members(members: list) -> list
```

Parse measures and dimensions from the Cube meta model.

**Arguments**:

- `members` _list_ - List of dimension or measure definitions from Cube meta.
  

**Returns**:

- `list` - List of parsed members in LookML format.
  

**Example**:

  >>> members = [{'name': 'total_sales', 'type': 'sum', 'sql': 'amount'}]
  >>> parsed = parse_members(members)
  >>> print(parsed[0]['name'])
  'total_sales'

<a id="lkml2cube.parser.cube_api.parse_meta"></a>

#### parse\_meta

```python
def parse_meta(cube_model: dict) -> dict
```

Parse the Cube meta model and return a simplified version.

Separates Cube cubes (-> LookML views) from Cube views (-> LookML explores).

**Arguments**:

- `cube_model` _dict_ - Complete Cube model from meta API.
  

**Returns**:

- `dict` - LookML model with structure:
- `{'views'` - list, 'explores': list}
  

**Example**:

  >>> cube_model = {'cubes': [{'name': 'orders', 'sql_table': 'orders'}]}
  >>> lookml_model = parse_meta(cube_model)
  >>> print(lookml_model['views'][0]['name'])
  'orders'

