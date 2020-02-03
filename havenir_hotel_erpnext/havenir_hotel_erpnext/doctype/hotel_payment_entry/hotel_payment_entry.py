# -*- coding: utf-8 -*-
# Copyright (c) 2020, Havenir and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class HotelPaymentEntry(Document):
	def on_submit(self):
		create_payment_entry(self)
	
	def get_room_details(self):
		check_in_id = frappe.get_value('Rooms',self.room,'check_in_id')
		check_in_doc = frappe.get_doc('Hotel Check In',check_in_id)
		result = [check_in_doc.guest_id,check_in_doc.guest_name,check_in_doc.name]
		return result

def create_payment_entry(self):
	company = frappe.get_doc('Company',self.company)
	payment_entry = frappe.new_doc('Payment Entry')
	payment_entry.payment_type = 'Receive'
	payment_entry.mode_of_payment = 'Cash'
	payment_entry.paid_to = company.default_cash_account
	payment_entry.paid_from = company.default_receivable_account
	payment_entry.party_type = 'Customer'
	payment_entry.party = 'Hotel Walk In Customer'
	payment_entry.received_amount = self.amount_paid
	payment_entry.paid_amount = self.amount_paid
	payment_entry.remarks = 'Room ' + str(self.room)
	payment_entry.insert(ignore_permissions=True)
	payment_entry.submit()
