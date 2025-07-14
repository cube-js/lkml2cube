import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from lkml2cube.parser.loader import (
    write_lookml_files,
    _generate_lookml_content,
    _generate_dimension_lines,
    _generate_measure_lines,
    _generate_filter_lines,
)


class TestLookMLWriter:
    """Test suite for LookML file writing functionality."""

    def test_write_lookml_files_with_views(self):
        """Test writing LookML files for views."""
        lookml_model = {
            "views": [
                {
                    "name": "orders",
                    "label": "Orders Table",
                    "sql_table_name": "public.orders",
                    "dimensions": [
                        {
                            "name": "id",
                            "label": "Order ID",
                            "type": "number",
                            "sql": "${TABLE}.id"
                        }
                    ],
                    "measures": [
                        {
                            "name": "count",
                            "label": "Count of Orders",
                            "type": "count",
                            "sql": "*"
                        }
                    ]
                }
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            summary = write_lookml_files(lookml_model, temp_dir)

            # Check summary structure
            assert "views" in summary
            assert len(summary["views"]) == 1
            assert summary["views"][0]["name"] == "orders"

            # Check file was created
            expected_path = Path(temp_dir) / "views" / "orders.view.lkml"
            assert expected_path.exists()

            # Check file content
            with open(expected_path, "r") as f:
                content = f.read()
                assert "view orders {" in content
                assert 'label: "Orders Table"' in content
                assert "sql_table_name: public.orders ;;" in content
                assert "dimension: id {" in content
                assert "measure: count {" in content

    def test_write_lookml_files_with_explores(self):
        """Test writing LookML files for explores."""
        lookml_model = {
            "explores": [
                {
                    "name": "order_analysis",
                    "label": "Order Analysis"
                }
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            summary = write_lookml_files(lookml_model, temp_dir)

            # Check summary structure
            assert "explores" in summary
            assert len(summary["explores"]) == 1
            assert summary["explores"][0]["name"] == "order_analysis"

            # Check file was created
            expected_path = Path(temp_dir) / "explores" / "order_analysis.explore.lkml"
            assert expected_path.exists()

            # Check file content
            with open(expected_path, "r") as f:
                content = f.read()
                assert "explore order_analysis {" in content
                assert 'label: "Order Analysis"' in content

    def test_write_lookml_files_empty_model(self):
        """Test handling of empty LookML model."""
        with pytest.raises(Exception, match="No LookML model available"):
            write_lookml_files(None, "/tmp")

        with pytest.raises(Exception, match="No LookML model available"):
            write_lookml_files({}, "/tmp")

    def test_write_lookml_files_creates_directories(self):
        """Test that directories are created as needed."""
        lookml_model = {
            "views": [{"name": "test_view"}],
            "explores": [{"name": "test_explore"}]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            write_lookml_files(lookml_model, temp_dir)

            views_dir = Path(temp_dir) / "views"
            explores_dir = Path(temp_dir) / "explores"

            assert views_dir.exists() and views_dir.is_dir()
            assert explores_dir.exists() and explores_dir.is_dir()


class TestLookMLContentGeneration:
    """Test suite for LookML content generation functions."""

    def test_generate_lookml_content_view_basic(self):
        """Test basic view content generation."""
        view_element = {
            "name": "orders",
            "label": "Orders Table"
        }

        content = _generate_lookml_content(view_element, "view")
        lines = content.split("\n")

        assert lines[0] == "view orders {"
        assert '  label: "Orders Table"' in lines
        assert lines[-1] == "}"

    def test_generate_lookml_content_view_with_sql_table(self):
        """Test view content generation with SQL table."""
        view_element = {
            "name": "orders",
            "sql_table_name": "public.orders"
        }

        content = _generate_lookml_content(view_element, "view")
        assert "sql_table_name: public.orders ;;" in content

    def test_generate_lookml_content_view_with_derived_table(self):
        """Test view content generation with derived table."""
        view_element = {
            "name": "orders",
            "derived_table": {
                "sql": "SELECT * FROM orders WHERE status = 'active'"
            }
        }

        content = _generate_lookml_content(view_element, "view")
        assert "derived_table: {" in content
        assert "sql: SELECT * FROM orders WHERE status = 'active' ;;" in content

    def test_generate_lookml_content_view_with_multiline_sql(self):
        """Test view content generation with multiline SQL."""
        view_element = {
            "name": "orders",
            "derived_table": {
                "sql": "SELECT *\nFROM orders\nWHERE status = 'active'"
            }
        }

        content = _generate_lookml_content(view_element, "view")
        lines = content.split("\n")
        
        assert "sql:" in content
        assert "SELECT *" in content
        assert "FROM orders" in content
        assert "WHERE status = 'active'" in content

    def test_generate_lookml_content_view_with_extends(self):
        """Test view content generation with extends."""
        view_element = {
            "name": "orders",
            "extends": ["base_table"]
        }

        content = _generate_lookml_content(view_element, "view")
        assert "extends: [base_table]" in content

    def test_generate_lookml_content_explore_basic(self):
        """Test basic explore content generation."""
        explore_element = {
            "name": "order_analysis",
            "label": "Order Analysis"
        }

        content = _generate_lookml_content(explore_element, "explore")
        lines = content.split("\n")

        assert lines[0] == "explore order_analysis {"
        assert '  label: "Order Analysis"' in lines
        assert lines[-1] == "}"

    def test_generate_dimension_lines_basic(self):
        """Test basic dimension line generation."""
        dimension = {
            "name": "order_id",
            "label": "Order ID",
            "type": "number",
            "sql": "${TABLE}.id"
        }

        lines = _generate_dimension_lines(dimension)
        content = "\n".join(lines)

        assert "dimension: order_id {" in content
        assert 'label: "Order ID"' in content
        assert "type: number" in content
        assert "sql: ${TABLE}.id ;;" in content

    def test_generate_dimension_lines_with_description(self):
        """Test dimension line generation with description."""
        dimension = {
            "name": "order_id",
            "description": "Unique identifier for orders",
            "type": "number"
        }

        lines = _generate_dimension_lines(dimension)
        content = "\n".join(lines)

        assert 'description: "Unique identifier for orders"' in content

    def test_generate_dimension_lines_hidden(self):
        """Test dimension line generation with hidden property."""
        dimension = {
            "name": "internal_id",
            "type": "number",
            "hidden": "yes"
        }

        lines = _generate_dimension_lines(dimension)
        content = "\n".join(lines)

        assert "hidden: yes" in content

    def test_generate_dimension_lines_multiline_sql(self):
        """Test dimension line generation with multiline SQL."""
        dimension = {
            "name": "complex_field",
            "type": "string",
            "sql": "CASE\n  WHEN status = 'A' THEN 'Active'\n  ELSE 'Inactive'\nEND"
        }

        lines = _generate_dimension_lines(dimension)
        content = "\n".join(lines)

        assert "sql:" in content
        assert "CASE" in content
        assert "WHEN status = 'A' THEN 'Active'" in content
        assert ";;" in content

    def test_generate_measure_lines_basic(self):
        """Test basic measure line generation."""
        measure = {
            "name": "total_sales",
            "label": "Total Sales",
            "type": "sum",
            "sql": "${TABLE}.amount"
        }

        lines = _generate_measure_lines(measure)
        content = "\n".join(lines)

        assert "measure: total_sales {" in content
        assert 'label: "Total Sales"' in content
        assert "type: sum" in content
        assert "sql: ${TABLE}.amount ;;" in content

    def test_generate_measure_lines_with_description_and_hidden(self):
        """Test measure line generation with description and hidden."""
        measure = {
            "name": "internal_metric",
            "description": "Internal calculation metric",
            "type": "number",
            "hidden": "yes"
        }

        lines = _generate_measure_lines(measure)
        content = "\n".join(lines)

        assert 'description: "Internal calculation metric"' in content
        assert "hidden: yes" in content

    def test_generate_filter_lines_basic(self):
        """Test basic filter line generation."""
        filter_def = {
            "name": "date_filter",
            "label": "Date Filter",
            "type": "date"
        }

        lines = _generate_filter_lines(filter_def)
        content = "\n".join(lines)

        assert "filter: date_filter {" in content
        assert 'label: "Date Filter"' in content
        assert "type: date" in content

    def test_generate_filter_lines_with_description(self):
        """Test filter line generation with description."""
        filter_def = {
            "name": "status_filter",
            "description": "Filter by order status",
            "type": "string"
        }

        lines = _generate_filter_lines(filter_def)
        content = "\n".join(lines)

        assert 'description: "Filter by order status"' in content


class TestLookMLIntegration:
    """Integration tests for LookML writing functionality."""

    def test_full_view_generation(self):
        """Test complete view file generation with all components."""
        lookml_model = {
            "views": [
                {
                    "name": "comprehensive_view",
                    "label": "Comprehensive Test View",
                    "sql_table_name": "schema.table",
                    "extends": ["base_view"],
                    "dimensions": [
                        {
                            "name": "id",
                            "label": "ID",
                            "type": "number",
                            "sql": "${TABLE}.id",
                            "description": "Primary key"
                        },
                        {
                            "name": "hidden_field",
                            "type": "string",
                            "sql": "${TABLE}.internal",
                            "hidden": "yes"
                        }
                    ],
                    "measures": [
                        {
                            "name": "count",
                            "label": "Count",
                            "type": "count",
                            "sql": "*"
                        }
                    ],
                    "filters": [
                        {
                            "name": "date_range",
                            "label": "Date Range",
                            "type": "date"
                        }
                    ]
                }
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            summary = write_lookml_files(lookml_model, temp_dir)

            # Verify file creation and content
            file_path = Path(temp_dir) / "views" / "comprehensive_view.view.lkml"
            assert file_path.exists()

            with open(file_path, "r") as f:
                content = f.read()

            # Check all components are present
            assert "view comprehensive_view {" in content
            assert 'label: "Comprehensive Test View"' in content
            assert "sql_table_name: schema.table ;;" in content
            assert "extends: [base_view]" in content
            assert "dimension: id {" in content
            assert "dimension: hidden_field {" in content
            assert "measure: count {" in content
            assert "filter: date_range {" in content
            assert "hidden: yes" in content

    def test_multiple_views_and_explores(self):
        """Test writing multiple views and explores."""
        lookml_model = {
            "views": [
                {"name": "view1", "label": "First View"},
                {"name": "view2", "label": "Second View"}
            ],
            "explores": [
                {"name": "explore1", "label": "First Explore"},
                {"name": "explore2", "label": "Second Explore"}
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            summary = write_lookml_files(lookml_model, temp_dir)

            # Check summary
            assert len(summary["views"]) == 2
            assert len(summary["explores"]) == 2

            # Check all files exist
            view1_path = Path(temp_dir) / "views" / "view1.view.lkml"
            view2_path = Path(temp_dir) / "views" / "view2.view.lkml"
            explore1_path = Path(temp_dir) / "explores" / "explore1.explore.lkml"
            explore2_path = Path(temp_dir) / "explores" / "explore2.explore.lkml"

            assert view1_path.exists()
            assert view2_path.exists()
            assert explore1_path.exists()
            assert explore2_path.exists()

    def test_empty_elements_handling(self):
        """Test handling of elements without names."""
        lookml_model = {
            "views": [
                {"name": "valid_view"},
                {"label": "No name view"},  # Missing name
                {"name": ""}  # Empty name
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            summary = write_lookml_files(lookml_model, temp_dir)

            # Should only create file for valid view
            assert len(summary["views"]) == 1
            assert summary["views"][0]["name"] == "valid_view"

            # Only one file should exist
            files = list(Path(temp_dir).rglob("*.lkml"))
            assert len(files) == 1