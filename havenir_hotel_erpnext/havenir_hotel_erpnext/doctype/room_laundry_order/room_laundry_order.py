# -*- coding: utf-8 -*-
# Copyright (c) 2020, Havenir and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RoomLaundryOrder(Document):
	def validate(self):
		room_doc = frappe.get_doc('Rooms', self.room)
		if room_doc.room_status != 'Checked In' and room_doc.check_in_id == self.check_in_id:
				frappe.throw('Room Status is not Checked In')
				
	def on_submit(self):
		self.status = 'To Check Out'
		doc = frappe.get_doc('Room Laundry Order', self.name)
		doc.db_set('status','To Check Out')
	
	def on_cancel(self):
		self.status = "Cancelled"
		doc = frappe.get_doc('Room Laundry Order', self.name)
		doc.db_set('status','Cancelled')
