"""
Unit tests for the LookMLConverter class.

This module contains comprehensive tests for the LookMLConverter class,
including initialization, configuration management, and all core conversion methods.
"""

import pytest
import yaml
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock, mock_open
from os.path import join, dirname

from lkml2cube.converter import LookMLConverter


class TestLookMLConverterInitialization:
    """Test LookMLConverter initialization and configuration."""

    def test_default_initialization(self):
        """Test LookMLConverter with default parameters."""
        converter = LookMLConverter()
        
        assert converter.outputdir == "."
        assert converter.rootdir is None
        assert converter.parseonly is False
        assert converter.printonly is False
        assert converter.use_explores_name is False

    def test_custom_initialization(self):
        """Test LookMLConverter with custom parameters."""
        converter = LookMLConverter(
            outputdir="/tmp/output",
            rootdir="/tmp/root",
            parseonly=True,
            printonly=True,
            use_explores_name=True
        )
        
        assert converter.outputdir == "/tmp/output"
        assert converter.rootdir == "/tmp/root"
        assert converter.parseonly is True
        assert converter.printonly is True
        assert converter.use_explores_name is True

    def test_string_representation(self):
        """Test __repr__ method."""
        converter = LookMLConverter(outputdir="/tmp")
        repr_str = repr(converter)
        
        assert "LookMLConverter" in repr_str
        assert "outputdir='/tmp'" in repr_str
        assert "rootdir='None'" in repr_str
        assert "parseonly=False" in repr_str


class TestLookMLConverterConfiguration:
    """Test configuration management methods."""

    def test_get_config(self):
        """Test get_config method."""
        converter = LookMLConverter(outputdir="/tmp", parseonly=True)
        config = converter.get_config()
        
        expected_config = {
            'outputdir': '/tmp',
            'rootdir': None,
            'parseonly': True,
            'printonly': False,
            'use_explores_name': False
        }
        
        assert config == expected_config

    def test_set_config_partial(self):
        """Test set_config with partial updates."""
        converter = LookMLConverter()
        
        converter.set_config(outputdir="/new/path", parseonly=True)
        
        assert converter.outputdir == "/new/path"
        assert converter.parseonly is True
        assert converter.printonly is False  # Should remain unchanged

    def test_set_config_all_params(self):
        """Test set_config with all parameters."""
        converter = LookMLConverter()
        
        converter.set_config(
            outputdir="/new/path",
            rootdir="/new/root",
            parseonly=True,
            printonly=True,
            use_explores_name=True
        )
        
        assert converter.outputdir == "/new/path"
        assert converter.rootdir == "/new/root"
        assert converter.parseonly is True
        assert converter.printonly is True
        assert converter.use_explores_name is True

    def test_set_config_none_values(self):
        """Test set_config with None values (should not change)."""
        converter = LookMLConverter(outputdir="/original", parseonly=True)
        
        converter.set_config(outputdir=None, parseonly=None)
        
        assert converter.outputdir == "/original"
        assert converter.parseonly is True


class TestLookMLConverterCubes:
    """Test the cubes() method."""

    @patch('lkml2cube.converter.file_loader')
    def test_cubes_file_not_found(self, mock_file_loader):
        """Test cubes method when file is not found."""
        mock_file_loader.return_value = None
        converter = LookMLConverter()
        
        with pytest.raises(ValueError, match="No files were found on path"):
            converter.cubes("nonexistent.lkml")

    @patch('lkml2cube.converter.file_loader')
    def test_cubes_parseonly(self, mock_file_loader):
        """Test cubes method with parseonly=True."""
        sample_lookml = {
            'views': [{'name': 'orders', 'sql_table_name': 'orders'}]
        }
        mock_file_loader.return_value = sample_lookml
        
        converter = LookMLConverter(parseonly=True)
        result = converter.cubes("test.lkml")
        
        assert 'lookml_model' in result
        assert 'parsed_model' in result
        assert result['lookml_model'] == sample_lookml
        assert isinstance(result['parsed_model'], str)

    @patch('lkml2cube.converter.console')
    @patch('lkml2cube.converter.yaml.dump')
    @patch('lkml2cube.converter.generate_cube_joins')
    @patch('lkml2cube.converter.parse_view')
    @patch('lkml2cube.converter.file_loader')
    def test_cubes_printonly(self, mock_file_loader, mock_parse_view, 
                           mock_generate_joins, mock_yaml_dump, mock_console):
        """Test cubes method with printonly=True."""
        sample_lookml = {'views': [{'name': 'orders'}]}
        sample_cube_def = {'cubes': [{'name': 'orders'}]}
        yaml_output = "cubes:\n- name: orders\n"
        
        mock_file_loader.return_value = sample_lookml
        mock_parse_view.return_value = sample_cube_def
        mock_generate_joins.return_value = sample_cube_def
        mock_yaml_dump.return_value = yaml_output
        
        converter = LookMLConverter(printonly=True)
        result = converter.cubes("test.lkml")
        
        assert 'lookml_model' in result
        assert 'cube_def' in result
        assert 'yaml_output' in result
        assert result['yaml_output'] == yaml_output
        mock_console.print.assert_called_once_with(yaml_output)

    @patch('lkml2cube.converter.print_summary')
    @patch('lkml2cube.converter.write_files')
    @patch('lkml2cube.converter.generate_cube_joins')
    @patch('lkml2cube.converter.parse_view')
    @patch('lkml2cube.converter.file_loader')
    def test_cubes_write_files(self, mock_file_loader, mock_parse_view,
                              mock_generate_joins, mock_write_files, mock_print_summary):
        """Test cubes method with file writing."""
        sample_lookml = {'views': [{'name': 'orders'}]}
        sample_cube_def = {'cubes': [{'name': 'orders'}]}
        sample_summary = {'cubes': [{'name': 'orders', 'path': '/tmp/orders.yml'}]}
        
        mock_file_loader.return_value = sample_lookml
        mock_parse_view.return_value = sample_cube_def
        mock_generate_joins.return_value = sample_cube_def
        mock_write_files.return_value = sample_summary
        
        converter = LookMLConverter(outputdir="/tmp")
        result = converter.cubes("test.lkml")
        
        assert 'lookml_model' in result
        assert 'cube_def' in result
        assert 'summary' in result
        assert result['summary'] == sample_summary
        
        mock_write_files.assert_called_once_with(sample_cube_def, outputdir="/tmp")
        mock_print_summary.assert_called_once_with(sample_summary)


class TestLookMLConverterViews:
    """Test the views() method."""

    @patch('lkml2cube.converter.file_loader')
    def test_views_file_not_found(self, mock_file_loader):
        """Test views method when file is not found."""
        mock_file_loader.return_value = None
        converter = LookMLConverter()
        
        with pytest.raises(ValueError, match="No files were found on path"):
            converter.views("nonexistent.lkml")

    @patch('lkml2cube.converter.file_loader')
    def test_views_parseonly(self, mock_file_loader):
        """Test views method with parseonly=True."""
        sample_lookml = {
            'views': [{'name': 'orders'}],
            'explores': [{'name': 'orders_explore'}]
        }
        mock_file_loader.return_value = sample_lookml
        
        converter = LookMLConverter(parseonly=True)
        result = converter.views("test.lkml")
        
        assert 'lookml_model' in result
        assert 'parsed_model' in result
        assert result['lookml_model'] == sample_lookml

    @patch('lkml2cube.converter.console')
    @patch('lkml2cube.converter.yaml.dump')
    @patch('lkml2cube.converter.parse_explores')
    @patch('lkml2cube.converter.file_loader')
    def test_views_printonly(self, mock_file_loader, mock_parse_explores, 
                            mock_yaml_dump, mock_console):
        """Test views method with printonly=True."""
        sample_lookml = {'views': [{'name': 'orders'}], 'explores': []}
        sample_cube_def = {'cubes': [{'name': 'orders'}], 'views': []}
        yaml_output = "cubes:\n- name: orders\nviews: []\n"
        
        mock_file_loader.return_value = sample_lookml
        mock_parse_explores.return_value = sample_cube_def
        mock_yaml_dump.return_value = yaml_output
        
        converter = LookMLConverter(printonly=True, use_explores_name=True)
        result = converter.views("test.lkml")
        
        assert 'yaml_output' in result
        assert result['yaml_output'] == yaml_output
        mock_parse_explores.assert_called_once_with(sample_lookml, True)
        mock_console.print.assert_called_once_with(yaml_output)

    @patch('lkml2cube.converter.print_summary')
    @patch('lkml2cube.converter.write_files')
    @patch('lkml2cube.converter.parse_explores')
    @patch('lkml2cube.converter.file_loader')
    def test_views_write_files(self, mock_file_loader, mock_parse_explores,
                              mock_write_files, mock_print_summary):
        """Test views method with file writing."""
        sample_lookml = {'views': [{'name': 'orders'}], 'explores': []}
        sample_cube_def = {'cubes': [{'name': 'orders'}], 'views': []}
        sample_summary = {'cubes': [{'name': 'orders', 'path': '/tmp/orders.yml'}], 'views': []}
        
        mock_file_loader.return_value = sample_lookml
        mock_parse_explores.return_value = sample_cube_def
        mock_write_files.return_value = sample_summary
        
        converter = LookMLConverter(outputdir="/tmp", use_explores_name=False)
        result = converter.views("test.lkml")
        
        assert 'summary' in result
        assert result['summary'] == sample_summary
        
        mock_parse_explores.assert_called_once_with(sample_lookml, False)
        mock_write_files.assert_called_once_with(sample_cube_def, outputdir="/tmp")


class TestLookMLConverterExplores:
    """Test the explores() method."""

    @patch('lkml2cube.converter.meta_loader')
    def test_explores_no_response(self, mock_meta_loader):
        """Test explores method when no response is received."""
        mock_meta_loader.return_value = None
        converter = LookMLConverter()
        
        with pytest.raises(ValueError, match="No response received from"):
            converter.explores("http://test.com/meta", "token")

    @patch('lkml2cube.converter.meta_loader')
    def test_explores_parseonly(self, mock_meta_loader):
        """Test explores method with parseonly=True."""
        sample_cube_model = {
            'cubes': [{'name': 'orders', 'sql_table': 'orders'}]
        }
        mock_meta_loader.return_value = sample_cube_model
        
        converter = LookMLConverter(parseonly=True)
        result = converter.explores("http://test.com/meta", "token")
        
        assert 'cube_model' in result
        assert 'parsed_model' in result
        assert result['cube_model'] == sample_cube_model

    @patch('lkml2cube.converter.console')
    @patch('lkml2cube.converter.yaml.dump')
    @patch('lkml2cube.converter.parse_meta')
    @patch('lkml2cube.converter.meta_loader')
    def test_explores_printonly(self, mock_meta_loader, mock_parse_meta,
                               mock_yaml_dump, mock_console):
        """Test explores method with printonly=True."""
        sample_cube_model = {'cubes': [{'name': 'orders'}]}
        sample_lookml_model = {'views': [{'name': 'orders'}], 'explores': []}
        yaml_output = "views:\n- name: orders\nexplores: []\n"
        
        mock_meta_loader.return_value = sample_cube_model
        mock_parse_meta.return_value = sample_lookml_model
        mock_yaml_dump.return_value = yaml_output
        
        converter = LookMLConverter(printonly=True)
        result = converter.explores("http://test.com/meta", "token")
        
        assert 'lookml_model' in result
        assert 'yaml_output' in result
        assert result['yaml_output'] == yaml_output
        mock_console.print.assert_called_once_with(yaml_output)

    @patch('lkml2cube.converter.print_summary')
    @patch('lkml2cube.converter.write_lookml_files')
    @patch('lkml2cube.converter.parse_meta')
    @patch('lkml2cube.converter.meta_loader')
    def test_explores_write_files(self, mock_meta_loader, mock_parse_meta,
                                 mock_write_lookml_files, mock_print_summary):
        """Test explores method with file writing."""
        sample_cube_model = {'cubes': [{'name': 'orders'}]}
        sample_lookml_model = {'views': [{'name': 'orders'}], 'explores': []}
        sample_summary = {'views': [{'name': 'orders', 'path': '/tmp/orders.lkml'}], 'explores': []}
        
        mock_meta_loader.return_value = sample_cube_model
        mock_parse_meta.return_value = sample_lookml_model
        mock_write_lookml_files.return_value = sample_summary
        
        converter = LookMLConverter(outputdir="/tmp")
        result = converter.explores("http://test.com/meta", "token")
        
        assert 'lookml_model' in result
        assert 'summary' in result
        assert result['summary'] == sample_summary
        
        mock_write_lookml_files.assert_called_once_with(sample_lookml_model, outputdir="/tmp")
        mock_print_summary.assert_called_once_with(sample_summary)


class TestLookMLConverterUtilities:
    """Test utility methods."""

    @patch('lkml2cube.converter.file_loader')
    def test_validate_files_all_valid(self, mock_file_loader):
        """Test validate_files with all valid files."""
        mock_file_loader.side_effect = [
            {'views': [{'name': 'orders'}]},
            {'views': [{'name': 'customers'}]}
        ]
        
        converter = LookMLConverter()
        result = converter.validate_files(["orders.lkml", "customers.lkml"])
        
        assert result == {"orders.lkml": True, "customers.lkml": True}
        assert mock_file_loader.call_count == 2

    @patch('lkml2cube.converter.file_loader')
    def test_validate_files_mixed_results(self, mock_file_loader):
        """Test validate_files with mixed valid/invalid files."""
        mock_file_loader.side_effect = [
            {'views': [{'name': 'orders'}]},
            None,  # Invalid file
            Exception("Parse error")  # Exception
        ]
        
        converter = LookMLConverter()
        result = converter.validate_files(["orders.lkml", "invalid.lkml", "error.lkml"])
        
        assert result == {
            "orders.lkml": True,
            "invalid.lkml": False,
            "error.lkml": False
        }

    @patch('lkml2cube.converter.file_loader')
    def test_validate_files_empty_list(self, mock_file_loader):
        """Test validate_files with empty file list."""
        converter = LookMLConverter()
        result = converter.validate_files([])
        
        assert result == {}
        mock_file_loader.assert_not_called()


class TestLookMLConverterIntegration:
    """Integration tests using real sample files."""

    def setup_method(self):
        """Set up test fixtures."""
        self.samples_dir = join(dirname(__file__), "samples")
        # Clear the global visited_path cache to prevent interference between tests
        from lkml2cube.parser import loader
        loader.visited_path.clear()

    def test_cubes_integration_with_sample_files(self):
        """Test cubes method with actual sample files."""
        converter = LookMLConverter(parseonly=True, rootdir=self.samples_dir)
        
        # Use the sample orders view file (full path as expected by file_loader)
        file_path = join(self.samples_dir, "lkml/views/orders.view.lkml")
        result = converter.cubes(file_path)
        
        assert 'lookml_model' in result
        assert 'parsed_model' in result
        assert result['lookml_model'] is not None
        assert 'views' in result['lookml_model']
        assert len(result['lookml_model']['views']) > 0

    def test_views_integration_with_sample_files(self):
        """Test views method with actual sample files."""
        converter = LookMLConverter(parseonly=True, rootdir=self.samples_dir)
        
        # Use the sample explores file (full path as expected by file_loader)
        file_path = join(self.samples_dir, "lkml/explores/orders_summary.model.lkml")
        result = converter.views(file_path)
        
        assert 'lookml_model' in result
        assert 'parsed_model' in result
        assert result['lookml_model'] is not None

    def test_validate_files_with_sample_files(self):
        """Test validate_files with actual sample files."""
        converter = LookMLConverter(rootdir=self.samples_dir)
        
        # Use full paths as expected by file_loader
        file_paths = [
            join(self.samples_dir, "lkml/views/orders.view.lkml"),
            join(self.samples_dir, "lkml/views/nonexistent.view.lkml")
        ]
        
        result = converter.validate_files(file_paths)
        
        # First file should be valid, second should be invalid
        assert len(result) == 2
        assert result[file_paths[0]] == True
        assert result[file_paths[1]] == False


class TestLookMLConverterErrorHandling:
    """Test error handling and edge cases."""

    def test_cubes_with_invalid_file_path(self):
        """Test cubes method with invalid file path."""
        converter = LookMLConverter()
        
        with pytest.raises(ValueError, match="No files were found on path"):
            converter.cubes("nonexistent_file.lkml")

    def test_views_with_invalid_file_path(self):
        """Test views method with invalid file path."""
        converter = LookMLConverter()
        
        with pytest.raises(ValueError, match="No files were found on path"):
            converter.views("nonexistent_file.lkml")

    def test_explores_with_invalid_url(self):
        """Test explores method with invalid URL."""
        converter = LookMLConverter()
        
        with pytest.raises(ValueError, match="A valid token must be provided"):
            converter.explores("http://invalid.com/meta", "")

    @patch('lkml2cube.converter.meta_loader')
    def test_explores_with_api_error(self, mock_meta_loader):
        """Test explores method with API error."""
        mock_meta_loader.side_effect = Exception("API Error")
        converter = LookMLConverter()
        
        with pytest.raises(Exception, match="API Error"):
            converter.explores("http://test.com/meta", "token")

    @patch('lkml2cube.converter.file_loader')
    def test_cubes_with_parse_error(self, mock_file_loader):
        """Test cubes method with parsing error."""
        mock_file_loader.side_effect = Exception("Parse error")
        converter = LookMLConverter()
        
        with pytest.raises(Exception, match="Parse error"):
            converter.cubes("test.lkml")

    def test_set_config_with_invalid_types(self):
        """Test set_config with various parameter types."""
        converter = LookMLConverter()
        
        # These should work without error
        converter.set_config(outputdir="string")
        converter.set_config(parseonly=True)
        converter.set_config(parseonly=False)
        converter.set_config(rootdir=None)
        
        # Verify the values were set correctly
        assert converter.outputdir == "string"
        assert converter.parseonly is False
        assert converter.rootdir is None


class TestLookMLConverterYAMLConfiguration:
    """Test YAML configuration setup."""

    def test_yaml_representers_configured(self):
        """Test that YAML representers are properly configured."""
        from lkml2cube.parser.types import folded_unicode, literal_unicode
        
        # Creating a converter should configure YAML representers
        converter = LookMLConverter()
        
        # Test that the representers work
        folded_text = folded_unicode("This is folded text")
        literal_text = literal_unicode("This is literal text")
        
        # These should not raise errors
        yaml_output = yaml.dump({"folded": folded_text, "literal": literal_text})
        assert isinstance(yaml_output, str)

    def test_multiple_converter_instances(self):
        """Test that multiple converter instances work correctly."""
        converter1 = LookMLConverter(outputdir="/tmp1")
        converter2 = LookMLConverter(outputdir="/tmp2")
        
        assert converter1.outputdir == "/tmp1"
        assert converter2.outputdir == "/tmp2"
        
        # Configuration should be independent
        converter1.set_config(parseonly=True)
        assert converter1.parseonly is True
        assert converter2.parseonly is False