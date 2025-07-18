import re
import traceback

from pprint import pformat

from lkml2cube.parser.views import parse_view
from lkml2cube.parser.types import console

snake_case = r"\{([a-zA-Z]+(?:_[a-zA-Z]+)*\.[a-zA-Z]+(?:_[a-zA-Z]+)*)\}"


def snakify(s):
    """Convert a string to snake_case format.
    
    Args:
        s (str): String to convert to snake_case.
    
    Returns:
        str: Snake_case version of the input string.
    
    Example:
        >>> snakify('MyViewName')
        'my_view_name'
        >>> snakify('Order-Details')
        'order_details'
    """
    return "_".join(
        re.sub(
            "([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", s.replace("-", " "))
        ).split()
    ).lower()


def build_cube_name_look_up(cube_def):
    """Build a lookup dictionary for cube names in the cube definition.
    
    Args:
        cube_def (dict): Cube definition containing 'cubes' list.
    
    Note:
        This function modifies the cube_def dictionary in place by adding
        a 'cube_name_look_up' key if it doesn't exist.
    
    Example:
        >>> cube_def = {'cubes': [{'name': 'orders'}, {'name': 'customers'}]}
        >>> build_cube_name_look_up(cube_def)
        >>> print('orders' in cube_def['cube_name_look_up'])
        True
    """
    if "cube_name_look_up" in cube_def:
        return
    cube_name_look_up = {}
    for cube_element in cube_def["cubes"]:
        cube_name_look_up[cube_element["name"]] = cube_element
    cube_def["cube_name_look_up"] = cube_name_look_up


def get_cube_from_cube_def(cube_def, cube_name):
    """Get a cube definition by name from the cube definition.
    
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
    """
    if "cube_name_look_up" not in cube_def:
        build_cube_name_look_up(cube_def)
    if cube_name in cube_def["cube_name_look_up"]:
        return cube_def["cube_name_look_up"][cube_name]
    return None


def get_cube_names_from_join_condition(join_condition):
    """Extract cube names from a join condition SQL string.
    
    Args:
        join_condition (str): SQL join condition containing cube references.
    
    Returns:
        list[str]: List of cube names found in the join condition.
    
    Example:
        >>> join_condition = '${orders.customer_id} = ${customers.id}'
        >>> get_cube_names_from_join_condition(join_condition)
        ['orders', 'customers']
    """
    return [cube.split(".")[0] for cube in re.findall(snake_case, join_condition)]


def traverse_graph(join_paths, cube_left, cube_right):
    """Find the shortest path between two cubes using BFS traversal.
    
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
    """
    # Create a queue for BFS
    queue = []
    queue.append([cube_left])

    while queue:
        # Dequeue a vertex from queue
        tmp_path = queue.pop(0)
        # If this adjacent node is the destination node,
        # then return true
        last_node = tmp_path[len(tmp_path) - 1]
        if last_node == cube_right:
            return ".".join(tmp_path)
        #  Else, continue to do BFS
        if last_node in join_paths:
            for cube in join_paths[last_node]:
                if cube not in tmp_path:
                    new_path = []
                    new_path = tmp_path + [cube]
                    queue.append(new_path)

    console.print(
        f"Cubes are not reachable: {cube_left}, {cube_right}", style="bold red"
    )
    return ".".join([cube_left, cube_right])


def generate_cube_joins(cube_def, lookml_model):
    """Generate cube join definitions from LookML explores.
    
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
    """
    if "explores" not in lookml_model or not lookml_model["explores"]:
        return cube_def
    for explore in lookml_model["explores"]:
        if "joins" not in explore:
            continue

        for join_element in explore["joins"]:
            try:
                cube_right = join_element["name"]

                joined_cubes = [
                    cube
                    for cube in get_cube_names_from_join_condition(
                        join_element["sql_on"]
                    )
                    if cube != cube_right
                ]
                if joined_cubes:
                    if "from" in join_element:
                        cube = {
                            "name": cube_right,
                            "extends": join_element["from"],
                            "shown": False,
                        }
                        cube_def["cubes"].append(cube)
                    else:
                        cube = get_cube_from_cube_def(cube_def, cube_right)
                        if not cube:
                            console.print(
                                f'Cube referenced in explores not found: {join_element["name"]}'
                            )
                            continue

                    join_condition = join_element["sql_on"]

                    if "joins" not in cube:
                        cube["joins"] = []

                    cube["joins"].append(
                        {
                            "name": joined_cubes[0],
                            "sql": join_condition,
                            "relationship": join_element["relationship"],
                        }
                    )
            except Exception:
                console.print(
                    f"Error while parsing explore: {pformat(explore)}", style="bold red"
                )
                console.print(traceback.format_exc())

    return cube_def


def generate_cube_views(cube_def, lookml_model, use_explores_name=False):
    """Generate Cube view definitions from LookML explores.
    
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
    """
    if "views" not in cube_def:
        cube_def["views"] = []
    if "explores" not in lookml_model or not lookml_model["explores"]:
        return cube_def
    for explore in lookml_model["explores"]:
        try:
            central_cube = explore["name"]
            label = explore.get("label", explore.get("view_label", explore["name"]))
            view_name = snakify(label)
            view = {
                # concat _view to avoid name collision in Cube
                "name": central_cube + "_view" if use_explores_name else view_name,
                "description": label,
                "cubes": [
                    {"join_path": central_cube, "includes": "*", "alias": view_name}
                ],
            }

            if "hidden" in explore:
                view["public"] = not bool(explore["hidden"] == "yes")

            if "joins" not in explore or not explore["joins"]:
                cube_def["views"].append(view)
                continue
            # Create Graph
            join_paths = {}
            for join_element in explore["joins"]:
                cube_right = join_element["name"]
                cube_left = [
                    cube
                    for cube in get_cube_names_from_join_condition(
                        join_element["sql_on"]
                    )
                    if cube != cube_right
                ][0]

                if cube_left in join_paths:
                    join_paths[cube_left].append(cube_right)
                else:
                    join_paths[cube_left] = [cube_right]
            # traverse graph
            for join_element in explore["joins"]:
                cube_right = join_element["name"]
                join_path = {
                    "join_path": traverse_graph(join_paths, central_cube, cube_right),
                    "includes": "*",
                    "alias": cube_right,
                }
                view["cubes"].append(join_path)

            # End
            cube_def["views"].append(view)

        except Exception:
            console.print(
                f"Error while parsing explore: {pformat(explore)}", style="bold red"
            )
            console.print(traceback.format_exc())
    return cube_def


def parse_explores(lookml_model, use_explores_name=False):
    """Parse LookML explores into Cube definitions with joins and views.
    
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
    """
    # First we read all possible lookml views.
    cube_def = parse_view(lookml_model, raise_when_views_not_present=False)
    if "explores" not in lookml_model:
        raise Exception(
            "LookML explores are needed to generate Cube Views, no explore found in path."
        )
    cube_def = generate_cube_joins(cube_def, lookml_model)

    cube_def = generate_cube_views(cube_def, lookml_model, use_explores_name)

    return cube_def
