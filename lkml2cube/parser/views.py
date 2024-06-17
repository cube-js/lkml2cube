import copy
import traceback
import rich

from pprint import pformat
from lkml2cube.parser.types import type_map, literal_unicode

console = rich.console.Console()


def parse_view(lookml_model, raise_when_views_not_present=True):
    cubes = []
    cube_def = {"cubes": cubes}
    rpl_table = lambda s: s.replace("${TABLE}", "{CUBE}").replace("${", "{")
    sets = {}

    if raise_when_views_not_present and "views" not in lookml_model:
        raise Exception(
            f"The following object types are not implemented yet: {lookml_model.keys()}"
        )
    elif "views" not in lookml_model:
        return cube_def

    for view in lookml_model["views"]:
        try:
            if "sets" in view:
                for set in view["sets"]:
                    sets[set["name"]] = set["fields"]

            label = view.get("label", view.get("view_label", view["name"]))
            cube = {
                "name": view["name"],
                "description": label,
                "dimensions": [],
                "measures": [],
                "joins": [],
            }

            if "extends" in view or "extends__all" in view:
                extended_views = view.get("extends", view.get("extends__all", []))
                extended_views = [x for l in extended_views for x in l]
                parent_views = []
                for lkml_view in extended_views:
                    found = False
                    for view_item in lookml_model["views"]:
                        if lkml_view == view_item["name"]:
                            parent_views.append(view_item)
                            found = True
                    if not found:
                        console.print(f"View not found: {lkml_view}", style="bold red")
                parent_views.append(view)

                # MRO is left to right
                view = copy.deepcopy(parent_views.pop(0))
                while len(parent_views) > 0:
                    next_view = parent_views.pop(0)
                    for elements in (
                        "dimensions",
                        "filters",
                        "measures",
                        "dimension_groups",
                    ):
                        if elements in next_view and elements in view:
                            next_view[elements] = next_view[elements] + view[elements]
                    view.update(next_view)

            if "sql_table_name" in view:
                cube["sql_table"] = view["sql_table_name"]
            elif "derived_table" in view and "sql" in view["derived_table"]:
                cube["sql"] = view["derived_table"]["sql"]

            if "sql" in cube:
                cube["sql"] = literal_unicode(rpl_table(cube["sql"]))

            dimensions = (
                view.get("dimensions", [])
                + view.get("filters", [])
                + view.get("dimension_groups", [])
            )
            filters = {element["name"]: True for element in view.get("filters", [])}

            for dimension in dimensions:
                if "type" not in dimension:
                    # Defaults to string, cube needs a type.
                    dimension["type"] = "string"
                # validate schema
                skip_dim = False
                if dimension["type"] not in type_map:
                    console.print(
                        f'Dimension type: {dimension["type"]} not implemented yet:\n {dimension}',
                        style="bold red",
                    )
                    skip_dim = True
                for property in ("sql", "name"):
                    if property not in dimension:
                        console.print(
                            f"Dimension must have {property} property:\n {dimension}",
                            style="bold red",
                        )
                if skip_dim:
                    continue

                cube_dimension = {
                    "name": dimension["name"],
                    "sql": rpl_table(dimension["sql"]),
                    "type": type_map[dimension["type"]],
                }

                if "hidden" in dimension:
                    cube_dimension["public"] = not bool(dimension["hidden"] == "yes")

                if dimension["name"] in filters:
                    cube_dimension["type"] = "boolean"

                if dimension["type"] == "tier":
                    bins = dimension.get("bins", dimension.get("tiers"))
                    if not bins:
                        console.print(
                            f'Dimension type: {dimension["type"]} requires tiers',
                            style="bold red",
                        )
                        continue
                    if len(bins) < 2:
                        pass
                    else:
                        tier_sql = f"CASE "
                        for i in range(0, len(bins) - 1):
                            tier_sql += f" WHEN {cube_dimension['sql']} >= {bins[i]} AND {cube_dimension['sql']} < {bins[i + 1]} THEN {bins[i]} "
                        tier_sql += "ELSE NULL END"
                        cube_dimension["sql"] = tier_sql
                cube["dimensions"].append(cube_dimension)

            for measure in view.get("measures", []):
                if measure["type"] not in type_map:
                    msg = f'Measure type: {measure["type"]} not implemented yet:\n# {measure}'
                    console.print(f"# {msg}", style="bold red")
                    continue

                cube_measure = {
                    "name": measure["name"],
                    "type": type_map[measure["type"]],
                }

                if "hidden" in measure:
                    cube_measure["public"] = not bool(measure["hidden"] == "yes")

                if measure["type"] != "count":
                    cube_measure["sql"] = rpl_table(measure["sql"])
                elif "drill_fields" in measure:
                    drill_members = []
                    for drill_field in measure["drill_fields"]:
                        if "*" in drill_field:
                            drill_field = drill_field.replace("*", "")
                            if drill_field not in sets:
                                console.print(
                                    f"set undefined {drill_field}", style="bold red"
                                )
                            else:
                                drill_members += sets[drill_field]
                        else:
                            drill_members.append(drill_field)
                        cube_measure["drill_members"] = drill_members

                cube["measures"].append(cube_measure)

            cubes.append(cube)
        except Exception:
            console.print(
                f"Error while parsing view: {pformat(view)}", style="bold red"
            )
            console.print(traceback.format_exc())
    return cube_def
