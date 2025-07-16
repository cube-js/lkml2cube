# lkml2cube.parser

## Submodules

### lkml2cube.parser.cube_api

#### Functions

##### meta_loader()
Load the Cube meta API and return the model as a dictionary.
    
    Args:
        meta_url (str): URL to the Cube meta API endpoint.
        token (str): Authentication token for the API.
    
    Returns:
        dict: Cube model data from the meta API.
    
    Raises:
        ValueError: If no valid token is provided.
        Exception: If the API request fails or returns non-200 status.
    
    Example:
        >>> model = meta_loader('https://api.cube.dev/v1/meta', 'my-token')
        >>> print(model['cubes'][0]['name'])
        'orders'

##### parse_members()
Parse measures and dimensions from the Cube meta model.
    
    Args:
        members (list): List of dimension or measure definitions from Cube meta.
    
    Returns:
        list: List of parsed members in LookML format.
    
    Example:
        >>> members = [{'name': 'total_sales', 'type': 'sum', 'sql': 'amount'}]
        >>> parsed = parse_members(members)
        >>> print(parsed[0]['name'])
        'total_sales'

##### parse_meta()
Parse the Cube meta model and return a simplified version.
    
    Separates Cube cubes (-> LookML views) from Cube views (-> LookML explores).
    
    Args:
        cube_model (dict): Complete Cube model from meta API.
    
    Returns:
        dict: LookML model with structure:
            {'views': list, 'explores': list}
    
    Example:
        >>> cube_model = {'cubes': [{'name': 'orders', 'sql_table': 'orders'}]}
        >>> lookml_model = parse_meta(cube_model)
        >>> print(lookml_model['views'][0]['name'])
        'orders'


### lkml2cube.parser.explores

#### Functions

##### build_cube_name_look_up()
Build a lookup dictionary for cube names in the cube definition.
    
    Args:
        cube_def (dict): Cube definition containing 'cubes' list.
    
    Note:
        modifies the cube_def dictionary in place by adding
        a 'cube_name_look_up' key if it doesn't exist.
    
    Example:
        >>> cube_def = {'cubes': [{'name': 'orders'}, {'name': 'customers'}]}
        >>> build_cube_name_look_up(cube_def)
        >>> print('orders' in cube_def['cube_name_look_up'])
        True

##### generate_cube_joins()
Generate cube join definitions from LookML explores.
    
    Args:
        cube_def (dict): Existing cube definition to modify.
        lookml_model (dict): LookML model containing explores with joins.
    
    Returns:
        dict: Updated cube definition with join information added to cubes.
    
    Raises:
        Exception: If cube referenced in explores is not found.
    
    Example:
        >>> cube_def = {'cubes': [{'name': 'orders'}, {'name': 'customers'}]}
        >>> lookml_model = {'explores': [{'joins': [{'name': 'customers', 'sql_on': '${orders.customer_id} = ${customers.id}', 'relationship': 'many_to_one'}]}]}
        >>> updated_def = generate_cube_joins(cube_def, lookml_model)
        >>> print(updated_def['cubes'][1]['joins'][0]['name'])
        'orders'

##### generate_cube_views()
Generate Cube view definitions from LookML explores.
    
    Args:
        cube_def (dict): Cube definition to add views to.
        lookml_model (dict): LookML model containing explores.
        use_explores_name (bool, optional): Whether to use explore names as view names. Defaults to False.
    
    Returns:
        dict: Updated cube definition with view definitions added.
    
    Example:
        >>> cube_def = {'cubes': [{'name': 'orders'}]}
        >>> lookml_model = {'explores': [{'name': 'orders_explore', 'label': 'Orders Analysis'}]}
        >>> updated_def = generate_cube_views(cube_def, lookml_model)
        >>> print(updated_def['views'][0]['name'])
        'orders_analysis'

##### get_cube_from_cube_def()
Get a cube definition by name from the cube definition.
    
    Args:
        cube_def (dict): Cube definition containing 'cubes' list.
        cube_name (str): Name of the cube to retrieve.
    
    Returns:
        dict | None: Cube definition if found, None otherwise.
    
    Example:
        >>> cube_def = {'cubes': [{'name': 'orders', 'sql_table': 'orders'}]}
        >>> cube = get_cube_from_cube_def(cube_def, 'orders')
        >>> print(cube['sql_table'])
        'orders'

##### get_cube_names_from_join_condition()
Extract cube names from a join condition SQL string.
    
    Args:
        join_condition (str): SQL join condition containing cube references.
    
    Returns:
        list[str]: List of cube names found in the join condition.
    
    Example:
        >>> join_condition = '${orders.customer_id} = ${customers.id}'
        >>> get_cube_names_from_join_condition(join_condition)
        ['orders', 'customers']

##### parse_explores()
Parse LookML explores into Cube definitions with joins and views.
    
    Args:
        lookml_model (dict): LookML model containing views and explores.
        use_explores_name (bool, optional): Whether to use explore names as view names. Defaults to False.
    
    Returns:
        dict: Complete cube definition with cubes, joins, and views.
    
    Raises:
        Exception: If no explores are found in the LookML model.
    
    Example:
        >>> lookml_model = {
        ...     'views': [{'name': 'orders', 'sql_table_name': 'orders'}],
        ...     'explores': [{'name': 'orders_explore', 'joins': [{'name': 'customers', 'sql_on': '${orders.customer_id} = ${customers.id}', 'relationship': 'many_to_one'}]}]
        ... }
        >>> cube_def = parse_explores(lookml_model)
        >>> print(len(cube_def['cubes']))
        1
        >>> print(len(cube_def['views']))
        1

##### snakify()
Convert a string to snake_case format.
    
    Args:
        s (str): String to convert to snake_case.
    
    Returns:
        str: Snake_case version of the input string.
    
    Example:
        >>> snakify('MyViewName')
        'my_view_name'
        >>> snakify('Order-Details')
        'order_details'

##### traverse_graph()
Find the shortest path between two cubes using BFS traversal.
    
    Args:
        join_paths (dict): Dictionary mapping cube names to their connected cubes.
        cube_left (str): Starting cube name.
        cube_right (str): Target cube name.
    
    Returns:
        str: Dot-separated path from cube_left to cube_right.
    
    Example:
        >>> join_paths = {'orders': ['customers'], 'customers': ['addresses']}
        >>> traverse_graph(join_paths, 'orders', 'addresses')
        'orders.customers.addresses'


### lkml2cube.parser.loader

#### Functions

##### file_loader()
Load LookML files and resolve includes recursively.
    
    Args:
        file_path_input (str): File path pattern to load (supports glob patterns).
        rootdir_param (str | None): Root directory for resolving includes.
        namespace (dict | None): Existing namespace to merge content into.
    
    Returns:
        dict: Loaded LookML model with resolved includes.
    
    Raises:
        FileNotFoundError: If specified file path cannot be found.
        ValueError: If LookML file cannot be parsed.
    
    Example:
        >>> namespace = file_loader('models/*.lkml', '/path/to/root')
        >>> print(namespace['views'][0]['name'])
        'my_view'

##### print_summary()
Print a formatted summary of generated files using Rich tables.
    
    Args:
        summary (dict): Summary dictionary containing file information with keys
            'cubes', 'views', and/or 'explores', each containing lists of
            {'name': str, 'path': str} dictionaries.
    
    Example:
        >>> summary = {'cubes': [{'name': 'orders', 'path': '/output/cubes/orders.yml'}]}
        >>> print_summary(summary)
        # Displays a formatted table showing the generated files

##### update_namespace()
Update namespace with new file content, merging lists and handling conflicts.
    
    Args:
        namespace (dict | None): Existing namespace dictionary or None.
        new_file (dict): New file content to merge into namespace.
    
    Returns:
        dict: Updated namespace with merged content.
    
    Example:
        >>> namespace = {'views': [{'name': 'view1'}]}
        >>> new_file = {'views': [{'name': 'view2'}]}
        >>> update_namespace(namespace, new_file)
        {'views': [{'name': 'view1'}, {'name': 'view2'}]}

##### write_files()
Write cube definitions to separate files organized by type.
    
    Args:
        cube_def (dict): Cube definitions containing 'cubes' and/or 'views' keys.
        outputdir (str): Output directory path.
    
    Returns:
        dict: Summary of written files with structure:
            {'cubes': [{'name': str, 'path': str}], 'views': [{'name': str, 'path': str}]}
    
    Raises:
        Exception: If no cube definition is provided.
        OSError: If output directory cannot be created or files cannot be written.
    
    Example:
        >>> cube_def = {'cubes': [{'name': 'orders'}], 'views': [{'name': 'orders_view'}]}
        >>> summary = write_files(cube_def, '/output')
        >>> print(summary['cubes'][0]['name'])
        'orders'

##### write_lookml_files()
Write LookML model to files in the output directory.
    
    Args:
        lookml_model (dict): LookML model containing 'views' and/or 'explores' keys.
        outputdir (str): Output directory path.
    
    Returns:
        dict: Summary of written files with structure:
            {'views': [{'name': str, 'path': str}], 'explores': [{'name': str, 'path': str}]}
    
    Raises:
        Exception: If no LookML model is provided.
        OSError: If output directory cannot be created or files cannot be written.
    
    Example:
        >>> lookml_model = {'views': [{'name': 'orders'}], 'explores': [{'name': 'orders_explore'}]}
        >>> summary = write_lookml_files(lookml_model, '/output')
        >>> print(summary['views'][0]['name'])
        'orders'

##### write_single_file()
Write a single cube definition to a YAML file.
    
    Args:
        cube_def (dict): Cube definition to write.
        outputdir (str): Output directory path.
        subdir (str, optional): Subdirectory within output directory. Defaults to "cubes".
        file_name (str, optional): Name of the output file. Defaults to "my_cubes.yml".
    
    Raises:
        OSError: If output directory cannot be created or file cannot be written.
    
    Example:
        >>> cube_def = {'cubes': [{'name': 'orders', 'sql_table': 'orders'}]}
        >>> write_single_file(cube_def, '/output', 'cubes', 'orders.yml')


### lkml2cube.parser.types

#### Classes

##### Console
Simple console wrapper for printing messages.
    
    This class provides a basic print interface compatible with Rich console
    while falling back to standard print functionality.

**Methods:**

- `print()`: Print a message to the console

##### folded_unicode
String subclass for YAML folded scalar representation.
    
    This class marks strings that should be represented as folded scalars
    in YAML output (using the '>' style).
    
    Example:
        >>> text = folded_unicode("This is a long
string that will be folded")
        >>> # When dumped to YAML, will use '>' style

##### literal_unicode
String subclass for YAML literal scalar representation.
    
    This class marks strings that should be represented as literal scalars
    in YAML output (using the '|' style).
    
    Example:
        >>> sql = literal_unicode("SELECT *
FROM table
WHERE id = 1")
        >>> # When dumped to YAML, will use '|' style preserving line breaks

#### Functions

##### folded_unicode_representer()
YAML representer for folded_unicode strings.
    
    Args:
        dumper: YAML dumper instance.
        data (folded_unicode): String data to represent.
    
    Returns:
        Scalar representation with folded style.
    
    Example:
        >>> import yaml
        >>> yaml.add_representer(folded_unicode, folded_unicode_representer)
        >>> yaml.dump(folded_unicode("long text"))
        '> long text
'

##### literal_unicode_representer()
YAML representer for literal_unicode strings.
    
    Args:
        dumper: YAML dumper instance.
        data (literal_unicode): String data to represent.
    
    Returns:
        Scalar representation with literal style.
    
    Example:
        >>> import yaml
        >>> yaml.add_representer(literal_unicode, literal_unicode_representer)
        >>> yaml.dump(literal_unicode("SELECT *
FROM table"))
        '|
  SELECT *
  FROM table
'


### lkml2cube.parser.views

#### Functions

##### parse_view()
Parse LookML views into Cube definitions.
    
    Converts LookML view definitions into Cube format, handling dimensions, measures,
    view inheritance, and various LookML-specific features like tiers and drill fields.
    
    Args:
        lookml_model (dict): LookML model containing views to parse.
        raise_when_views_not_present (bool, optional): Whether to raise an exception
            when no views are found. Defaults to True.
    
    Returns:
        dict: Cube definitions with structure:
            {'cubes': [{'name': str, 'description': str, 'dimensions': list, 'measures': list, 'joins': list}]}
    
    Raises:
        Exception: If raise_when_views_not_present is True and no views are found,
            or if required dimension properties are missing.
    
    Example:
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

