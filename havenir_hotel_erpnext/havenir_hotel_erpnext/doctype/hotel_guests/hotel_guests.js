// Copyright (c) 2020, Havenir and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hotel Guests', {
	guest_name: function(frm) {
		frm.set_value('guest_name',frm.doc.guest_name.toUpperCase())
	},

	validate: function(frm){
		if (frm.doc.cnic == undefined && frm.doc.passport_no == undefined){
			frappe.throw('Please enter CNIC or Passport Number')
		}
	}
});
