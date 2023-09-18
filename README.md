# lkml2cube

lkml2cube is a tool to convert LookML models into Cube data models.

## Usage

There are two main commands, `cubes` and `views`. Both commands read all the files in the provided input parameter, including those referenced by the LookML keyword `includes`.
The difference is that the `cubes` command only creates Cube's `cube` model definitions, while the `views` command creates `cube` and `view` model definitions. In LookML syntax, the join relationships are defined at the explore level (equivalent to Cube's `view`). That's the reason explores need special treatment and also the reason for explores to be ignored in the lkml2cube `cubes` command.

### Install

```sh
pip install lkml2cube
```

### Convert LookML views into Cube YAML definition.

```sh
lkml2cube cubes path/to/file.view.lkml --outputdir examples/
```

### Show Python dict representation of the LookerML object

```sh
lkml2cube cubes --parseonly path/to/file.view.lkml
```

### Convert LookML Explores into Cube's views YAML definition.

```sh
lkml2cube views path/to/file.explore.lkml --outputdir examples/
```
