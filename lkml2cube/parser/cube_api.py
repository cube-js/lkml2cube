import requests
from lkml2cube.parser.types import reverse_type_map, literal_unicode, console


def meta_loader(
    meta_url: str,
    token: str,
) -> dict:
    """Load the Cube meta API and return the model as a dictionary.
    
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
    """

    if not token:
        raise ValueError("A valid token must be provided to access the Cube meta API.")

    # We need the extended version of the meta API to get the full model
    if not meta_url.endswith("?extended"):
        meta_url += "?extended"

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(meta_url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch meta data: {response.text}")

    return response.json()


def parse_members(members: list) -> list:
    """Parse measures and dimensions from the Cube meta model.
    
    Args:
        members (list): List of dimension or measure definitions from Cube meta.
    
    Returns:
        list: List of parsed members in LookML format.
    
    Example:
        >>> members = [{'name': 'total_sales', 'type': 'sum', 'sql': 'amount'}]
        >>> parsed = parse_members(members)
        >>> print(parsed[0]['name'])
        'total_sales'
    """

    rpl_table = (
        lambda s: s.replace("${", "{").replace("{CUBE}", "{TABLE}").replace("{", "${")
    )
    convert_to_literal = lambda s: (
        literal_unicode(rpl_table(s)) if "\n" in s else rpl_table(s)
    )
    parsed_members = []

    for member in members:
        if member.get("type") not in reverse_type_map:
            console.print(
                f'Dimension type: {member["type"]} not implemented yet:\n {member}',
                style="bold red",
            )
            continue

        dim = {
            "name": member.get("name"),
            "label": member.get("title", member.get("name")),
            "description": member.get("description", ""),
            "type": reverse_type_map.get(member.get("aggType", member.get("type"))),
        }
        if "sql" in member:
            dim["sql"] = convert_to_literal(member["sql"])

        if not member.get("public"):
            dim["hidden"] = "yes"

        parsed_members.append(dim)
    return parsed_members


def parse_meta(cube_model: dict) -> dict:
    """Parse the Cube meta model and return a simplified version.
    
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
    """

    lookml_model = {
        "views": [],
        "explores": [],
    }

    for model in cube_model.get("cubes", []):
        # Determine if this is a cube (table-based) or view (join-based)
        is_view = _is_cube_view(model)
        
        if is_view:
            # This is a Cube view -> LookML explore
            explore = _parse_cube_view_to_explore(model)
            lookml_model["explores"].append(explore)
        else:
            # This is a Cube cube -> LookML view
            view = _parse_cube_to_view(model)
            lookml_model["views"].append(view)

    return lookml_model


def _is_cube_view(model: dict) -> bool:
    """Determine if a Cube model is a view (has joins) or a cube (has its own data source).
    
    Views typically have aliasMember references and no sql_table/sql property.
    
    Args:
        model (dict): Cube model definition.
    
    Returns:
        bool: True if the model is a view, False if it's a cube.
    
    Example:
        >>> model = {'dimensions': [{'aliasMember': 'orders.id'}]}
        >>> _is_cube_view(model)
        True
        >>> model = {'sql_table': 'orders', 'dimensions': [{'name': 'id'}]}
        >>> _is_cube_view(model)
        False
    """
    # Check if any dimensions or measures use aliasMember (indicating joins)
    has_alias_members = False
    
    for dimension in model.get("dimensions", []):
        if "aliasMember" in dimension:
            has_alias_members = True
            break
    
    if not has_alias_members:
        for measure in model.get("measures", []):
            if "aliasMember" in measure:
                has_alias_members = True
                break
    
    # If it has alias members and no own data source, it's a view
    has_own_data_source = "sql_table" in model or "sql" in model
    
    return has_alias_members and not has_own_data_source


def _parse_cube_to_view(model: dict) -> dict:
    """Parse a Cube cube into a LookML view.
    
    Args:
        model (dict): Cube model definition.
    
    Returns:
        dict: LookML view definition with dimensions, measures, and metadata.
    
    Example:
        >>> model = {'name': 'orders', 'sql_table': 'orders', 'dimensions': [{'name': 'id', 'type': 'string'}]}
        >>> view = _parse_cube_to_view(model)
        >>> print(view['name'])
        'orders'
        >>> print(view['sql_table_name'])
        'orders'
    """
    view = {
        "name": model.get("name"),
        "label": model.get("title", model.get("description", model.get("name"))),
        "extends": [],
        "dimensions": [],
        "measures": [],
        "filters": [],
    }

    if "extends" in model:
        view["extends"] = [model["extends"]]

    if "sql_table" in model:
        view["sql_table_name"] = model["sql_table"]

    if "sql" in model:
        view["derived_table"] = {"sql": model["sql"]}

    if "dimensions" in model:
        view["dimensions"] = parse_members(model["dimensions"])
    if "measures" in model:
        view["measures"] = parse_members(model["measures"])

    return view


def _parse_cube_view_to_explore(model: dict) -> dict:
    """Parse a Cube view into a LookML explore with joins.
    
    Args:
        model (dict): Cube view model definition with aliasMember references.
    
    Returns:
        dict: LookML explore definition with joins based on referenced cubes.
    
    Example:
        >>> model = {
        ...     'name': 'orders_analysis',
        ...     'dimensions': [{'aliasMember': 'orders.id'}, {'aliasMember': 'customers.name'}]
        ... }
        >>> explore = _parse_cube_view_to_explore(model)
        >>> print(explore['name'])
        'orders_analysis'
        >>> print(len(explore['joins']))
        1
    """
    explore = {
        "name": model.get("name"),
        "label": model.get("title", model.get("description", model.get("name"))),
        "joins": []
    }
    
    # Extract join information from aliasMember references
    joined_cubes = set()
    primary_cube = None
    
    # Find all referenced cubes from dimensions and measures
    for dimension in model.get("dimensions", []):
        if "aliasMember" in dimension:
            cube_name = dimension["aliasMember"].split(".")[0]
            joined_cubes.add(cube_name)
    
    for measure in model.get("measures", []):
        if "aliasMember" in measure:
            cube_name = measure["aliasMember"].split(".")[0]
            joined_cubes.add(cube_name)
    
    # Try to determine the primary cube (base of the explore)
    # Usually the most referenced cube or the first one
    if joined_cubes:
        # For now, use the first cube alphabetically as primary
        # In a real implementation, you might have more logic here
        primary_cube = min(joined_cubes)
        joined_cubes.remove(primary_cube)
        
        explore["view_name"] = primary_cube
        
        # Create joins for the remaining cubes
        for cube_name in sorted(joined_cubes):
            join = {
                "name": cube_name,
                "view_label": cube_name.replace("_", " ").title(),
                "type": "left_outer",  # Default join type  
                "relationship": "many_to_one",  # Default relationship
                # In a real implementation, you'd extract actual join conditions
                # from the Cube model's join definitions
                "sql_on": f"${{{primary_cube}.id}} = ${{{cube_name}.id}}"
            }
            explore["joins"].append(join)
    
    return explore
