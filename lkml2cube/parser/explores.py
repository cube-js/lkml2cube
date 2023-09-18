
import re
import traceback
import typer

from pprint import pformat

from lkml2cube.parser.views import parse_view

snake_case = r'\{([a-zA-Z]+(?:_[a-zA-Z]+)*\.[a-zA-Z]+(?:_[a-zA-Z]+)*)\}'

def snakify(s):
  return '_'.join(
        re.sub('([A-Z][a-z]+)', r' \1',
        re.sub('([A-Z]+)', r' \1',
        s.replace('-', ' '))).split()
    ).lower()

def build_cube_name_look_up(cube_def):
    if 'cube_name_look_up' in cube_def:
        return
    cube_name_look_up = {}
    for cube_element in cube_def['cubes']:
        cube_name_look_up[cube_element['name']] = cube_element
    cube_def['cube_name_look_up'] = cube_name_look_up

def get_cube_from_cube_def(cube_def, cube_name):
    if 'cube_name_look_up' not in cube_def:
        build_cube_name_look_up(cube_def)
    if cube_name in cube_def['cube_name_look_up']:
        return cube_def['cube_name_look_up'][cube_name]
    return None

def get_cube_names_from_join_condition(join_condition):
    return [cube.split('.')[0] for cube in re.findall(snake_case, join_condition)]

def traverse_graph(join_paths, cube_left, cube_right):
    # Create a queue for BFS
    queue = []
    queue.append([cube_left])

    while queue:
        #Dequeue a vertex from queue
        tmp_path = queue.pop(0)
        # If this adjacent node is the destination node,
        # then return true
        last_node = tmp_path[len(tmp_path)-1]
        if last_node == cube_right:
            return '.'.join(tmp_path)
        #  Else, continue to do BFS
        if last_node in join_paths:
            for cube in join_paths[last_node]:
                if cube not in tmp_path:
                    new_path = []
                    new_path = tmp_path + [cube]
                    queue.append(new_path)

    typer.echo(f'Cubes are not reachable: {cube_left}, {cube_right}')
    return '.'.join(cube_left, cube_right)


def generate_cube_joins(cube_def, lookml_model):
    for explore in lookml_model['explores']:
        if 'joins' not in explore:
            continue

        for join_element in explore['joins']:
            try:
                cube_right = join_element['name']
            
                joined_cubes = [cube for cube in get_cube_names_from_join_condition(join_element['sql_on']) if cube != cube_right]
                if joined_cubes:
                    if 'from' in join_element:
                        cube = {
                            'name': cube_right,
                            'extends': join_element['from'],
                            'shown': False,
                        }
                        cube_def['cubes'].append(cube)
                    else:
                        cube = get_cube_from_cube_def(cube_def, cube_right)

                    join_condition = join_element['sql_on']

                    if 'joins' not in cube:
                        cube['joins'] = []

                    cube['joins'].append({
                        'name': joined_cubes[0],
                        'sql': join_condition,
                        'relationship': join_element['relationship']
                    })
            except Exception:
                typer.echo(f'Error while parsing explore: {pformat(explore)}')
                typer.echo(traceback.format_exc())

    return cube_def

def generate_cube_views(cube_def, lookml_model):
    if 'views' not in cube_def:
        cube_def['views'] = []
    for explore in lookml_model['explores']:
        try:
            central_cube = explore['name']
            view_name = snakify(explore['label'])
            view = {
                'name': view_name,
                'description': explore['label'],
                'cubes': [{
                    'join_path': central_cube,
                    'includes': "*",
                    'alias': view_name
                }]
            }

            if 'joins' not in explore:
                cube_def['views'].append(view)
                continue
            # Create Graph
            join_paths = {}
            for join_element in explore['joins']:
                cube_right = join_element['name']
                cube_left = [cube for cube in get_cube_names_from_join_condition(join_element['sql_on']) if cube != cube_right][0]

                if cube_left in join_paths:
                    join_paths[cube_left].append(cube_right)
                else:
                    join_paths[cube_left] = [cube_right]
            # traverse graph
            for join_element in explore['joins']:
                cube_right = join_element['name']
                join_path = {
                    'join_path': traverse_graph(join_paths, central_cube, cube_right),
                    'includes': "*",
                    'alias': cube_right
                }
                view['cubes'].append(join_path)
                
            # End
            cube_def['views'].append(view)

        except Exception:
            typer.echo(f'Error while parsing explore: {pformat(explore)}')
            typer.echo(traceback.format_exc())
    return cube_def


def parse_explores(lookml_model):
    # First we read all possible lookml views.
    cube_def = parse_view(lookml_model, raise_when_views_not_present=False)
    if 'explores' not in lookml_model:
        raise Exception('LookML explores are needed to generate Cube Views, no explore found in path.')
    cube_def = generate_cube_joins(cube_def, lookml_model)

    cube_def = generate_cube_views(cube_def, lookml_model)

    return cube_def