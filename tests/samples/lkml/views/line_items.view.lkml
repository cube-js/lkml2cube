# The name of this view in Looker is "Line Items"
view: line_items {
  view_label: "Line Items"
  # The sql_table_name parameter indicates the underlying database table
  # to be used for all fields in this view.
  sql_table_name: {{_user_attributes['ecom_database']}}.{{_user_attributes['ecom_schema']}}."LINE_ITEMS"
    ;;
  # In order to join this view in an Explore,
  # define primary_key: yes on a dimension that has no repeated values.

  dimension: id {
    primary_key: yes
    type: number
    sql: ${TABLE}."ID" ;;
  }

  # This table contains a foreign key to other tables.
  # Joins are defined in explores
  dimension: order_id {
    hidden: yes
    type: number
    sql: ${TABLE}."ORDER_ID" ;;
  }

  dimension: product_id {
    hidden: yes
    type: number
    sql: ${TABLE}."PRODUCT_ID" ;;
  }

  dimension: price {
    type: number
    sql: ${TABLE}."PRICE" ;;
  }

  dimension: quantity {
    label: "Quantity"
    type: number
    sql: ${TABLE}."QUANTITY" ;;
  }

  # You can reference other dimensions while defining a dimension.
  dimension: line_amount {
    type: number
    sql: ${quantity} * ${price};;
  }

  dimension: quantity_bins {
    type: tier
    style: integer
    bins: [0,10,50,100]
    sql: ${quantity}  ;;
  }

  # A measure is a field that uses a SQL aggregate function. Here are defined sum and count
  # measures for this view, but you can also add measures of many different aggregates.

  measure: total_quantity {
    type: sum
    sql: ${quantity} ;;
  }

  measure: total_amount {
    type: sum
    sql: ${line_amount} ;;
  }

  measure: count {
    type: count
  }


  # Dates and timestamps can be represented in Looker using a dimension group of type: time.
  # Looker converts dates and timestamps to the specified timeframes within the dimension group.

  dimension_group: created_at {
    type: time
    timeframes: [
      raw,
      time,
      date,
      week,
      month,
      quarter,
      year
    ]
    sql: ${TABLE}."CREATED_AT" ;;
  }

}