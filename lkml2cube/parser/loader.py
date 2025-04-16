import glob
import lkml
import rich
import yaml

from os.path import abspath, dirname, join
from pathlib import Path

from lkml2cube.parser.types import console

visited_path = {}


def update_namespace(namespace, new_file):

    if namespace is None:
        return new_file
    for key, value in new_file.items():
        if key in namespace and key in ("views", "explores"):
            namespace[key] = namespace[key] + new_file[key]
        elif key in namespace and key in ("includes"):  # remove duplicates
            namespace[key] = list(set(namespace[key] + new_file[key]))
        elif key in ("views", "explores", "includes"):
            namespace[key] = new_file[key]
        elif key in ("connection"):
            pass  # ignored keys
        else:
            console.print(f"Key not supported yet: {key}", style="bold red")
    return namespace


def file_loader(file_path_input, rootdir_param, namespace=None):

    file_paths = glob.glob(file_path_input)
    for file_path in file_paths:
        if file_path in visited_path:
            continue
        visited_path[file_path] = True
        lookml_model = lkml.load(open(file_path, "r"))
        if "includes" in lookml_model:
            for included_path in lookml_model["includes"]:
                if (
                    namespace
                    and "includes" in namespace
                    and included_path in namespace["includes"]
                ):
                    continue
                if included_path.startswith("/"):
                    included_path = included_path[1:]
                root_dir = dirname(abspath(file_path))
                if rootdir_param:
                    root_dir = rootdir_param
                namespace = file_loader(
                    join(root_dir, included_path), rootdir_param, namespace=namespace
                )
        namespace = update_namespace(namespace, lookml_model)
    return namespace


def write_single_file(
    cube_def: dict,
    outputdir: str,
    subdir: str = "cubes",
    file_name: str = "my_cubes.yml",
):

    f = open(join(outputdir, subdir, file_name), "w")
    f.write(yaml.dump(cube_def, allow_unicode=True))
    f.close()


def write_files(cube_def, outputdir):

    summary = {"cubes": [], "views": []}

    if not cube_def:
        raise Exception("No cube definition available")

    for cube_root_element in ("cubes", "views"):

        if cube_root_element in cube_def:

            Path(join(outputdir, cube_root_element)).mkdir(parents=True, exist_ok=True)

            if len(cube_def[cube_root_element]) == 1:
                file_name = cube_def[cube_root_element][0]["name"] + ".yml"
                write_single_file(
                    cube_def=cube_def,
                    outputdir=outputdir,
                    subdir=cube_root_element,
                    file_name=file_name,
                )
                summary[cube_root_element].append(
                    {
                        "name": cube_def[cube_root_element][0]["name"],
                        "path": str(
                            Path(join(outputdir, cube_root_element, file_name))
                        ),
                    }
                )

            elif len(cube_def[cube_root_element]) > 1:
                for cube_element in cube_def[cube_root_element]:
                    new_def = {cube_root_element: [cube_element]}
                    file_name = cube_element["name"] + ".yml"
                    write_single_file(
                        cube_def=new_def,
                        outputdir=outputdir,
                        subdir=cube_root_element,
                        file_name=file_name,
                    )
                    summary[cube_root_element].append(
                        {
                            "name": cube_element["name"],
                            "path": str(
                                Path(join(outputdir, cube_root_element, file_name))
                            ),
                        }
                    )
            else:
                # Empty 'cubes' definition
                # not expected but not invalid
                pass

    return summary


def print_summary(summary):
    for cube_root_element in ("cubes", "views"):
        table = rich.table.Table(title=f"Generated {cube_root_element}")
        table.add_column("Element Name", justify="right", style="cyan", no_wrap=True)
        table.add_column("Path", style="magenta")
        for row in summary[cube_root_element]:
            table.add_row(row["name"], row["path"])
        if len(summary[cube_root_element]) > 0:
            console.print(table)
