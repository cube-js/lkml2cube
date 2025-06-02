import requests
from lkml2cube.parser.types import reverse_type_map, literal_unicode, console


def meta_loader(
    meta_url: str,
    token: str,
) -> dict:
    """
    Load the Cube meta API and return the model as a dictionary.
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
    """
    Parse measures and dimensions from the Cube meta model.
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
    """
    Parse the Cube meta model and return a simplified version.
    """

    lookml_model = {
        "views": [],
        "explores": [],
    }

    for model in cube_model.get("cubes", []):

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

        lookml_model["views"].append(view)

    return lookml_model
