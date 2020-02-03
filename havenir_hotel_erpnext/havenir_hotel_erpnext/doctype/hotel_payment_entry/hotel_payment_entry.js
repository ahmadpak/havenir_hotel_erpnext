// Copyright (c) 2020, Havenir and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hotel Payment Entry', {
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
	
	room: function(frm){
		if (frm.doc.room != undefined) {
			frm
			.call('get_room_details')
			.then(r => {
				var data = r.message;
				frm.doc.guest_id = data[0];
				frm.doc.guest_name = data[1];
				frm.doc.check_in_id = data[2];
				frm.refresh_field('guest_id');
				frm.refresh_field('guest_name');
				frm.refresh_field('check_in_id');
			})
		}
	},

	amount_paid: function(frm){
		if (frm.doc.amount_paid <=0){
			frm.doc.amount_paid = 0;
			frm.refresh_field('amount_paid');
			frappe.msgprint('Amount Paid should be greater than zero.')
		}
	},

	validate: function(frm){
		if (frm.doc.amount_paid <=0){
			frm.doc.amount_paid = 0;
			frm.refresh_field('amount_paid');
			frappe.throw('Amount Paid should be greater than zero.')
		}
	}
});
