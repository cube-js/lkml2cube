import glob
import lkml
import typer
import yaml

from os.path import abspath, dirname, join
from pathlib import Path

visited_path = {}

def update_namespace(namespace, new_file):
    if namespace is None:
        return new_file
    for key, value in new_file.items():
        if key in namespace and key in ('views', 'explores'):
            namespace[key] = namespace[key] + new_file[key]
        elif key in ('views', 'explores'):
            namespace[key] = new_file[key]
        elif key in ('connection'):
            pass # ignored keys
        else:
            typer.echo(f'Key not supported yet: {key}')
    return namespace

def file_loader(file_path_input, namespace=None):
    file_paths = glob.glob(file_path_input)
    for file_path in file_paths:
        if file_path in visited_path:
            continue
        visited_path[file_path] = True
        lookml_model = lkml.load(open(file_path, 'r'))
        if 'includes' in lookml_model:
            for included_path in lookml_model['includes']:
                if included_path.startswith('/'):
                    included_path = included_path[1:]
                root_dir = dirname(abspath(file_path))
                namespace = file_loader(join(root_dir, included_path), namespace=namespace)
        namespace = update_namespace(namespace, lookml_model)
    return namespace


def write_files(cube_def, outputdir, file_name = 'my_cubes.yml'):
    if 'cubes' in cube_def and len(cube_def['cubes']) == 1:
        file_name = cube_def['cubes'][0]['name'] + '.yml'
    Path(join(outputdir, 'cubes')).mkdir(parents=True, exist_ok=True)
    f = open(join(outputdir, 'cubes', file_name), 'w')
    f.write(yaml.dump(cube_def))
    f.close()
