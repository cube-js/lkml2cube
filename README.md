# lkml2cube

A comprehensive tool for bidirectional conversion between LookML and Cube data models.

## Features

- **LookML → Cube**: Convert LookML views and explores to Cube model definitions
- **Cube → LookML**: Generate production-ready LookML from Cube meta API
- **Smart Detection**: Automatically distinguishes between Cube cubes (→ LookML views) and Cube views (→ LookML explores)
- **Production Ready**: Generates LookML with includes, proper joins, primary keys, and drill fields
- **Rich Output**: Beautiful console tables showing generated files

## Installation

```sh
pip install lkml2cube
```

## Usage

lkml2cube can be used both as a command-line tool and as a Python library:

### Command Line Interface

Use the CLI commands for quick conversions and automation:

#### Commands

lkml2cube provides three main commands for different conversion scenarios:

##### 1. `cubes` - LookML Views → Cube Models

Converts LookML view files into Cube YAML definitions (cubes only).

```sh
# Convert a single LookML view
lkml2cube cubes path/to/orders.view.lkml --outputdir examples/

# Parse and inspect LookML structure
lkml2cube cubes --parseonly path/to/orders.view.lkml

# Convert with custom root directory for includes
lkml2cube cubes views/orders.view.lkml --outputdir models/ --rootdir ../my_project/
```

##### 2. `views` - LookML Explores → Cube Models  

Converts LookML explore files into Cube YAML definitions (cubes + views with joins).

```sh
# Convert LookML explores with join relationships
lkml2cube views path/to/sales_analysis.explore.lkml --outputdir examples/

# Print YAML output to console
lkml2cube views --printonly path/to/sales_analysis.explore.lkml
```

##### 3. `explores` - Cube Meta API → LookML ✨ **NEW**

Generates production-ready LookML files from Cube's meta API endpoint.

```sh
# Generate LookML from Cube deployment
lkml2cube explores "https://your-cube.com/cubejs-api/v1/meta" \
  --token "your-jwt-token" \
  --outputdir looker_models/

# Preview the parsed Cube model
lkml2cube explores "https://your-cube.com/cubejs-api/v1/meta" \
  --token "your-jwt-token" \
  --parseonly

# Print generated LookML to console
lkml2cube explores "https://your-cube.com/cubejs-api/v1/meta" \
  --token "your-jwt-token" \
  --printonly
```

### Python API

For programmatic usage, import and use the `LookMLConverter` class:

```python
from lkml2cube.converter import LookMLConverter

# Initialize converter with options
converter = LookMLConverter(
    outputdir="./output",
    rootdir="./models",
    parseonly=False,
    printonly=False,
    use_explores_name=False
)

# Convert LookML views to Cube definitions
result = converter.cubes("path/to/orders.view.lkml")
print(f"Generated {len(result['summary']['cubes'])} cube files")

# Convert LookML explores to Cube definitions with views
result = converter.views("path/to/explores.lkml")
print(f"Generated {len(result['summary']['views'])} view files")

# Generate LookML from Cube API
result = converter.explores("https://api.cube.dev/v1/meta", "jwt-token")
print(f"Generated {len(result['summary']['views'])} LookML views")
```

#### Configuration Management

The converter maintains state and can be reconfigured:

```python
# Update configuration
converter.set_config(parseonly=True, outputdir="/tmp/new-output")

# Get current configuration
config = converter.get_config()
print(f"Current output directory: {config['outputdir']}")

# Validate files before processing
file_paths = ["model1.lkml", "model2.lkml"]
validation_results = converter.validate_files(file_paths)
valid_files = [f for f, valid in validation_results.items() if valid]
```

#### Return Values

All conversion methods return a dictionary with:

- **parseonly=True**: `{'lookml_model': dict, 'parsed_model': str}`
- **printonly=True**: `{'lookml_model': dict, 'cube_def': dict, 'yaml_output': str}`
- **Default**: `{'lookml_model': dict, 'cube_def': dict, 'summary': dict}`

The `summary` contains details about generated files:

```python
{
  'cubes': [{'name': 'orders', 'path': '/output/cubes/orders.yml'}],
  'views': [{'name': 'orders_view', 'path': '/output/views/orders_view.yml'}]
}
```

#### Why Use the Python API?

- **State Management**: Maintain configuration across multiple conversions
- **Programmatic Control**: Integrate conversions into data pipelines
- **Validation**: Check file validity before processing
- **Error Handling**: Catch and handle conversion errors gracefully
- **Batch Processing**: Process multiple files efficiently
- **Custom Workflows**: Build complex conversion workflows

## What Gets Generated

### From Cube Cubes → LookML Views

```yaml
# Cube cube definition
cubes:
  - name: orders
    sql_table: public.orders
    dimensions:
      - name: id
        type: number
        sql: "{TABLE}.id"
```

**Generates:**

```lookml
view orders {
  label: "Orders"
  sql_table_name: public.orders ;;
  
  dimension: id {
    label: "Order ID"
    type: number
    primary_key: yes
    sql: ${TABLE}.id ;;
  }
  
  measure: count {
    type: count
    drill_fields: [id, name]
  }
}
```

### From Cube Views → LookML Explores

```yaml
# Cube view with joins
views:
  - name: order_analysis
    cubes:
      - join_path: orders
      - join_path: customers
```

**Generates:**

```lookml
include: "/views/orders.view.lkml"
include: "/views/customers.view.lkml"

explore order_analysis {
  label: "Order Analysis"
  view_name: orders
  
  join: customers {
    view_label: "Customers"
    type: left_outer
    relationship: many_to_one
    sql_on: ${orders.customer_id} = ${customers.id} ;;
  }
}
```

## Advanced Usage

### Working with Includes

The tool automatically handles LookML `include` statements and can resolve relative paths:

**CLI:**
```sh
# Use --rootdir to resolve include paths
lkml2cube views explores/sales.explore.lkml \
  --outputdir output/ \
  --rootdir /path/to/lookml/project/
```

**Python API:**
```python
# Set rootdir for include resolution
converter = LookMLConverter(
    rootdir="/path/to/lookml/project/",
    outputdir="output/"
)
result = converter.views("explores/sales.explore.lkml")
```

### Authentication for Cube API

The `explores` command requires a valid JWT token for Cube authentication:

**CLI:**
```sh
# Get your token from Cube's authentication
export CUBE_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

lkml2cube explores "https://your-cube.com/cubejs-api/v1/meta" \
  --token "$CUBE_TOKEN" \
  --outputdir looker_models/
```

**Python API:**
```python
# Use environment variables or pass token directly
import os
converter = LookMLConverter(outputdir="looker_models/")
result = converter.explores(
    "https://your-cube.com/cubejs-api/v1/meta",
    os.getenv("CUBE_TOKEN")
)
```

### Batch Processing

The Python API makes it easy to process multiple files:

```python
from lkml2cube.converter import LookMLConverter
from pathlib import Path

converter = LookMLConverter(outputdir="output/")

# Process all LookML files in a directory
lookml_dir = Path("models/")
for lkml_file in lookml_dir.glob("*.lkml"):
    try:
        print(f"Processing {lkml_file}...")
        result = converter.cubes(str(lkml_file))
        print(f"  ✓ Generated {len(result['summary']['cubes'])} cubes")
    except Exception as e:
        print(f"  ✗ Error processing {lkml_file}: {e}")

# Validate files before processing
file_paths = [str(f) for f in lookml_dir.glob("*.lkml")]
validation_results = converter.validate_files(file_paths)
valid_files = [f for f, valid in validation_results.items() if valid]
print(f"Found {len(valid_files)} valid LookML files")
```

### Pipeline Integration

Integrate lkml2cube into your data pipeline:

```python
from lkml2cube.converter import LookMLConverter
import logging

def sync_cube_to_lookml(cube_api_url: str, token: str, output_dir: str):
    """Sync Cube models to LookML files."""
    converter = LookMLConverter(outputdir=output_dir)
    
    try:
        # Generate LookML from Cube API
        result = converter.explores(cube_api_url, token)
        
        # Log results
        views_count = len(result['summary']['views'])
        explores_count = len(result['summary']['explores'])
        
        logging.info(f"Generated {views_count} LookML views")
        logging.info(f"Generated {explores_count} LookML explores")
        
        return result['summary']
        
    except Exception as e:
        logging.error(f"Failed to sync Cube to LookML: {e}")
        raise

# Use in your pipeline
if __name__ == "__main__":
    summary = sync_cube_to_lookml(
        "https://your-cube.com/cubejs-api/v1/meta",
        "your-jwt-token",
        "looker_models/"
    )
    print(f"Sync complete: {summary}")
```

## Output Structure

The tool creates organized directory structures:

```
outputdir/
├── views/           # LookML views or Cube cubes → LookML views  
│   ├── orders.view.lkml
│   └── customers.view.lkml
└── explores/        # Cube views → LookML explores
    └── sales_analysis.explore.lkml
```

## Key Features

- **Smart Detection**: Automatically identifies Cube cubes vs views based on `aliasMember` usage
- **Include Generation**: Explores automatically include referenced view files
- **Primary Key Detection**: Auto-detects ID fields and marks them as primary keys
- **Rich Metadata**: Preserves labels, descriptions, and data types
- **Join Relationships**: Generates proper LookML join syntax with relationships
- **Production Ready**: Follows LookML best practices and conventions

