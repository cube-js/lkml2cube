import pytest
import yaml

from os.path import join, dirname

from lkml2cube.parser.loader import file_loader
from lkml2cube.parser.views import parse_view
from lkml2cube.parser.explores import parse_explores, generate_cube_joins

# Dynamically calculate the root directory
rootdir = join(dirname(__file__), "samples")


class TestExamples:
    def test_simple_view(self):
        file_path = "lkml/views/orders.view.lkml"
        # print(join(rootdir, file_path))
        lookml_model = file_loader(join(rootdir, file_path), rootdir)

        # lookml_model can't be None
        # if None it means file was not found or couldn't be parsed
        assert lookml_model is not None

        cube_def = parse_view(lookml_model)
        cube_def = generate_cube_joins(cube_def, lookml_model)

        # Convert the generated cube definition to a dictionary
        generated_yaml = yaml.safe_load(yaml.dump(cube_def, allow_unicode=True))

        # print("Expected yaml:")
        # print(yaml.dump(generated_yaml, allow_unicode=True))

        file_path = "cubeml/orders.yml"
        # print(join(rootdir, file_path))
        with open(join(rootdir, file_path)) as f:
            cube_model = yaml.safe_load(f)

        # print(cube_model)

        # Compare the two dictionaries
        assert (
            generated_yaml == cube_model
        ), "Generated YAML does not match the expected YAML"
