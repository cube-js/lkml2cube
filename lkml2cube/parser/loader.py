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
        elif key in namespace and key in ('includes'): # remove duplicates
            namespace[key] = list(set(namespace[key] + new_file[key]))
        elif key in ('views', 'explores', 'includes'):
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
                if namespace and 'includes' in namespace and included_path in namespace['includes']:
                    continue
                if included_path.startswith('/'):
                    included_path = included_path[1:]
                root_dir = dirname(abspath(file_path))
                namespace = file_loader(join(root_dir, included_path), namespace=namespace)
        namespace = update_namespace(namespace, lookml_model)
    return namespace


def write_single_file(cube_def: dict, outputdir: str, subdir: str = 'cubes', file_name: str = 'my_cubes.yml'):

    f = open(join(outputdir, subdir, file_name), 'w')
    f.write(yaml.dump(cube_def))
    f.close()


def write_files(cube_def, outputdir):
    
    if not cube_def:
        raise Exception('No cube definition available')
    
    for cube_root_element in ('cubes', 'views'):

        if cube_root_element in cube_def:

            Path(join(outputdir, cube_root_element)).mkdir(parents=True, exist_ok=True)

            if len(cube_def[cube_root_element]) == 1:
                write_single_file(cube_def=cube_def, 
                                outputdir=outputdir,
                                subdir=cube_root_element,
                                file_name=cube_def[cube_root_element][0]['name'] + '.yml')

            elif len(cube_def[cube_root_element]) > 1:
                for cube_element in cube_def[cube_root_element]:
                    new_def = {
                        cube_root_element: [cube_element]
                    }
                    write_single_file(cube_def=new_def,
                                    outputdir=outputdir,
                                    subdir=cube_root_element,
                                    file_name=cube_element['name'] + '.yml')
            else:
                # Empty 'cubes' definition
                # not expected but not invalid
                pass
        
