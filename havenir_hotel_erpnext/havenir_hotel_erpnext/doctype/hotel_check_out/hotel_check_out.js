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
          frm.refresh_field("check_in_id");
          frm.refresh_field("cnic");
          frm.refresh_field("guest_name");
          frm.refresh_field("check_in");
        })
        .then(r => {
          frm.call("get_items").then(r => {
            if (r.message) {
              console.log(r.message);
              var data = r.message;
              var check_in_date = Date(frm.doc.check_in).replace(/-/g, "/");
              var check_out_date = Date(frm.doc.check_out).replace(/-/g, "/");
              var Difference_In_Time =
								check_in_date - check_out_date;
							console.log(frm.doc.check_in)
							console.log(check_in_date)
							console.log(frm.doc.check_out)
							console.log(check_out_date)
              var Difference_In_Days = Difference_In_Time / (1000 * 3600 * 24);
              console.log(Difference_In_Days);
              frm.add_child("items", {
                item: data[0][0].room_type,
                qty: 2,
                rate: data[0][0].rate,
                amount: 2 * data[0][0].rate
              });
              frm.refresh_field("items");
            }
          });
        });
    }
  }
});
