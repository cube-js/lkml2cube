# Table of Contents

* [lkml2cube.parser.types](#lkml2cube.parser.types)
  * [Console](#lkml2cube.parser.types.Console)
    * [print](#lkml2cube.parser.types.Console.print)
  * [folded\_unicode](#lkml2cube.parser.types.folded_unicode)
  * [literal\_unicode](#lkml2cube.parser.types.literal_unicode)
  * [folded\_unicode\_representer](#lkml2cube.parser.types.folded_unicode_representer)
  * [literal\_unicode\_representer](#lkml2cube.parser.types.literal_unicode_representer)

<a id="lkml2cube.parser.types"></a>

# lkml2cube.parser.types

<a id="lkml2cube.parser.types.Console"></a>

## Console Objects

```python
class Console()
```

Simple console wrapper for printing messages.

This class provides a basic print interface compatible with Rich console
while falling back to standard print functionality.

<a id="lkml2cube.parser.types.Console.print"></a>

#### print

```python
def print(s, *args)
```

Print a message to the console.

**Arguments**:

- `s` _str_ - Message to print.
- `*args` - Additional arguments (currently ignored).
  

**Example**:

  >>> console = Console()
  >>> console.print("Hello world", style="bold")
  Hello world

<a id="lkml2cube.parser.types.folded_unicode"></a>

## folded\_unicode Objects

```python
class folded_unicode(str)
```

String subclass for YAML folded scalar representation.

This class marks strings that should be represented as folded scalars
in YAML output (using the '>' style).

**Example**:

  >>> text = folded_unicode("This is a long
  string that will be folded")
  >>> # When dumped to YAML, will use '>' style

<a id="lkml2cube.parser.types.literal_unicode"></a>

## literal\_unicode Objects

```python
class literal_unicode(str)
```

String subclass for YAML literal scalar representation.

This class marks strings that should be represented as literal scalars
in YAML output (using the '|' style).

**Example**:

  >>> sql = literal_unicode("SELECT *
  FROM table
  WHERE id = 1")
  >>> # When dumped to YAML, will use '|' style preserving line breaks

<a id="lkml2cube.parser.types.folded_unicode_representer"></a>

#### folded\_unicode\_representer

```python
def folded_unicode_representer(dumper, data)
```

YAML representer for folded_unicode strings.

**Arguments**:

- `dumper` - YAML dumper instance.
- `data` _folded_unicode_ - String data to represent.
  

**Returns**:

  Scalar representation with folded style.
  

**Example**:

  >>> import yaml
  >>> yaml.add_representer(folded_unicode, folded_unicode_representer)
  >>> yaml.dump(folded_unicode("long text"))
  '> long text
  '

<a id="lkml2cube.parser.types.literal_unicode_representer"></a>

#### literal\_unicode\_representer

```python
def literal_unicode_representer(dumper, data)
```

YAML representer for literal_unicode strings.

**Arguments**:

- `dumper` - YAML dumper instance.
- `data` _literal_unicode_ - String data to represent.
  

**Returns**:

  Scalar representation with literal style.
  

**Example**:

  >>> import yaml
  >>> yaml.add_representer(literal_unicode, literal_unicode_representer)
  >>> yaml.dump(literal_unicode("SELECT *
  FROM table"))
  '|
  SELECT *
  FROM table
  '

