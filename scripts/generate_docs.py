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
    modules = [
        "lkml2cube.parser.cube_api",
        "lkml2cube.parser.explores",
        "lkml2cube.parser.loader",
        "lkml2cube.parser.types",
        "lkml2cube.parser.views",
        "lkml2cube.converter",
        "lkml2cube.main",
    ]

    for module in modules:
        output_file = f"docs/{module.replace('.', '_')}.md"
        print(f"Generating documentation for {module}...")

        # First try pydoc-markdown
        if try_pydoc_markdown(module, output_file):
            print(f"  ✓ Created {output_file} using pydoc-markdown")
        else:
            print(f"  ✗ Error generating docs for {module}")


def try_pydoc_markdown(module, output_file):
    """Try to generate documentation using pydoc-markdown."""
    try:
        # Create a temporary config file for this module
        config = {
            "loaders": [{"type": "python", "search_path": ["."], "modules": [module]}],
            "renderer": {
                "type": "markdown",
                "render_toc": True,
                "render_module_header": True,
                "filename": output_file,
            },
        }

        config_file = f".pydoc-markdown-{module.replace('.', '_')}.yml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)

        # Run pydoc-markdown with the config file
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.abspath(".") + ":" + env.get("PYTHONPATH", "")

        result = subprocess.run(
            ["pydoc-markdown", config_file], capture_output=True, text=True, env=env
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
