"""
Tests for LookML constants parsing and substitution.

This module tests the constant parsing functionality, including:
- Parsing constants from LookML files
- Substituting constants in strings using @{constant_name} syntax
- Handling constants in views, explores, and their properties
"""

import pytest
import os
from lkml2cube.parser.loader import file_loader, substitute_constants


class TestConstantParsing:
    """Test constant parsing and substitution functionality."""

    def test_constant_substitution_simple(self):
        """Test basic constant substitution in strings."""
        constants = {'city': 'Tokyo', 'country': 'Japan'}
        
        # Test simple string substitution
        result = substitute_constants("@{city} Users", constants)
        assert result == "Tokyo Users"
        
        # Test multiple constants in one string
        result = substitute_constants("Users from @{city}, @{country}", constants)
        assert result == "Users from Tokyo, Japan"

    def test_constant_substitution_in_dict(self):
        """Test constant substitution in dictionary structures."""
        constants = {'city': 'Okayama'}
        
        obj = {
            'label': '@{city} Users',
            'description': 'Users from @{city}',
            'nested': {
                'field': '@{city} data'
            }
        }
        
        result = substitute_constants(obj, constants)
        
        assert result['label'] == 'Okayama Users'
        assert result['description'] == 'Users from Okayama'
        assert result['nested']['field'] == 'Okayama data'

    def test_constant_substitution_in_list(self):
        """Test constant substitution in list structures."""
        constants = {'city': 'Tokyo'}
        
        obj = ['@{city} Users', '@{city} Orders', 'Static string']
        
        result = substitute_constants(obj, constants)
        
        assert result[0] == 'Tokyo Users'
        assert result[1] == 'Tokyo Orders'
        assert result[2] == 'Static string'

    def test_constant_not_found(self):
        """Test behavior when constant is not found."""
        constants = {'city': 'Tokyo'}
        
        # Should leave unknown constants unchanged
        result = substitute_constants("@{city} Users from @{unknown}", constants)
        assert result == "Tokyo Users from @{unknown}"

    def test_constants_in_lookml_file(self):
        """Test loading and parsing constants from a LookML file."""
        file_path = os.path.join(os.path.dirname(__file__), "samples", "lkml", "constants_test.lkml")
        
        # Reset visited_path to ensure clean state
        from lkml2cube.parser.loader import visited_path
        visited_path.clear()
        
        # Load the model
        model = file_loader(file_path, None)
        
        # Check that constants were parsed
        assert "constants" in model
        constants_dict = {c["name"]: c["value"] for c in model["constants"]}
        assert "city" in constants_dict
        assert "country" in constants_dict
        assert constants_dict["city"] == "Okayama"
        assert constants_dict["country"] == "Japan"

    def test_constant_substitution_in_loaded_model(self):
        """Test that constants are substituted in loaded LookML model."""
        file_path = os.path.join(os.path.dirname(__file__), "samples", "lkml", "constants_test.lkml")
        
        # Reset visited_path to ensure clean state
        from lkml2cube.parser.loader import visited_path
        visited_path.clear()
        
        # Load the model
        model = file_loader(file_path, None)
        
        # Check that model was loaded
        assert model is not None
        
        # Check that constants were substituted in explores
        explores = model.get("explores", [])
        assert len(explores) > 0
        
        users_explore = next((e for e in explores if e["name"] == "users"), None)
        assert users_explore is not None
        assert users_explore["label"] == "Okayama Users"
        assert users_explore["description"] == "Users from Okayama, Japan"

    def test_constant_substitution_in_views(self):
        """Test that constants are substituted in view definitions."""
        file_path = os.path.join(os.path.dirname(__file__), "samples", "lkml", "constants_test.lkml")
        
        # Reset visited_path to ensure clean state
        from lkml2cube.parser.loader import visited_path
        visited_path.clear()
        
        # Load the model
        model = file_loader(file_path, None)
        
        # Check that model was loaded
        assert model is not None
        
        # Check that constants were substituted in views
        views = model.get("views", [])
        assert len(views) > 0
        
        users_view = next((v for v in views if v["name"] == "users"), None)
        assert users_view is not None
        assert users_view["label"] == "Okayama Users Data"
        
        # Check dimension labels
        dimensions = users_view.get("dimensions", [])
        name_dimension = next((d for d in dimensions if d["name"] == "name"), None)
        assert name_dimension is not None
        assert name_dimension["label"] == "User Name in Okayama"
        
        # Check measure labels
        measures = users_view.get("measures", [])
        count_measure = next((m for m in measures if m["name"] == "count"), None)
        assert count_measure is not None
        assert count_measure["label"] == "Count of Okayama Users"