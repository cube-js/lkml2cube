connection: "my_connection"

include: "/views/*.view.lkml"                # include all views in the views/ folder in this project
# include: "/**/*.view.lkml"                 # include all views in this project
# include: "/**/*.dashboard.lookml"   # include a LookML dashboard called my_dashboard


explore: orders {
  label: "Orders Summary"

  join: line_items {
    relationship: one_to_many
    sql_on: ${orders.id} = ${line_items.order_id} ;;
    type:  left_outer
  }

  join: products {
    relationship: many_to_one
    sql_on: ${line_items.product_id} = ${products.id} ;;
    type:  left_outer
  }

}

explore: line_items {
  label: "Line Items Summary"

  join: orders {
    relationship: many_to_one
    sql_on: ${line_items.order_id} = ${orders.id} ;;
    type:  left_outer
  }

  join: products {
    relationship: many_to_one
    sql_on: ${line_items.product_id} = ${products.id} ;;
    type:  left_outer
  }
}
