# Table of Contents

* [lkml2cube.parser.explores](#lkml2cube.parser.explores)
  * [snakify](#lkml2cube.parser.explores.snakify)
  * [build\_cube\_name\_look\_up](#lkml2cube.parser.explores.build_cube_name_look_up)
  * [get\_cube\_from\_cube\_def](#lkml2cube.parser.explores.get_cube_from_cube_def)
  * [get\_cube\_names\_from\_join\_condition](#lkml2cube.parser.explores.get_cube_names_from_join_condition)
  * [traverse\_graph](#lkml2cube.parser.explores.traverse_graph)
  * [generate\_cube\_joins](#lkml2cube.parser.explores.generate_cube_joins)
  * [generate\_cube\_views](#lkml2cube.parser.explores.generate_cube_views)
  * [parse\_explores](#lkml2cube.parser.explores.parse_explores)

<a id="lkml2cube.parser.explores"></a>

# lkml2cube.parser.explores

<a id="lkml2cube.parser.explores.snakify"></a>

#### snakify

```python
def snakify(s)
```

Convert a string to snake_case format.

**Arguments**:

- `s` _str_ - String to convert to snake_case.
  

**Returns**:

- `str` - Snake_case version of the input string.
  

**Example**:

  >>> snakify('MyViewName')
  'my_view_name'
  >>> snakify('Order-Details')
  'order_details'

<a id="lkml2cube.parser.explores.build_cube_name_look_up"></a>

#### build\_cube\_name\_look\_up

```python
def build_cube_name_look_up(cube_def)
```

Build a lookup dictionary for cube names in the cube definition.

**Arguments**:

- `cube_def` _dict_ - Cube definition containing 'cubes' list.
  

**Notes**:

  modifies the cube_def dictionary in place by adding
  a 'cube_name_look_up' key if it doesn't exist.
  

**Example**:

  >>> cube_def = {'cubes': [{'name': 'orders'}, {'name': 'customers'}]}
  >>> build_cube_name_look_up(cube_def)
  >>> print('orders' in cube_def['cube_name_look_up'])
  True

<a id="lkml2cube.parser.explores.get_cube_from_cube_def"></a>

#### get\_cube\_from\_cube\_def

```python
def get_cube_from_cube_def(cube_def, cube_name)
```

Get a cube definition by name from the cube definition.

**Arguments**:

- `cube_def` _dict_ - Cube definition containing 'cubes' list.
- `cube_name` _str_ - Name of the cube to retrieve.
  

**Returns**:

  dict | None: Cube definition if found, None otherwise.
  

**Example**:

  >>> cube_def = {'cubes': [{'name': 'orders', 'sql_table': 'orders'}]}
  >>> cube = get_cube_from_cube_def(cube_def, 'orders')
  >>> print(cube['sql_table'])
  'orders'

<a id="lkml2cube.parser.explores.get_cube_names_from_join_condition"></a>

#### get\_cube\_names\_from\_join\_condition

```python
def get_cube_names_from_join_condition(join_condition)
```

Extract cube names from a join condition SQL string.

**Arguments**:

- `join_condition` _str_ - SQL join condition containing cube references.
  

**Returns**:

- `list[str]` - List of cube names found in the join condition.
  

**Example**:

  >>> join_condition = '${orders.customer_id} = ${customers.id}'
  >>> get_cube_names_from_join_condition(join_condition)
  ['orders', 'customers']

<a id="lkml2cube.parser.explores.traverse_graph"></a>

#### traverse\_graph

```python
def traverse_graph(join_paths, cube_left, cube_right)
```

Find the shortest path between two cubes using BFS traversal.

**Arguments**:

- `join_paths` _dict_ - Dictionary mapping cube names to their connected cubes.
- `cube_left` _str_ - Starting cube name.
- `cube_right` _str_ - Target cube name.
  

**Returns**:

- `str` - Dot-separated path from cube_left to cube_right.
  

**Example**:

  >>> join_paths = {'orders': ['customers'], 'customers': ['addresses']}
  >>> traverse_graph(join_paths, 'orders', 'addresses')
  'orders.customers.addresses'

<a id="lkml2cube.parser.explores.generate_cube_joins"></a>

#### generate\_cube\_joins

```python
def generate_cube_joins(cube_def, lookml_model)
```

Generate cube join definitions from LookML explores.

**Arguments**:

- `cube_def` _dict_ - Existing cube definition to modify.
- `lookml_model` _dict_ - LookML model containing explores with joins.
  

**Returns**:

- `dict` - Updated cube definition with join information added to cubes.
  

**Raises**:

- `Exception` - If cube referenced in explores is not found.
  

**Example**:

  >>> cube_def = {'cubes': [{'name': 'orders'}, {'name': 'customers'}]}
  >>> lookml_model = {'explores': [{'joins': [{'name': 'customers', 'sql_on': '${orders.customer_id} = ${customers.id}', 'relationship': 'many_to_one'}]}]}
  >>> updated_def = generate_cube_joins(cube_def, lookml_model)
  >>> print(updated_def['cubes'][1]['joins'][0]['name'])
  'orders'

<a id="lkml2cube.parser.explores.generate_cube_views"></a>

#### generate\_cube\_views

```python
def generate_cube_views(cube_def, lookml_model, use_explores_name=False)
```

Generate Cube view definitions from LookML explores.

**Arguments**:

- `cube_def` _dict_ - Cube definition to add views to.
- `lookml_model` _dict_ - LookML model containing explores.
- `use_explores_name` _bool, optional_ - Whether to use explore names as view names. Defaults to False.
  

**Returns**:

- `dict` - Updated cube definition with view definitions added.
  

**Example**:

  >>> cube_def = {'cubes': [{'name': 'orders'}]}
  >>> lookml_model = {'explores': [{'name': 'orders_explore', 'label': 'Orders Analysis'}]}
  >>> updated_def = generate_cube_views(cube_def, lookml_model)
  >>> print(updated_def['views'][0]['name'])
  'orders_analysis'

<a id="lkml2cube.parser.explores.parse_explores"></a>

#### parse\_explores

```python
def parse_explores(lookml_model, use_explores_name=False)
```

Parse LookML explores into Cube definitions with joins and views.

**Arguments**:

- `lookml_model` _dict_ - LookML model containing views and explores.
- `use_explores_name` _bool, optional_ - Whether to use explore names as view names. Defaults to False.
  

**Returns**:

- `dict` - Complete cube definition with cubes, joins, and views.
  

**Raises**:

- `Exception` - If no explores are found in the LookML model.
  

**Example**:

  >>> lookml_model = {
  ...     'views': [{'name': 'orders', 'sql_table_name': 'orders'}],
  ...     'explores': [{'name': 'orders_explore', 'joins': [{'name': 'customers', 'sql_on': '${orders.customer_id} = ${customers.id}', 'relationship': 'many_to_one'}]}]
  ... }
  >>> cube_def = parse_explores(lookml_model)
  >>> print(len(cube_def['cubes']))
  1
  >>> print(len(cube_def['views']))
  1

