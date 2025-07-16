import rich


# console = rich.console.Console()
class Console:
    """Simple console wrapper for printing messages.
    
    This class provides a basic print interface compatible with Rich console
    while falling back to standard print functionality.
    """
    
    def print(self, s, *args):
        """Print a message to the console.
        
        Args:
            s (str): Message to print.
            *args: Additional arguments (currently ignored).
        
        Example:
            >>> console = Console()
            >>> console.print("Hello world", style="bold")
            Hello world
        """
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
    """String subclass for YAML folded scalar representation.
    
    This class marks strings that should be represented as folded scalars
    in YAML output (using the '>' style).
    
    Example:
        >>> text = folded_unicode("This is a long\nstring that will be folded")
        >>> # When dumped to YAML, will use '>' style
    """
    pass


class literal_unicode(str):
    """String subclass for YAML literal scalar representation.
    
    This class marks strings that should be represented as literal scalars
    in YAML output (using the '|' style).
    
    Example:
        >>> sql = literal_unicode("SELECT *\nFROM table\nWHERE id = 1")
        >>> # When dumped to YAML, will use '|' style preserving line breaks
    """
    pass


def folded_unicode_representer(dumper, data):
    """YAML representer for folded_unicode strings.
    
    Args:
        dumper: YAML dumper instance.
        data (folded_unicode): String data to represent.
    
    Returns:
        Scalar representation with folded style.
    
    Example:
        >>> import yaml
        >>> yaml.add_representer(folded_unicode, folded_unicode_representer)
        >>> yaml.dump(folded_unicode("long text"))
        '> long text\n'
    """
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")


def literal_unicode_representer(dumper, data):
    """YAML representer for literal_unicode strings.
    
    Args:
        dumper: YAML dumper instance.
        data (literal_unicode): String data to represent.
    
    Returns:
        Scalar representation with literal style.
    
    Example:
        >>> import yaml
        >>> yaml.add_representer(literal_unicode, literal_unicode_representer)
        >>> yaml.dump(literal_unicode("SELECT *\nFROM table"))
        '|\n  SELECT *\n  FROM table\n'
    """
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
