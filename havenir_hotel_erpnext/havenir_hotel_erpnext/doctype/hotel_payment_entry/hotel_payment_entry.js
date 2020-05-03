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

	refresh: function (frm) { 
		if (frm.doc.docstatus == 0){
			frm.trigger("entry_type")	
		}
	},

	entry_type: function(frm){
		if (frm.doc.room){
			frm
			.call('get_advance_payments')
			.then( r => {
				frm.doc.advance = r.message
				frm.refresh_field('advance')
			})
		}
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
				frm.doc.contact_no = data[3];
				frm.refresh_field('guest_id');
				frm.refresh_field('guest_name');
				frm.refresh_field('check_in_id');
				frm.refresh_field('contact_no');
				frm.trigger('entry_type');
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

		if (frm.doc.amount_paid > frm.doc.advance && frm.doc.entry_type == 'Refund'){
			frappe.throw('Cannot refund amount more than advance paid');
		}
	}
});
