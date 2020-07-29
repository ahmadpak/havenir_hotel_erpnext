# -*- coding: utf-8 -*-
# Copyright (c) 2020, Havenir and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.core.doctype.sms_settings.sms_settings import send_sms


class HotelCheckIn(Document):
    def validate(self):
        for room in self.rooms:
            room_doc = frappe.get_doc('Rooms', room.room_no)
            if room_doc.room_status != 'Available':
                frappe.throw('Room {} is not Available'.format(room.room_no))

    def on_submit(self):
        self.status = 'To Check Out'
        doc = frappe.get_doc('Hotel Check In', self.name)
        doc.db_set('status', 'To Check Out')
        for room in self.rooms:
            room_doc = frappe.get_doc('Rooms', room.room_no)
            room_doc.db_set('check_in_id', self.name)
            room_doc.db_set('room_status', 'Checked In')
        # send_payment_sms(self)

    def on_cancel(self):
        self.status = "Cancelled"
        doc = frappe.get_doc('Hotel Check In', self.name)
        doc.db_set('status', 'Cancelled')
        for room in self.rooms:
            room_doc = frappe.get_doc('Rooms', room.room_no)
            room_doc.db_set('check_in_id', None)
            room_doc.db_set('room_status', 'Available')

    def get_room_price(self, room):
        room_price = frappe.get_value('Rooms', {
            'room_number': room
        }, [
            'price'
        ])
        return room_price

def send_payment_sms(self):
    sms_settings = frappe.get_doc('SMS Settings')
    if sms_settings.sms_gateway_url:
        msg = 'Dear '
        msg += self.guest_name
        msg += ''',\nWe are delighted that you have selected our hotel. The entire team at the Hotel PakHeritage welcomes you and trust your stay with us will be both enjoyable and comfortable.\nRegards,\nHotel Management'''
        send_sms([self.contact_no], msg = msg)