# Table of Contents

* [lkml2cube.parser.views](#lkml2cube.parser.views)
  * [parse\_view](#lkml2cube.parser.views.parse_view)

<a id="lkml2cube.parser.views"></a>

# lkml2cube.parser.views

<a id="lkml2cube.parser.views.parse_view"></a>

#### parse\_view

```python
def parse_view(lookml_model, raise_when_views_not_present=True)
```

Parse LookML views into Cube definitions.

Converts LookML view definitions into Cube format, handling dimensions, measures,
view inheritance, and various LookML-specific features like tiers and drill fields.

**Arguments**:

- `lookml_model` _dict_ - LookML model containing views to parse.
- `raise_when_views_not_present` _bool, optional_ - Whether to raise an exception
  when no views are found. Defaults to True.
  

**Returns**:

- `dict` - Cube definitions with structure:
- `{'cubes'` - [{'name': str, 'description': str, 'dimensions': list, 'measures': list, 'joins': list}]}
  

**Raises**:

- `Exception` - If raise_when_views_not_present is True and no views are found,
  or if required dimension properties are missing.
  

**Example**:

  >>> lookml_model = {
  ...     'views': [{
  ...         'name': 'orders',
  ...         'sql_table_name': 'public.orders',
  ...         'dimensions': [{'name': 'id', 'type': 'number', 'sql': '${TABLE}.id'}],
  ...         'measures': [{'name': 'count', 'type': 'count'}]
  ...     }]
  ... }
  >>> cube_def = parse_view(lookml_model)
  >>> print(cube_def['cubes'][0]['name'])
  'orders'

