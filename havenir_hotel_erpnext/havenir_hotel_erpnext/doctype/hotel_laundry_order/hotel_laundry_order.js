// Copyright (c) 2020, Havenir and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hotel Laundry Order', {
	setup: function(frm) {
    // setting query for rooms to be visible in list
    frm.set_query('room', function(doc) {
      return {
        filters: {
          room_status: 'Checked In'
        }
      };
		});
		
		frm.set_query('item','items', function(doc) {
      return {
        filters: {
          item_group: 'Laundry'
        }
      };
    });
	},

	total_amount: function(frm){
		let temp_total_amount = 0;
		for (var i in frm.doc.items){
			temp_total_amount += frm.doc.items[i].amount;
		}
		frm.set_value('total_amount',temp_total_amount);
		frm.refresh_field('total_amount');
	}
});

frappe.ui.form.on('Hotel Laundry Order Item', {
	qty: function(frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn);
		if(row.rate != undefined){
			row.amount = row.qty * row.rate;
			frm.refresh_field('items');
			frm.trigger('total_amount')
		}
	},
	rate: function(frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn);
		if(row.qty != undefined){
			row.amount = row.qty * row.rate;
			frm.refresh_field('items');
			frm.trigger('total_amount')
		}
	},
	
	items_remove: function(frm, cdt, cdn){
		frm.trigger('total_amount');
	},
})