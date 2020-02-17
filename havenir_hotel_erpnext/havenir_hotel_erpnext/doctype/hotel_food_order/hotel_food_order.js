// Copyright (c) 2020, Havenir and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotel Food Order", {
  setup: function(frm) {
    // setting query for rooms to be visible in list
    frm.set_query("room", function(doc) {
      return {
        filters: {
          room_status: "Checked In"
        }
      };
    });

    frm.set_query("item", "items", function(doc) {
      return {
        filters: {
          item_group: "Restaurant"
        }
      };
    });
  },

  validate: function(frm) {
    if (frm.doc.order_type == "Room") {
      if (frm.doc.room == null || frm.doc.room == "") {
        frappe.throw("Please select room no");
      }
    } else if (frm.doc.order_type == "Restaurant") {
      if (frm.doc.table == null) {
        frappe.throw("Please select table no");
      }
    } else if (frm.doc.order_type == "Staff") {
      if (frm.doc.department == null) {
        frappe.throw("Please select department");
      }
    }

    if (
      frm.doc.order_type == "Restaurant" ||
			frm.doc.order_type == "Take Away" ||
			frm.doc.is_paid == 1
    ) {
      let temp_net_balance =
        frm.doc.total_amount - frm.doc.discount_amount - frm.doc.amount_paid;
      if (temp_net_balance > 0) {
        frappe.throw("Please pay the bill to proceed");
      }
    }
  },

  total_amount: function(frm) {
    let temp_total_amount = 0;
    for (var i in frm.doc.items) {
      if (frm.doc.items[i].amount) {
        temp_total_amount += frm.doc.items[i].amount;
      }
    }
    frm.set_value("total_amount", temp_total_amount);
    var temp_discount_percentage =
      (frm.doc.discount_amount / temp_total_amount) * 100;
    frm.doc.discount_percentage = temp_discount_percentage;
    frm.refresh_field("total_amount");
    frm.refresh_field("discount_percentage");
    frm.trigger("update_bill");
  },

  update_bill: function(frm) {
    frm.doc.net_payable = frm.doc.total_amount - frm.doc.discount_amount + frm.doc.service_charges;
    frm.refresh_field("net_payable");

    var temp_refund = frm.doc.net_payable - frm.doc.amount_paid;
    if (temp_refund < 0) {
      frm.doc.refund = -temp_refund;
    } else {
      frm.doc.refund = 0;
    }
    frm.refresh_field("refund");
  },

  order_type: function(frm) {
    if (frm.doc.order_type == "Room") {
      frm.doc.discount_amount = 0;
      frm.doc.amount_paid = 0;
      frm.refresh_field("discount_amount");
      frm.refresh_field("amount_paid");
      frm.trigger("total_amount");
    } else {
      frm.doc.discount_amount = 0;
      frm.doc.table = null;
      frm.doc.room = null;
      frm.refresh_field("table");
      frm.refresh_field("room");

      frm.doc.amount_paid = 0;
      frm.doc.check_in_id = null;
      frm.doc.guest_name = null;
      frm.refresh_field("discount_amount");
      frm.refresh_field("amount_paid");
      frm.refresh_field("check_in_id");
      frm.refresh_field("guest_name");
      frm.trigger("total_amount");
    }
  },

  discount_amount: function(frm) {
    frm.doc.discount_percentage =
      (frm.doc.discount_amount / frm.doc.total_amount) * 100;
    frm.refresh_field("discount_amount");
    frm.refresh_field("discount_percentage");
    frm.trigger("update_bill");
  },

  discount_percentage: function(frm) {
    frm.doc.discount_amount = Math.round(
      (frm.doc.total_amount * frm.doc.discount_percentage) / 100
    );
    frm.refresh_field("discount_amount");
    frm.trigger("update_bill");
  },

  service_charges: function(frm){
    frm.trigger('update_bill');
  },

  amount_paid: function(frm) {
    frm.trigger("update_bill");
  }
});

frappe.ui.form.on("Hotel Food Order Item", {
  item: function(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    if (row.item) {
      frm.call("get_price", { item: row.item }).then(r => {
        if (r.message) {
					frappe.model.set_value(cdt, cdn, 'rate', r.message);
				}
      })
    }
  },

  qty: function(frm, cdt, cdn) {
			let row = frappe.get_doc(cdt, cdn);
			if (row.qty < 0){
				row.qty = 0;
				frm.refresh_field('items')
				frappe.throw('Qty cannot be negative!')
			}
			if (row.rate && row.qty) {
				row.amount = row.qty * row.rate;
				frm.refresh_field("items");
				frm.trigger("total_amount");
			}
  },
  rate: function(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    if (row.qty != undefined && row.item != undefined) {
      if (row.item == 'BREAKFAST COMPLIMENTARY' || row.item == 'LUNCH COMPLIMENTARY' || row.item == 'DINNER COMPLIMENTARY'){
        row.amount = row.qty * row.rate;
        frm.refresh_field("items");
        frm.trigger("total_amount");
      }
      else {
        frm.call("get_price", { item: row.item }).then(r => {
          if (r.message) {
            frappe.model.set_value(cdt, cdn, 'rate', r.message);
            row.amount = row.qty * row.rate;
            frm.refresh_field("items");
            frm.trigger("total_amount");
          }
        })
      }
    }
  },

  items_remove: function(frm, cdt, cdn) {
    frm.trigger("total_amount");
  }
});
