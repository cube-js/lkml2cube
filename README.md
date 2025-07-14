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

## Commands

lkml2cube provides three main commands for different conversion scenarios:

### 1. `cubes` - LookML Views → Cube Models

Converts LookML view files into Cube YAML definitions (cubes only).

```sh
# Convert a single LookML view
lkml2cube cubes path/to/orders.view.lkml --outputdir examples/

# Parse and inspect LookML structure
lkml2cube cubes --parseonly path/to/orders.view.lkml

# Convert with custom root directory for includes
lkml2cube cubes views/orders.view.lkml --outputdir models/ --rootdir ../my_project/
```

### 2. `views` - LookML Explores → Cube Models  

Converts LookML explore files into Cube YAML definitions (cubes + views with joins).

```sh
# Convert LookML explores with join relationships
lkml2cube views path/to/sales_analysis.explore.lkml --outputdir examples/

# Print YAML output to console
lkml2cube views --printonly path/to/sales_analysis.explore.lkml
```

### 3. `explores` - Cube Meta API → LookML ✨ **NEW**

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

```sh
# Use --rootdir to resolve include paths
lkml2cube views explores/sales.explore.lkml \
  --outputdir output/ \
  --rootdir /path/to/lookml/project/
```

### Authentication for Cube API

The `explores` command requires a valid JWT token for Cube authentication:

```sh
# Get your token from Cube's authentication
export CUBE_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

lkml2cube explores "https://your-cube.com/cubejs-api/v1/meta" \
  --token "$CUBE_TOKEN" \
  --outputdir looker_models/
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

