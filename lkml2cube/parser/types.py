import rich


# console = rich.console.Console()
class Console:
    def print(self, s, *args):
        print(s)


console = Console()

type_map = {
    "zipcode": "string",
    "string": "string",
    "number": "number",
    "tier": "number",
    "count": "count",
    "yesno": "boolean",
    "sum": "sum",
    "sum_distinct": "sum",
    "average": "avg",
    "average_distinct": "avg",
    "date": "time",
    "time": "time",
    "count_distinct": "count_distinct_approx",
}

reverse_type_map = {
    "string": "string",
    "number": "number",
    "count": "count",
    "boolean": "yesno",
    "sum": "sum",
    "avg": "average",
    "time": "time",
    "count_distinct": "count_distinct",
    "count_distinct_approx": "count_distinct",
}


class folded_unicode(str):
    pass


class literal_unicode(str):
    pass


def folded_unicode_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")


def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
