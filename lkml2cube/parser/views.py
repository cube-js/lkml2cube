
import traceback
import typer

from pprint import pformat


def parse_view(lookml_model, raise_when_views_not_present=True):
    cubes = []
    cube_def = {
        'cubes': cubes
    }
    rpl_table = lambda s: s.replace('${TABLE}', '{CUBE}').replace('${', '{')
    type_map = {
        'zipcode': 'string',
        'string': 'string',
        'number': 'number',
        'tier': 'number',
        'count': 'count',
        'yesno': 'boolean',
        'sum': 'sum',
        'sum_distinct': 'sum',
        'average': 'avg',
        'average_distinct': 'avg',
        'date': 'time',
        'time': 'time',
        'count_distinct': 'count_distinct_approx',
    }
    sets = {}
    
    if raise_when_views_not_present and 'views' not in lookml_model:
        raise Exception(f'The following object types are not implemented yet: {lookml_model.keys()}')
    elif 'views' not in lookml_model:
        return cube_def
    
    for view in lookml_model['views']:
        try:
            if 'sets' in view:
                for set in view['sets']:
                    sets[set['name']] = set['fields']

            cube = {
                'name': view['name'],
                'dimensions': [],
                'measures': [],
                'joins': []
            }
            if 'sql_table_name' in view:
                cube['sql_table'] = view['sql_table_name']
            elif 'derived_table' in view and 'sql' in view['derived_table']:
                cube['sql'] = view['derived_table']['sql']
            else:
                typer.echo(view)
                raise Exception(f'View type not implemented yet')
            
            if 'dimensions' not in view:
                typer.echo('cube does not support models without dimensions')
                continue

            for dimension in view['dimensions']:
                if 'type' not in dimension:
                    # Defaults to string, cube needs a type.
                    dimension['type'] = 'string'
                if dimension['type'] not in type_map:
                    raise Exception(f'Dimension type: {dimension["type"]} not implemented yet:\n {dimension}')
                cube_dimension = {
                    'name': dimension['name'],
                    'sql': rpl_table(dimension['sql']),
                    'type': type_map[dimension['type']]
                }
                if dimension['type'] == 'tier':
                    bins = dimension['bins']
                    if len(bins) < 2:
                        pass
                    else:
                        tier_sql = f'CASE '
                        for i in range(0, len(bins) - 1):
                            tier_sql += f" WHEN {cube_dimension['sql']} >= {bins[i]} AND {cube_dimension['sql']} < {bins[i + 1]} THEN {bins[i]} "
                        tier_sql += 'ELSE NULL END'
                        cube_dimension['sql'] = tier_sql
                cube['dimensions'].append(cube_dimension)

            if 'dimension_groups' in view:
                for dimension in view['dimension_groups']:
                    cube_dimension = {
                        'name': dimension['name'],
                        'sql': rpl_table(dimension['sql']),
                        'type': type_map[dimension['type']]
                    }
                    if 'type' not in dimension:
                        raise Exception(f'Dimension type: {dimension["type"]} not implemented yet:\n {dimension}')
                    cube['dimensions'].append(cube_dimension)

            if 'measures' not in view:
                cubes.append(cube)
                continue

            for measure in view['measures']:
                if measure['type'] not in type_map:
                    msg = f'Measure type: {measure["type"]} not implemented yet:\n# {measure}'
                    if measure["type"] in ('list', 'sum_distinct'):
                        typer.echo(f'# {msg}')
                        continue
                    else:
                        raise Exception(msg)
                cube_measure = {
                    'name': measure['name'],
                    'type': type_map[measure['type']]
                }
                if measure['type'] != 'count':
                    cube_measure['sql'] = rpl_table(measure['sql'])
                elif 'drill_fields' in measure:
                    drill_members = []
                    for drill_field in measure['drill_fields']:
                        if '*' in drill_field:
                            drill_field = drill_field.replace('*', '')
                            if drill_field not in sets:
                                typer.echo(f'set undefined {drill_field}')
                            else:
                                drill_members += sets[drill_field]
                        else:
                            drill_members.append(drill_field)
                        cube_measure['drill_members'] = drill_members

                cube['measures'].append(cube_measure)

            cubes.append(cube)
        except Exception:
            typer.echo(f'Error while parsing view: {pformat(view)}')
            typer.echo(traceback.format_exc())
    return cube_def
