import glob
import lkml
import rich
import rich.table
import rich.console
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


def write_lookml_files(lookml_model, outputdir):
    """
    Write LookML model to files in the output directory.
    """
    summary = {"views": [], "explores": []}
    
    if not lookml_model:
        raise Exception("No LookML model available")
    
    for lookml_root_element in ("views", "explores"):
        if lookml_root_element in lookml_model and lookml_model[lookml_root_element]:
            
            Path(join(outputdir, lookml_root_element)).mkdir(parents=True, exist_ok=True)
            
            for element in lookml_model[lookml_root_element]:
                element_name = element.get("name")
                if not element_name:
                    continue
                    
                file_name = f"{element_name}.{lookml_root_element[:-1]}.lkml"
                file_path = join(outputdir, lookml_root_element, file_name)
                
                # Generate includes for explores
                includes = None
                if lookml_root_element == "explores":
                    includes = _generate_includes_for_explore(element, lookml_model)
                
                # Generate LookML content
                lookml_content = _generate_lookml_content(element, lookml_root_element[:-1], includes)
                
                with open(file_path, "w") as f:
                    f.write(lookml_content)
                
                summary[lookml_root_element].append({
                    "name": element_name,
                    "path": str(Path(file_path))
                })
    
    return summary


def _generate_lookml_content(element, element_type, includes=None):
    """
    Generate LookML content for a view or explore element.
    """
    lines = []
    name = element.get("name", "unnamed")
    
    # Add includes for explores
    if element_type == "explore" and includes:
        for include in includes:
            lines.append(f'include: "{include}"')
        lines.append("")  # Empty line after includes
    
    lines.append(f"{element_type} {name} {{")
    
    if element_type == "view":
        # Handle view-specific properties
        if "label" in element:
            lines.append(f'  label: "{element["label"]}"')
        
        if "sql_table_name" in element:
            lines.append(f'  sql_table_name: {element["sql_table_name"]} ;;')
        
        if "derived_table" in element and "sql" in element["derived_table"]:
            lines.append("  derived_table: {")
            sql_content = element["derived_table"]["sql"]
            if isinstance(sql_content, str) and "\n" in sql_content:
                lines.append("    sql:")
                for sql_line in sql_content.split("\n"):
                    lines.append(f"      {sql_line}")
                lines.append("    ;;")
            else:
                lines.append(f"    sql: {sql_content} ;;")
            lines.append("  }")
        
        if "extends" in element and element["extends"]:
            for extend in element["extends"]:
                lines.append(f"  extends: [{extend}]")
        
        # Handle dimensions
        if "dimensions" in element:
            for dim in element["dimensions"]:
                lines.extend(_generate_dimension_lines(dim))
        
        # Handle measures
        if "measures" in element:
            for measure in element["measures"]:
                lines.extend(_generate_measure_lines(measure))
        
        # Handle filters
        if "filters" in element:
            for filter_def in element["filters"]:
                lines.extend(_generate_filter_lines(filter_def))
    
    elif element_type == "explore":
        # Handle explore-specific properties
        if "label" in element:
            lines.append(f'  label: "{element["label"]}"')
        
        if "description" in element:
            lines.append(f'  description: "{element["description"]}"')
        
        if "hidden" in element and element["hidden"]:
            lines.append(f"  hidden: yes")
        
        # Add view_name if specified
        if "view_name" in element:
            lines.append(f"  view_name: {element['view_name']}")
        
        # Add joins
        if "joins" in element and element["joins"]:
            for join in element["joins"]:
                lines.extend(_generate_join_lines(join))
    
    lines.append("}")
    return "\n".join(lines)


def _generate_dimension_lines(dimension):
    """
    Generate LookML lines for a dimension.
    """
    lines = []
    name = dimension.get("name", "unnamed")
    lines.append(f"  dimension: {name} {{")
    
    if "label" in dimension:
        lines.append(f'    label: "{dimension["label"]}"')
    
    if "description" in dimension and dimension["description"]:
        lines.append(f'    description: "{dimension["description"]}"')
    
    if "type" in dimension:
        lines.append(f'    type: {dimension["type"]}')
    
    # Add primary_key if this looks like an ID field
    if "primary_key" in dimension and dimension["primary_key"]:
        lines.append("    primary_key: yes")
    elif name.lower().endswith("_id") or name.lower() == "id":
        lines.append("    primary_key: yes")
    
    if "sql" in dimension:
        sql_content = dimension["sql"]
        if isinstance(sql_content, str) and "\n" in sql_content:
            lines.append("    sql:")
            for sql_line in sql_content.split("\n"):
                lines.append(f"      {sql_line}")
            lines.append("    ;;")
        else:
            lines.append(f"    sql: {sql_content} ;;")
    
    if "hidden" in dimension and dimension["hidden"] == "yes":
        lines.append("    hidden: yes")
    
    lines.append("  }")
    return lines


def _generate_measure_lines(measure):
    """
    Generate LookML lines for a measure.
    """
    lines = []
    name = measure.get("name", "unnamed")
    lines.append(f"  measure: {name} {{")
    
    if "label" in measure:
        lines.append(f'    label: "{measure["label"]}"')
    
    if "description" in measure and measure["description"]:
        lines.append(f'    description: "{measure["description"]}"')
    
    if "type" in measure:
        lines.append(f'    type: {measure["type"]}')
    
    if "sql" in measure:
        sql_content = measure["sql"]
        if isinstance(sql_content, str) and "\n" in sql_content:
            lines.append("    sql:")
            for sql_line in sql_content.split("\n"):
                lines.append(f"      {sql_line}")
            lines.append("    ;;")
        else:
            lines.append(f"    sql: {sql_content} ;;")
    
    # Add drill_fields for count measures
    if measure.get("type") == "count":
        lines.append("    drill_fields: [id, name]")
    
    if "hidden" in measure and measure["hidden"] == "yes":
        lines.append("    hidden: yes")
    
    lines.append("  }")
    return lines


def _generate_filter_lines(filter_def):
    """
    Generate LookML lines for a filter.
    """
    lines = []
    name = filter_def.get("name", "unnamed")
    lines.append(f"  filter: {name} {{")
    
    if "label" in filter_def:
        lines.append(f'    label: "{filter_def["label"]}"')
    
    if "description" in filter_def and filter_def["description"]:
        lines.append(f'    description: "{filter_def["description"]}"')
    
    if "type" in filter_def:
        lines.append(f'    type: {filter_def["type"]}')
    
    lines.append("  }")
    return lines


def _generate_join_lines(join):
    """
    Generate LookML lines for a join.
    """
    lines = []
    name = join.get("name", "unnamed")
    lines.append(f"  join: {name} {{")
    
    if "view_label" in join:
        lines.append(f'    view_label: "{join["view_label"]}"')
    
    if "type" in join:
        lines.append(f"    type: {join['type']}")
    
    if "relationship" in join:
        lines.append(f"    relationship: {join['relationship']}")
    
    if "sql_on" in join:
        lines.append(f"    sql_on: {join['sql_on']} ;;")
    
    lines.append("  }")
    return lines


def _generate_includes_for_explore(explore, lookml_model):
    """
    Generate include statements for an explore based on the views it references.
    """
    includes = []
    referenced_views = set()
    
    # Add the base view
    if "view_name" in explore:
        referenced_views.add(explore["view_name"])
    
    # Add joined views
    if "joins" in explore:
        for join in explore["joins"]:
            referenced_views.add(join["name"])
    
    # Generate include paths for referenced views
    for view_name in referenced_views:
        # Check if the view exists in our model
        view_exists = any(view["name"] == view_name for view in lookml_model.get("views", []))
        if view_exists:
            includes.append(f"/views/{view_name}.view.lkml")
    
    return includes


def print_summary(summary):
    # Use the proper Rich console for table rendering
    rich_console = rich.console.Console()
    
    for cube_root_element in ("cubes", "views", "explores"):
        if cube_root_element in summary and summary[cube_root_element]:
            table = rich.table.Table(title=f"Generated {cube_root_element}")
            table.add_column("Element Name", justify="right", style="cyan", no_wrap=True)
            table.add_column("Path", style="magenta")
            for row in summary[cube_root_element]:
                table.add_row(row["name"], row["path"])
            rich_console.print(table)
