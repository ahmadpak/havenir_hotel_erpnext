// Copyright (c) 2020, Havenir and contributors
// For license information, please see license.txt

frappe.ui.form.on("Hotel Check Out", {
  setup: function(frm) {
    // setting query for rooms to be visible in list
    frm.set_query("room", function(doc) {
      return {
        filters: {
          room_status: "Checked In"
        }
      };
    });
  },

  validate: function(frm){
    if ((frm.doc.net_total_amount - frm.doc.total_payments - frm.doc.amount_paid - frm.doc.discount - frm.food_discount) > 0 && frm.doc.customer == 'Hotel Walk In Customer'){
      frappe.throw('Amount paid must be equal or greater than net balance amount.')
    }
    // checking if any item is pos
    let is_pos = 0;
    let temp_msc_exp_total = 0
    let temp_msc_total_payments = 0
    for (var i in frm.doc.items){
      if (frm.doc.items[i].is_pos == 1){
        is_pos = 1;
        temp_msc_exp_total += frm.doc.items[i].amount;
      }
    }

    if ( is_pos == 1 ){
      for (var i in frm.doc.payments){
        temp_msc_total_payments += frm.doc.payments[i].amount;
      }
      if (( frm.food_discount + temp_msc_total_payments + frm.doc.discount + frm.doc.amount_paid) < temp_msc_exp_total){
        frappe.throw('Please pay POS Charges.')
      }
    }
    
  },

  total: function(frm) {
    var temp_total_amount = 0;
    var temp_stay_charges = 0;
    var temp_food_charges = 0;
    var temp_laundry_charges = 0;
    for (var i in frm.doc.items) {
      temp_total_amount += frm.doc.items[i].amount;
      if (frm.doc.items[i].document_type == "Hotel Check In") {
        temp_stay_charges += frm.doc.items[i].amount;
      } else if (frm.doc.items[i].document_type == "Hotel Food Order") {
        temp_food_charges += frm.doc.items[i].amount;
      } else if (frm.doc.items[i].document_type == "Hotel Laundry Order") {
        temp_laundry_charges += frm.doc.items[i].amount;
      }
    }
    frm.doc.stay_charges = temp_stay_charges;
    frm.doc.food = temp_food_charges;
    frm.doc.laundry = temp_laundry_charges;
    frm.doc.total_amount = temp_total_amount;
    frm.refresh_field("stay_charges");
    frm.refresh_field("food");
    frm.refresh_field("laundry");
    frm.refresh_field("total_amount");

    // Total Bill
    let temp_total_bill = 0
    temp_total_bill = frm.doc.stay_charges + frm.doc.food - frm.doc.food_discount + frm.doc.service_charges + frm.doc.laundry
    frm.doc.total_bill = temp_total_bill;
    frm.refresh_field('total_bill');

    for (var i in frm.doc.taxes_and_charges) {
      if (frm.doc.taxes_and_charges[i].type == "On Total") {
        if (frm.doc.taxes_and_charges[i].rate) {
          frm.doc.taxes_and_charges[i].amount = 0;
          frm.doc.taxes_and_charges[i].amount =
            (frm.doc.taxes_and_charges[i].rate * frm.doc.total_amount) / 100;
          frm.refresh_field("taxes_and_charges");
        }
      }
    }

    let temp_total_pos_charges = 0;
    for (var i in frm.doc.items){
      if(frm.doc.customer != 'Hotel Walk In Customer' && frm.doc.items[i].is_pos == 1){
        temp_total_pos_charges += frm.doc.items[i].amount;
      }
      else if(frm.doc.customer == 'Hotel Walk In Customer' && frm.doc.items[i].is_pos == 1){
        frm.doc.items[i].is_pos = 0;
      }
    }
    if (temp_total_pos_charges != 0){
      frm.doc.total_pos_charges = temp_total_pos_charges + frm.doc.service_charges - frm.doc.food_discount;
    }
    else {
      frm.doc.total_pos_charges = 0;
    }
    frm.refresh_field('items');
    frm.refresh_field('total_pos_charges');

    var temp_net_total_amount = 0;
    var temp_total_taxes_and_charges = 0;
    temp_net_total_amount += frm.doc.total_amount;
    for (var i in frm.doc.taxes_and_charges) {
      if (frm.doc.taxes_and_charges[i].amount) {
        temp_net_total_amount += frm.doc.taxes_and_charges[i].amount;
        temp_total_taxes_and_charges += frm.doc.taxes_and_charges[i].amount;
      }
    }
    frm.doc.total_taxes_and_charges = temp_total_taxes_and_charges;
    frm.doc.net_total_amount = temp_net_total_amount;
    
    var temp_total_payments = 0;
    for (var i in frm.doc.payments){
      temp_total_payments += frm.doc.payments[i].amount;
    }

    frm.doc.net_balance_amount = 0;
    var temp_net_balance_amount = frm.doc.net_total_amount + frm.doc.service_charges - frm.doc.food_discount- temp_total_payments - frm.doc.discount - frm.doc.amount_paid;
    if (temp_net_balance_amount > 0){
      frm.doc.net_balance_amount = temp_net_balance_amount;
    }
    
    frm.doc.refund = 0;
    if ( temp_net_balance_amount < 0 && frm.doc.total_pos_charges == 0){
      frm.doc.refund = -temp_net_balance_amount;
    }
    else if (frm.doc.total_pos_charges > 0) {
      frm.doc.refund = -(frm.doc.total_pos_charges - frm.doc.total_payments - frm.doc.amount_paid - frm.doc.discount);
    }
    
    frm.refresh_field("total_taxes_and_charges");
    frm.refresh_field("net_total_amount");
    frm.refresh_field('net_balance_amount');
    frm.refresh_field('refund');
  },

  room: function(frm) {
    if (frm.doc.room != undefined) {
      frm
        .call("get_check_in_details")
        .then(r => {
          var data = r.message;
          frm.doc.check_in_id = data[0];
          frm.doc.cnic = data[1];
          frm.doc.guest_name = data[2];
          frm.doc.check_in = data[3];
          frm.doc.contact_no = data[4];
          frm.doc.guest_id = data[5];
          frm.refresh_field("check_in_id");
          frm.refresh_field("cnic");
          frm.refresh_field("guest_name");
          frm.refresh_field("check_in");
          frm.refresh_field("contact_no");
          frm.refresh_field("guest_id");
        })
        .then(r => {
          frm.call("calculate_stay_days").then(r => {});

          frm.call("get_items").then(r => {
            if (r.message) {
              var data = r.message;
              if (data[0] == 0) {
                data[0] = 1;
              }
              frm.doc.items = undefined;
              frm.add_child("items", {
                item: data[1].room,
                qty: data[0],
                rate: data[1].price,
                amount: data[0] * data[1].price,
                date: frm.doc.check_in,
                document_type: "Hotel Check In",
                document_id: frm.doc.check_in_id
              });
              for (var i in data[2]) {
                for (var j in data[2][i].items) {
                  frm.add_child("items", {
                    item: data[2][i].items[j].item,
                    qty: data[2][i].items[j].qty,
                    rate: data[2][i].items[j].rate,
                    amount: data[2][i].items[j].amount,
                    date: data[2][i].date,
                    document_type: "Hotel Food Order",
                    document_id: data[2][i].name,
                    is_pos : 1
                  });
                }
              }
              for (var i in data[3]) {
                for (var j in data[3][i].items) {
                  frm.add_child("items", {
                    item: data[3][i].items[j].item,
                    qty: data[3][i].items[j].qty,
                    rate: data[3][i].items[j].rate,
                    amount: data[3][i].items[j].amount,
                    date: data[3][i].date,
                    document_type: "Hotel Laundry Order",
                    document_id: data[3][i].name,
                    is_pos : 1
                  });
                }
              }
              
              frm.doc.food_discount = data[5];
              frm.doc.service_charges = data[6];
              frm.refresh_field('food_discount');
              frm.refresh_field('service_charges');

              let temp_total_payments = 0
              frm.doc.payments = null;
              for (var i in data[4]){
                frm.add_child("payments", {
                  payment_entry: data[4][i].payment_entry,
                  amount: data[4][i].amount_paid,
                  posting_date: data[4][i].posting_date
                })
                temp_total_payments += data[4][i].amount_paid
              }
              frm.doc.total_payments = temp_total_payments;
              frm.refresh_field("items");
              frm.refresh_field("payments");
              frm.refresh_field("total_payments");
              frm.trigger("total");
            }
          });
        });
    }
  },

  customer: function(frm){
    if (frm.doc.customer != 'Hotel Walk In Customer'){
      for (var i in frm.doc.items){
        if (frm.doc.items[i].document_type != 'Hotel Check In'){
          frm.doc.items[i].is_pos = 1;
        }
      }
      frm.refresh_field('items');
    }
    frm.trigger('total');
  },

  check_out: function(frm) {
    frm.call("calculate_stay_days").then(r => {
      if (r.message) {
        if (r.message > -1) {
          var doc = frm.doc;
          var days = 0;
          if (r.message == 0) {
            days = 1;
          } else {
            days = r.message;
          }
          for (var i in doc.items) {
            if (doc.items[i].item) {
              if (doc.items[i].document_type.includes("Hotel Check In")) {
                doc.items[i].qty = days;
                doc.items[i].amount = days * doc.items[i].rate;
                frm.refresh_field("items");
              }
            }
          }
          frm.trigger("total");
        } else {
          frm.doc.check_out = undefined;
          frm.refresh_field("check_out");
          frappe.msgprint("Check out date cannot be before check in date.");
        }
      }
    });
  },

  service_charges: function (frm){
    frm.trigger("total");
  },

  discount: function(frm){
    frm.trigger("total");
  },
  
  amount_paid: function(frm){
    if (frm.doc.amount_paid < 0 ){
      frm.doc.amount_paid = 0;
      frm.refresh_field('amount_paid');
      frappe.msgprint('Amount paid must be greater than zero.')
    }
    else {
      frm.doc.refund = -(frm.doc.net_balance_amount - frm.doc.amount_paid);
      frm.refresh_field('refund');
    }
    frm.trigger('total');
  },

  is_tax_invoice: function(frm){
    if (frm.doc.is_tax_invoice == 1){
      frm.doc.naming_series = 'INV-CHK-OUT-.YYYY.-';
    }
    else{
      frm.doc.naming_series = 'CHK-OUT-.YYYY.-';
    }
    frm.refresh_field('naming_series');
  }
});

frappe.ui.form.on('Hotel Check Out Item', {
  is_pos: function(frm, cdt, cdn){
    frm.trigger('total');
  }
})


frappe.ui.form.on("Hotel Check Out Taxes and Charges", {
  type: function(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    if (row.type == "On Total") {
      if (row.rate) {
        row.amount = row.rate * frm.doc.total_amount;
      } else {
        row.amount = undefined;
      }
    } else {
      row.amount = undefined;
    }
    frm.refresh_field("taxes_and_charges");
    frm.trigger("total");
  },

  rate: function(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    if (row.type == "Actual") {
      row.rate = undefined;
    } else {
      row.amount = (row.rate * frm.doc.total_amount) / 100;
    }
    frm.refresh_field("taxes_and_charges");
    frm.trigger("total");
  },

  amount: function(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    if (row.type == "On Total") {
      if (row.rate) {
        row.amount = (row.rate * frm.doc.total_amount) / 100;
      } else {
        row.amount = undefined;
      }
    } else if (row.type == "") {
      row.amount = undefined;
    }

    frm.trigger("total");
  },

  taxes_and_charges_remove: function(frm, cdt, cdn) {
    frm.trigger("total");
  },

});
