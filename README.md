# lkml2cube

lkml2cube is a tool that converts LookML models into Cube data models.

## Usage

There are two main commands, `cubes` and `views`. Both commands read all the files in the provided input parameter, including those referenced by the LookML keyword `includes`.
The difference is that the `cubes` command only creates Cube's `cube` model definitions, while the `views` command creates `cube` and `view` model definitions. LookML syntax defines the join relationships at the explore level (equivalent to Cube's `view`). That's why explores need special treatment and why they are ignored in the lkml2cube `cubes` command.

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

### Use the `--rootdir` parameter to prepend a path for all `include:` paths.
```sh
lkml2cube views ../my_lookml_project/views/countries.view.lkml --outputdir model/ --rootdir ../my_lookml_project/
```

