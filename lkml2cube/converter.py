"""
Main converter class for lkml2cube providing a Python API for LookML to Cube conversion.

This module provides a high-level interface for converting LookML models to Cube definitions
without requiring CLI usage. It maintains configuration state and provides the same
functionality as the CLI commands.
"""

import pprint
import yaml
from typing import Optional, Dict, Any, List

from lkml2cube.parser.cube_api import meta_loader, parse_meta
from lkml2cube.parser.explores import parse_explores, generate_cube_joins
from lkml2cube.parser.loader import file_loader, write_files, write_lookml_files, print_summary
from lkml2cube.parser.views import parse_view
from lkml2cube.parser.types import (
    folded_unicode,
    literal_unicode,
    folded_unicode_representer,
    literal_unicode_representer,
    console,
)


class LookMLConverter:
    """Main converter class for LookML to Cube conversion operations.
    
    This class provides a Python API for converting LookML models to Cube definitions,
    maintaining configuration state and providing the same functionality as the CLI commands.
    
    Attributes:
        outputdir (str): Directory where output files will be written.
        rootdir (str | None): Root directory for resolving LookML includes.
        parseonly (bool): If True, only parse and return Python dict representation.
        printonly (bool): If True, print YAML output to stdout instead of writing files.
        use_explores_name (bool): Whether to use explore names for cube view names.
    """

    def __init__(
        self,
        outputdir: str = ".",
        rootdir: Optional[str] = None,
        parseonly: bool = False,
        printonly: bool = False,
        use_explores_name: bool = False,
    ):
        """Initialize the LookML converter with configuration options.
        
        Args:
            outputdir (str, optional): Directory where output files will be written. Defaults to ".".
            rootdir (str | None, optional): Root directory for resolving LookML includes. Defaults to None.
            parseonly (bool, optional): If True, only parse and return Python dict representation. Defaults to False.
            printonly (bool, optional): If True, print YAML output to stdout instead of writing files. Defaults to False.
            use_explores_name (bool, optional): Whether to use explore names for cube view names. Defaults to False.
        
        Example:
            >>> converter = LookMLConverter(outputdir="/tmp/output", rootdir="/lookml/models")
            >>> result = converter.cubes("models/*.lkml")
            >>> print(result['summary']['cubes'][0]['name'])
            'orders'
        """
        self.outputdir = outputdir
        self.rootdir = rootdir
        self.parseonly = parseonly
        self.printonly = printonly
        self.use_explores_name = use_explores_name
        
        # Configure YAML representers for proper formatting
        yaml.add_representer(folded_unicode, folded_unicode_representer)
        yaml.add_representer(literal_unicode, literal_unicode_representer)

    def cubes(self, file_path: str) -> Dict[str, Any]:
        """Generate cube definitions from LookML views.
        
        Converts LookML views into Cube cube definitions, handling dimensions, measures,
        and basic join relationships.
        
        Args:
            file_path (str): Path to LookML file(s) to process (supports glob patterns).
        
        Returns:
            dict: Result dictionary containing:
                - 'lookml_model': Parsed LookML model (if parseonly=True)
                - 'cube_def': Generated cube definitions
                - 'yaml_output': YAML string representation (if printonly=True)
                - 'summary': File generation summary (if files written)
        
        Raises:
            ValueError: If no files are found at the specified path.
        
        Example:
            >>> converter = LookMLConverter()
            >>> result = converter.cubes("models/orders.lkml")
            >>> print(result['cube_def']['cubes'][0]['name'])
            'orders'
        """
        lookml_model = file_loader(file_path, self.rootdir)
        
        if lookml_model is None:
            raise ValueError(f"No files were found on path: {file_path}")
        
        result = {'lookml_model': lookml_model}
        
        if self.parseonly:
            result['parsed_model'] = pprint.pformat(lookml_model)
            return result
        
        cube_def = parse_view(lookml_model)
        cube_def = generate_cube_joins(cube_def, lookml_model)
        result['cube_def'] = cube_def
        
        if self.printonly:
            yaml_output = yaml.dump(cube_def, allow_unicode=True)
            result['yaml_output'] = yaml_output
            console.print(yaml_output)
            return result
        
        summary = write_files(cube_def, outputdir=self.outputdir)
        result['summary'] = summary
        print_summary(summary)
        
        return result

    def views(self, file_path: str) -> Dict[str, Any]:
        """Generate cube definitions with views from LookML explores.
        
        Converts LookML explores into Cube definitions including both cubes and views
        with join relationships.
        
        Args:
            file_path (str): Path to LookML file(s) to process (supports glob patterns).
        
        Returns:
            dict: Result dictionary containing:
                - 'lookml_model': Parsed LookML model (if parseonly=True)
                - 'cube_def': Generated cube definitions with views
                - 'yaml_output': YAML string representation (if printonly=True)
                - 'summary': File generation summary (if files written)
        
        Raises:
            ValueError: If no files are found at the specified path.
        
        Example:
            >>> converter = LookMLConverter(use_explores_name=True)
            >>> result = converter.views("models/explores.lkml")
            >>> print(len(result['cube_def']['views']))
            2
        """
        lookml_model = file_loader(file_path, self.rootdir)
        
        if lookml_model is None:
            raise ValueError(f"No files were found on path: {file_path}")
        
        result = {'lookml_model': lookml_model}
        
        if self.parseonly:
            result['parsed_model'] = pprint.pformat(lookml_model)
            return result
        
        cube_def = parse_explores(lookml_model, self.use_explores_name)
        result['cube_def'] = cube_def
        
        if self.printonly:
            yaml_output = yaml.dump(cube_def, allow_unicode=True)
            result['yaml_output'] = yaml_output
            console.print(yaml_output)
            return result
        
        summary = write_files(cube_def, outputdir=self.outputdir)
        result['summary'] = summary
        print_summary(summary)
        
        return result

    def explores(self, metaurl: str, token: str) -> Dict[str, Any]:
        """Generate LookML explores from Cube meta API.
        
        Fetches Cube model from meta API and converts it to LookML explores,
        correctly mapping Cube cubes to LookML views and Cube views to LookML explores.
        
        Args:
            metaurl (str): URL to the Cube meta API endpoint.
            token (str): JWT token for Cube meta API authentication.
        
        Returns:
            dict: Result dictionary containing:
                - 'cube_model': Raw Cube model from meta API (if parseonly=True)
                - 'lookml_model': Converted LookML model
                - 'yaml_output': YAML string representation (if printonly=True)
                - 'summary': File generation summary (if files written)
        
        Raises:
            ValueError: If no response is received from the meta API.
            Exception: If API request fails or token is invalid.
        
        Example:
            >>> converter = LookMLConverter(outputdir="/tmp/lookml")
            >>> result = converter.explores("https://api.cube.dev/v1/meta", "jwt-token")
            >>> print(len(result['lookml_model']['explores']))
            3
        """
        cube_model = meta_loader(meta_url=metaurl, token=token)
        
        if cube_model is None:
            raise ValueError(f"No response received from: {metaurl}")
        
        result = {'cube_model': cube_model}
        
        if self.parseonly:
            result['parsed_model'] = pprint.pformat(cube_model)
            return result
        
        lookml_model = parse_meta(cube_model)
        result['lookml_model'] = lookml_model
        
        if self.printonly:
            yaml_output = yaml.dump(lookml_model, allow_unicode=True)
            result['yaml_output'] = yaml_output
            console.print(yaml_output)
            return result
        
        summary = write_lookml_files(lookml_model, outputdir=self.outputdir)
        result['summary'] = summary
        print_summary(summary)
        
        return result

    def set_config(
        self,
        outputdir: Optional[str] = None,
        rootdir: Optional[str] = None,
        parseonly: Optional[bool] = None,
        printonly: Optional[bool] = None,
        use_explores_name: Optional[bool] = None,
    ) -> None:
        """Update converter configuration options.
        
        Args:
            outputdir (str | None, optional): Directory where output files will be written.
            rootdir (str | None, optional): Root directory for resolving LookML includes.
            parseonly (bool | None, optional): If True, only parse and return Python dict representation.
            printonly (bool | None, optional): If True, print YAML output to stdout instead of writing files.
            use_explores_name (bool | None, optional): Whether to use explore names for cube view names.
        
        Example:
            >>> converter = LookMLConverter()
            >>> converter.set_config(outputdir="/new/path", parseonly=True)
            >>> result = converter.cubes("models/*.lkml")
            # Will now parse only and use the new output directory
        """
        if outputdir is not None:
            self.outputdir = outputdir
        if rootdir is not None:
            self.rootdir = rootdir
        if parseonly is not None:
            self.parseonly = parseonly
        if printonly is not None:
            self.printonly = printonly
        if use_explores_name is not None:
            self.use_explores_name = use_explores_name

    def get_config(self) -> Dict[str, Any]:
        """Get current converter configuration.
        
        Returns:
            dict: Current configuration settings.
        
        Example:
            >>> converter = LookMLConverter(outputdir="/tmp")
            >>> config = converter.get_config()
            >>> print(config['outputdir'])
            '/tmp'
        """
        return {
            'outputdir': self.outputdir,
            'rootdir': self.rootdir,
            'parseonly': self.parseonly,
            'printonly': self.printonly,
            'use_explores_name': self.use_explores_name,
        }

    def validate_files(self, file_paths: List[str]) -> Dict[str, bool]:
        """Validate that LookML files exist and can be loaded.
        
        Args:
            file_paths (list[str]): List of file paths to validate.
        
        Returns:
            dict: Dictionary mapping file paths to validation results.
        
        Example:
            >>> converter = LookMLConverter()
            >>> results = converter.validate_files(["models/orders.lkml", "models/missing.lkml"])
            >>> print(results["models/orders.lkml"])
            True
        """
        results = {}
        for file_path in file_paths:
            try:
                lookml_model = file_loader(file_path, self.rootdir)
                results[file_path] = lookml_model is not None
            except Exception:
                results[file_path] = False
        return results

    def __repr__(self) -> str:
        """Return string representation of the converter."""
        return (
            f"LookMLConverter(outputdir='{self.outputdir}', "
            f"rootdir='{self.rootdir}', parseonly={self.parseonly}, "
            f"printonly={self.printonly}, use_explores_name={self.use_explores_name})"
        )