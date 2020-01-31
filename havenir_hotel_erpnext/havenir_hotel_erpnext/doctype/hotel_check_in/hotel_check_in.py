# -*- coding: utf-8 -*-
# Copyright (c) 2020, Havenir and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class HotelCheckIn(Document):
	def on_submit(self):
		self.status = 'To Check Out'
		doc = frappe.get_doc('Hotel Check In', self.name)
		doc.db_set('status','To Check Out')
		room = frappe.get_doc('Rooms', self.room)
		room.db_set('check_in_id',self.name)
		room.db_set('room_status','Checked In')
		room.save()
	
	def on_cancel(self):
		self.status = "Cancelled"
		doc = frappe.get_doc('Hotel Check In', self.name)
		doc.db_set('status','Cancelled')
		room = frappe.get_doc('Rooms', self.room)
		room.db_set('check_in_id','')
		room.db_set('room_status','Available')
		room.save()
