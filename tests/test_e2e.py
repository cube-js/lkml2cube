import pytest
import yaml

from os.path import join, dirname

from lkml2cube.parser.loader import file_loader
from lkml2cube.parser.views import parse_view
from lkml2cube.parser.explores import parse_explores, generate_cube_joins

# Dynamically calculate the root directory
rootdir = join(dirname(__file__), "samples")


def _find_cube(cube_def, name):
    for cube in cube_def.get("cubes", []):
        if cube.get("name") == name:
            return cube
    return None


class TestExamples:
    def setup_method(self):
        """Set up test fixtures."""
        # Clear the global visited_path cache to prevent interference between tests
        from lkml2cube.parser import loader
        loader.visited_path.clear()

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


class TestJoinDirection:
    """Joins from an explore must land on the explore's base cube, with the
    LookML relationship preserved verbatim.

    Per Cube docs (https://cube.dev/docs/product/data-modeling/reference/joins):

        > The join does not need to be defined on both cubes, but the
        > definition can affect the join direction.
        > The cube which defines the join serves as a main table.

    The explore name in LookML *is* the base view — queries run from there,
    so the join must be declared on that cube to keep it as the main (LEFT)
    table in the generated SQL. Declaring on the joined-target cube with the
    same relationship value silently flips cardinality.
    """

    def setup_method(self):
        from lkml2cube.parser import loader
        loader.visited_path.clear()

    def _build(self):
        # The fixture's `include: "/views/*.view.lkml"` is relative to the
        # LookML project root (`tests/samples/lkml`), not the test samples
        # root — same Looker convention that the model files use.
        lkml_rootdir = join(rootdir, "lkml")
        file_path = join(lkml_rootdir, "explores/orders_summary.model.lkml")
        lookml_model = file_loader(file_path, lkml_rootdir)
        assert lookml_model is not None, "fixture failed to load"
        cube_def = parse_view(lookml_model, raise_when_views_not_present=False)
        return generate_cube_joins(cube_def, lookml_model)

    def test_one_to_many_lands_on_explore_base_cube(self):
        # explore: orders { join: line_items { relationship: one_to_many ... } }
        # Forward-side emit: cubes.orders.joins must contain line_items, rel one_to_many.
        cube_def = self._build()
        orders = _find_cube(cube_def, "orders")
        assert orders is not None
        joins = {j["name"]: j for j in orders.get("joins") or []}
        assert "line_items" in joins, (
            f"orders.joins missing line_items; got {list(joins)}"
        )
        assert joins["line_items"]["relationship"] == "one_to_many"

    def test_join_lands_on_sql_on_left_side_not_explore_base(self):
        # explore: orders { join: products { relationship: many_to_one
        #   sql_on: ${line_items.product_id} = ${products.id} } }
        # The sql_on references line_items, not orders — meaning the hop is
        # line_items → products, even though the join is declared inside
        # `explore: orders`. Cube's join graph uses Dijkstra to traverse, so
        # an `orders` query needing `products` walks orders→line_items→products.
        # Declaring the products join on `orders` would generate a wrong SQL
        # join because there's no orders.product_id column.
        cube_def = self._build()
        line_items = _find_cube(cube_def, "line_items")
        assert line_items is not None
        joins = {j["name"]: j for j in line_items.get("joins") or []}
        assert "products" in joins, (
            f"line_items.joins missing products; got {list(joins)}"
        )
        assert joins["products"]["relationship"] == "many_to_one"

    def test_separate_explore_writes_to_its_own_base(self):
        # The fixture also has: explore: line_items { join: orders {...},
        #   join: products {...} }. Those joins must land on cubes.line_items,
        # not on cubes.orders / cubes.products.
        cube_def = self._build()
        line_items = _find_cube(cube_def, "line_items")
        assert line_items is not None
        join_names = {j["name"] for j in line_items.get("joins") or []}
        assert {"orders", "products"} <= join_names, (
            f"line_items.joins missing one of orders/products; got {join_names}"
        )

    def test_target_cube_does_not_receive_inverse_join(self):
        # Regression guard: previously every explore-join was written to the
        # target cube with the LookML relationship copied verbatim, producing
        # cubes.line_items.joins.orders with relationship one_to_many — the
        # uninverted cardinality from the wrong side. The fix removes that
        # write entirely; the inverse-direction join only appears if a
        # separate explore declares it (here `explore: line_items` does, so
        # cubes.line_items.joins.orders exists at many_to_one, which is fine).
        cube_def = self._build()
        line_items = _find_cube(cube_def, "line_items")
        assert line_items is not None
        joins = {j["name"]: j for j in line_items.get("joins") or []}
        # Only one entry pointing at orders, with the relationship from the
        # line_items explore (many_to_one), not the orders explore's value.
        assert joins.get("orders", {}).get("relationship") == "many_to_one"
