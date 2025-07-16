# scripts/generate_docs.py
import os
import subprocess
import yaml
import sys
import importlib
import inspect
import pkgutil


def generate_module_docs():
    """Generate Markdown documentation for all Python modules."""

    # Ensure docs directory exists
    os.makedirs("docs", exist_ok=True)
    
    # Add current directory to Python path
    current_dir = os.path.abspath(".")
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # Try both pydoc-markdown and fallback to manual generation
    modules = ["lkml2cube.parser", "lkml2cube.converter", "lkml2cube.main"]
    
    for module in modules:
        output_file = f"docs/{module.replace('.', '_')}.md"
        print(f"Generating documentation for {module}...")
        
        # First try pydoc-markdown
        if try_pydoc_markdown(module, output_file):
            print(f"  ✓ Created {output_file} using pydoc-markdown")
            continue
        
        # Fallback to manual generation
        try:
            generate_manual_docs(module, output_file)
            print(f"  ✓ Created {output_file} using manual generation")
        except Exception as e:
            print(f"  ✗ Error generating docs for {module}: {e}")


def try_pydoc_markdown(module, output_file):
    """Try to generate documentation using pydoc-markdown."""
    try:
        # Create a temporary config file for this module
        config = {
            "loaders": [
                {
                    "type": "python",
                    "search_path": ["."],
                    "modules": [module]
                }
            ],
            "renderer": {
                "type": "markdown",
                "render_toc": True,
                "render_module_header": True,
                "markdown": {
                    "filename": output_file
                }
            }
        }
        
        config_file = f".pydoc-markdown-{module.replace('.', '_')}.yml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        # Run pydoc-markdown with the config file
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.abspath(".") + ":" + env.get("PYTHONPATH", "")
        
        result = subprocess.run(
            ["pydoc-markdown", config_file], 
            capture_output=True, 
            text=True,
            env=env
        )
        
        # Clean up temporary config file
        if os.path.exists(config_file):
            os.remove(config_file)
        
        if result.returncode == 0 and os.path.exists(output_file):
            optimize_for_llm(output_file)
            return True
        else:
            return False
    except Exception:
        return False


def generate_manual_docs(module_name, output_file):
    """Generate documentation manually using Python introspection."""
    try:
        # Import the module
        module = importlib.import_module(module_name)
        
        # Start building the documentation
        lines = []
        lines.append(f"# {module_name}")
        lines.append("")
        
        # Add module docstring if available
        if module.__doc__:
            lines.append(module.__doc__.strip())
            lines.append("")
        
        # Handle different module types
        if hasattr(module, "__path__"):  # It's a package
            # Get all submodules
            submodules = []
            for importer, modname, ispkg in pkgutil.iter_modules(module.__path__, module_name + "."):
                try:
                    submodule = importlib.import_module(modname)
                    submodules.append((modname, submodule))
                except ImportError:
                    continue
            
            if submodules:
                lines.append("## Submodules")
                lines.append("")
                for modname, submodule in submodules:
                    lines.append(f"### {modname}")
                    if submodule.__doc__:
                        lines.append(submodule.__doc__.strip())
                    lines.append("")
                    
                    # Add classes and functions from submodule
                    add_module_content(submodule, lines)
                    lines.append("")
        else:
            # It's a regular module
            add_module_content(module, lines)
        
        # Write to file
        with open(output_file, "w") as f:
            f.write("\n".join(lines))
        
        # Optimize for LLM consumption
        optimize_for_llm(output_file)
        
    except Exception as e:
        raise Exception(f"Failed to generate manual docs for {module_name}: {e}")


def add_module_content(module, lines):
    """Add classes and functions from a module to the documentation."""
    # Get all classes
    classes = []
    functions = []
    
    for name, obj in inspect.getmembers(module):
        if name.startswith("_"):
            continue
        if inspect.isclass(obj) and obj.__module__ == module.__name__:
            classes.append((name, obj))
        elif inspect.isfunction(obj) and obj.__module__ == module.__name__:
            functions.append((name, obj))
    
    # Document classes
    if classes:
        lines.append("#### Classes")
        lines.append("")
        for name, cls in classes:
            lines.append(f"##### {name}")
            if cls.__doc__:
                lines.append(cls.__doc__.strip())
            lines.append("")
            
            # Add methods
            methods = []
            for method_name, method in inspect.getmembers(cls):
                if (method_name.startswith("_") and method_name != "__init__") or not inspect.isfunction(method):
                    continue
                methods.append((method_name, method))
            
            if methods:
                lines.append("**Methods:**")
                lines.append("")
                for method_name, method in methods:
                    lines.append(f"- `{method_name}()`: {method.__doc__.strip().split('.')[0] if method.__doc__ else 'No description'}")
                lines.append("")
    
    # Document functions
    if functions:
        lines.append("#### Functions")
        lines.append("")
        for name, func in functions:
            lines.append(f"##### {name}()")
            if func.__doc__:
                lines.append(func.__doc__.strip())
            lines.append("")


def optimize_for_llm(filepath):
    """Compress documentation for optimal LLM consumption."""
    with open(filepath, "r") as f:
        content = f.read()

    # Remove redundant phrases
    optimizations = [
        ("This function ", ""),
        ("This method ", ""),
        ("is used to ", ""),
        ("is responsible for ", ""),
        ("The purpose of this ", ""),
    ]

    for old, new in optimizations:
        content = content.replace(old, new)

    with open(filepath, "w") as f:
        f.write(content)


if __name__ == "__main__":
    generate_module_docs()
