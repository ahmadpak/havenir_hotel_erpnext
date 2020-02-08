frappe.listview_settings["Hotel Food Order"] = {
  // add_fields: ["status", "produciton_item", "weight", "qty","produced_qty", "planned_start_date", "expected_delivery_date"],
  filters: [["status", "!=", "Cancelled"]],
  get_indicator: function(doc) {
    if (doc.status === "Submitted") {
      return [__("To Check Out"), "orange", "status,=,Submitted"];
    } else {
      return [
        __(doc.status),
        {
          Draft: "red",
          "To Check Out": "orange",
          Completed: "green",
          Cancelled: "red"
        }[doc.status],
        "status,=," + doc.status
      ];
    }
  } //*/
};
