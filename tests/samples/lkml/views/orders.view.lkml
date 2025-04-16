# The name of this view in Looker is "Orders"
view: orders {
  view_label: "Orders"
  # The sql_table_name parameter indicates the underlying database table
  # to be used for all fields in this view.
  sql_table_name: {{_user_attributes['ecom_database']}}.{{_user_attributes['ecom_schema']}}."ORDERS"
    ;;
  # In order to join this view in an Explore,
  # define primary_key: yes on a dimension that has no repeated values.

  dimension: id {
    primary_key: yes
    type: number
    sql: ${TABLE}."ID" ;;
  }

  dimension: item_id {
    label: "Item ID"
    description: "My description"
    type: number
    sql: ${TABLE}.item_id ;;
  }

  # Here's what a typical dimension looks like in LookML.
  # A dimension is a groupable field that can be used to filter query results.
  # This dimension will be called "Order Status" in Explore.

  dimension: order_status {
    type: string
    sql: ${TABLE}."STATUS" ;;
    description: "Order Status - The status of the order, making the description longer just to test correct parsing, adding some extra characters to make sure it is parsed correctly like ( a,b ) [ d, e]."
  }

  dimension: is_cancelled {
    label: "Is Cancelled"
    type: yesno
    sql: case ${TABLE}."STATUS" when "CANCELLED" then true else false end ;;
  }

  # A measure is a field that uses a SQL aggregate function. Here are defined count and count_distinct
  # measures for this view, but you can also add measures of many different aggregates.

  measure: count {
    type: count
  }

  measure: order_count_distinct {
    type: count_distinct
    sql: ${id} ;;
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

  dimension_group: completed_at {
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
    sql: ${TABLE}."COMPLETED_AT" ;;
  }
}