import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, Mock
from typer.testing import CliRunner

from lkml2cube.main import app


class TestExploresCommand:
    """Integration tests for the explores command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        
        # Sample Cube meta API response with both cubes and views
        self.sample_cube_meta = {
            "cubes": [
                {
                    "name": "orders",
                    "title": "Orders Table",
                    "sql_table": "public.orders",
                    "dimensions": [
                        {
                            "name": "id",
                            "title": "Order ID",
                            "type": "number",
                            "sql": "${TABLE}.id",
                            "public": True
                        },
                        {
                            "name": "status",
                            "title": "Order Status",
                            "type": "string",
                            "sql": "${TABLE}.status",
                            "public": True,
                            "description": "Status of the order"
                        },
                        {
                            "name": "internal_code",
                            "type": "string",
                            "sql": "${TABLE}.internal_code",
                            "public": False  # This should be hidden
                        }
                    ],
                    "measures": [
                        {
                            "name": "count",
                            "title": "Order Count",
                            "type": "count",
                            "aggType": "count",
                            "sql": "*",
                            "public": True
                        },
                        {
                            "name": "total_amount",
                            "title": "Total Amount",
                            "type": "sum",
                            "aggType": "sum",
                            "sql": "${TABLE}.amount",
                            "public": True,
                            "description": "Total order amount"
                        }
                    ]
                },
                {
                    "name": "customers",
                    "title": "Customer Information",
                    "sql": "SELECT * FROM customers WHERE active = true",
                    "dimensions": [
                        {
                            "name": "customer_id",
                            "title": "Customer ID",
                            "type": "number",
                            "sql": "${TABLE}.id",
                            "public": True
                        }
                    ],
                    "measures": [
                        {
                            "name": "customer_count",
                            "title": "Customer Count",
                            "type": "count",
                            "aggType": "count",
                            "sql": "*",
                            "public": True
                        }
                    ]
                },
                # Add a Cube view that should become a LookML explore
                {
                    "name": "order_summary",
                    "title": "Order Summary Analysis",
                    "description": "Combined view of orders and customer data",
                    "dimensions": [
                        {
                            "aliasMember": "orders.id",
                            "name": "order_summary.order_id",
                            "title": "Order ID",
                            "type": "number",
                            "public": True
                        },
                        {
                            "aliasMember": "customers.customer_id",
                            "name": "order_summary.customer_id", 
                            "title": "Customer ID",
                            "type": "number",
                            "public": True
                        }
                    ],
                    "measures": [
                        {
                            "aliasMember": "orders.total_amount",
                            "name": "order_summary.total_revenue",
                            "title": "Total Revenue",
                            "type": "number",
                            "public": True
                        }
                    ]
                }
            ]
        }

    @patch('lkml2cube.parser.cube_api.requests.get')
    def test_explores_command_parseonly(self, mock_get):
        """Test explores command with parseonly option."""
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_cube_meta
        mock_get.return_value = mock_response

        result = self.runner.invoke(app, [
            "explores",
            "http://localhost:4000/cubejs-api/v1/meta",
            "--token", "test-token",
            "--parseonly"
        ])

        assert result.exit_code == 0
        # Should contain the original cube meta data
        assert "orders" in result.stdout
        assert "customers" in result.stdout

    @patch('lkml2cube.parser.cube_api.requests.get')
    def test_explores_command_printonly(self, mock_get):
        """Test explores command with printonly option."""
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_cube_meta
        mock_get.return_value = mock_response

        result = self.runner.invoke(app, [
            "explores",
            "http://localhost:4000/cubejs-api/v1/meta",
            "--token", "test-token",
            "--printonly"
        ])

        assert result.exit_code == 0
        # Should contain the converted LookML model as YAML
        assert "views:" in result.stdout
        assert "explores:" in result.stdout
        assert "name: orders" in result.stdout
        assert "name: customers" in result.stdout  
        assert "name: order_summary" in result.stdout

    @patch('lkml2cube.parser.cube_api.requests.get')
    def test_explores_command_write_files(self, mock_get):
        """Test explores command writing files to output directory."""
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_cube_meta
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(app, [
                "explores",
                "http://localhost:4000/cubejs-api/v1/meta",
                "--token", "test-token",
                "--outputdir", temp_dir
            ])

            assert result.exit_code == 0

            # Check that files were created
            views_dir = Path(temp_dir) / "views"
            explores_dir = Path(temp_dir) / "explores"
            assert views_dir.exists()
            assert explores_dir.exists()

            orders_file = views_dir / "orders.view.lkml"
            customers_file = views_dir / "customers.view.lkml"
            order_summary_file = explores_dir / "order_summary.explore.lkml"

            assert orders_file.exists()
            assert customers_file.exists()
            assert order_summary_file.exists()

            # Check orders file content
            with open(orders_file, "r") as f:
                orders_content = f.read()

            assert "view orders {" in orders_content
            assert 'label: "Orders Table"' in orders_content
            assert "sql_table_name: public.orders ;;" in orders_content
            assert "dimension: id {" in orders_content
            assert "dimension: status {" in orders_content
            assert "dimension: internal_code {" in orders_content
            assert "measure: count {" in orders_content
            assert "measure: total_amount {" in orders_content
            assert "hidden: yes" in orders_content  # For internal_code
            assert 'description: "Status of the order"' in orders_content
            assert 'description: "Total order amount"' in orders_content

            # Check customers file content
            with open(customers_file, "r") as f:
                customers_content = f.read()

            assert "view customers {" in customers_content
            assert 'label: "Customer Information"' in customers_content
            assert "derived_table: {" in customers_content
            assert "sql: SELECT * FROM customers WHERE active = true ;;" in customers_content
            assert "dimension: customer_id {" in customers_content
            assert "measure: customer_count {" in customers_content

            # Check explore file content
            with open(order_summary_file, "r") as f:
                explore_content = f.read()

            assert "explore order_summary {" in explore_content
            assert 'label: "Order Summary Analysis"' in explore_content
            assert "view_name:" in explore_content
            assert "join:" in explore_content
            assert "type: left_outer" in explore_content
            assert "sql_on:" in explore_content

            # Check summary output - Rich tables are output as objects in test mode
            # Just verify the command completed successfully
            assert result.exit_code == 0

    @patch('lkml2cube.parser.cube_api.requests.get')
    def test_explores_command_api_error(self, mock_get):
        """Test explores command handling API errors."""
        # Mock a failed API response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        result = self.runner.invoke(app, [
            "explores",
            "http://localhost:4000/cubejs-api/v1/meta",
            "--token", "invalid-token"
        ])

        assert result.exit_code == 1
        assert "Failed to fetch meta data" in str(result.exception)

    @patch('lkml2cube.parser.cube_api.requests.get')
    def test_explores_command_no_response(self, mock_get):
        """Test explores command handling when no response received."""
        # Mock no response (None return)
        mock_get.side_effect = Exception("Connection failed")

        result = self.runner.invoke(app, [
            "explores",
            "http://localhost:4000/cubejs-api/v1/meta",
            "--token", "test-token"
        ])

        assert result.exit_code == 1

    @patch('lkml2cube.parser.cube_api.requests.get')
    def test_explores_command_extended_url(self, mock_get):
        """Test that explores command adds ?extended to URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"cubes": []}
        mock_get.return_value = mock_response

        result = self.runner.invoke(app, [
            "explores",
            "http://localhost:4000/cubejs-api/v1/meta",
            "--token", "test-token",
            "--printonly"
        ])

        assert result.exit_code == 0
        # Verify the URL was called with ?extended
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "http://localhost:4000/cubejs-api/v1/meta?extended"

    @patch('lkml2cube.parser.cube_api.requests.get')
    def test_explores_command_custom_output_dir(self, mock_get):
        """Test explores command with custom output directory."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cubes": [
                {
                    "name": "test_cube",
                    "dimensions": [{"name": "test_dim", "type": "string", "sql": "test", "public": True}],
                    "measures": []
                }
            ]
        }
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            custom_output = Path(temp_dir) / "custom" / "output"
            
            result = self.runner.invoke(app, [
                "explores",
                "http://localhost:4000/cubejs-api/v1/meta",
                "--token", "test-token",
                "--outputdir", str(custom_output)
            ])

            assert result.exit_code == 0

            # Check that custom directory structure was created
            views_dir = custom_output / "views"
            assert views_dir.exists()

            test_file = views_dir / "test_cube.view.lkml"
            assert test_file.exists()

    @patch('lkml2cube.parser.cube_api.requests.get')
    def test_explores_command_complex_sql(self, mock_get):
        """Test explores command with complex multiline SQL."""
        complex_cube_meta = {
            "cubes": [
                {
                    "name": "complex_view",
                    "sql": "SELECT\n  id,\n  name,\n  CASE\n    WHEN status = 'A' THEN 'Active'\n    ELSE 'Inactive'\n  END as status_desc\nFROM users",
                    "dimensions": [
                        {
                            "name": "complex_dimension",
                            "type": "string",
                            "sql": "CASE\n  WHEN ${TABLE}.type = 'premium'\n  THEN 'Premium User'\n  ELSE 'Regular User'\nEND",
                            "public": True
                        }
                    ],
                    "measures": []
                }
            ]
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = complex_cube_meta
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(app, [
                "explores",
                "http://localhost:4000/cubejs-api/v1/meta",
                "--token", "test-token",
                "--outputdir", temp_dir
            ])

            assert result.exit_code == 0

            # Check file content for proper multiline SQL handling
            view_file = Path(temp_dir) / "views" / "complex_view.view.lkml"
            assert view_file.exists()

            with open(view_file, "r") as f:
                content = f.read()

            # Check derived table multiline SQL
            assert "derived_table: {" in content
            assert "sql:" in content
            assert "SELECT" in content
            assert "CASE" in content
            assert "FROM users" in content

            # Check dimension multiline SQL
            assert "dimension: complex_dimension {" in content
            assert "WHEN ${TABLE}.type = 'premium'" in content
            assert "THEN 'Premium User'" in content