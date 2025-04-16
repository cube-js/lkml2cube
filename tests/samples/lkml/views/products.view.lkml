# The name of this view in Looker is "Products"
view: products {
  view_label: "Products"
  # The sql_table_name parameter indicates the underlying database table
  # to be used for all fields in this view.
  sql_table_name: {{_user_attributes['ecom_database']}}.{{_user_attributes['ecom_schema']}}."PRODUCTS"
    ;;
  # In order to join this view in an Explore,
  # define primary_key: yes on a dimension that has no repeated values.

  dimension: id {
    primary_key: yes
    type: number
    sql: ${TABLE}."ID" ;;
  }

  # Here's what a typical dimension looks like in LookML.
  # A dimension is a groupable field that can be used to filter query results.
  # This dimension will be called "Product Category" in Explore.

  dimension: product_category {
    type: string
    sql: ${TABLE}."PRODUCT_CATEGORY" ;;
  }


  # A measure is a field that uses a SQL aggregate function. Here are defined count 
  # measure for this view, but you can also add measures of many different aggregates.

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