# lkml2cube

lkml2cube is a tool to convert LookML models into Cube data models.

## Usage

Currently the only supported type of LookML object is views.

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

### Convert LookML Explroes into Cube's views YAML definition.

```sh
lkml2cube views path/to/file.explore.lkml --outputdir examples/
```
