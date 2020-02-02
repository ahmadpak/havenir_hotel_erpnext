# -*- coding: utf-8 -*-
# Copyright (c) 2020, Havenir and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class HotelCheckOut(Document):
    def on_submit(self):
        room_doc = frappe.get_doc('Rooms',self.room)
        room_doc.db_set('room_status','Available')
        check_in_doc = frappe.get_doc('Hotel Check In',self.check_in_id)
        all_checked_out = 1

        room_food_order_list = frappe.get_list('Room Food Order', filters={
            'status': 'To Check Out',
            'room': self.room,
            'check_in_id': self.check_in_id
        })

        for food_order in room_food_order_list:
            food_order_doc = frappe.get_doc('Room Food Order', food_order.name)
            food_order_doc.db_set('status','Completed')

        room_laundry_order_list = frappe.get_list('Room Laundry Order', filters={
            'status': 'To Check Out',
            'room': self.room,
            'check_in_id': self.check_in_id
        })

        for laundry_order in room_laundry_order_list:
            laundry_order_doc = frappe.get_doc('Room Laundry Order', laundry_order.name)
            laundry_order_doc.db_set('status','Completed')

        for room in check_in_doc.rooms:
            if frappe.db.get_value('Rooms',room.room_no,'room_status') == 'Checked In':
                all_checked_out = 0
        if all_checked_out == 1:
            check_in_doc.db_set('status','Completed')

    def get_check_in_details(self):
        room_doc = frappe.get_doc('Rooms', self.room)
        check_in_doc = frappe.get_doc('Hotel Check In', room_doc.check_in_id)
        return [check_in_doc.name, check_in_doc.cnic, check_in_doc.guest_name, check_in_doc.check_in, check_in_doc.contact_no, check_in_doc.guest_id]

    def calculate_stay_days(self):
        if frappe.utils.data.date_diff(self.check_out, self.check_in) == 0:
            return 1
        else:
            return frappe.utils.data.date_diff(self.check_out, self.check_in)

    def get_items(self):
        # Getting Hotel Check In Details
        hotel_check_in = frappe.get_doc('Hotel Check In', self.check_in_id)
        check_in_dict = {}
        for room in hotel_check_in.rooms:
            if room.room_no == self.room:
                check_in_dict['room_type'] = room.room_type
                check_in_dict['price'] = room.price

        # Geting Room Food Order Details
        food_order_list = []
        room_food_order_list = frappe.get_list('Room Food Order', filters={
            'status': 'To Check Out',
            'room': self.room,
            'check_in_id': self.check_in_id
        })
        for food_order in room_food_order_list:
            food_order_dict = {}
            food_order_doc = frappe.get_doc('Room Food Order', food_order.name)
            food_order_dict['name'] = food_order_doc.name
            food_order_dict['date'] = food_order_doc.posting_date
            food_order_dict['source'] = food_order_doc.source
            food_order_dict['items'] = []
            # Looping through items
            for item in food_order_doc.items:
                food_item_dict = {}
                food_item_dict['item'] = item.item
                food_item_dict['qty'] = item.qty
                food_item_dict['rate'] = item.rate
                food_item_dict['amount'] = item.amount
                food_order_dict['items'].append(food_item_dict)
            food_order_list.append(food_order_dict)

        # Getting Room Laundry Order Details
        laundry_order_list = []
        room_laundry_order_list = frappe.get_list('Room Laundry Order', filters={
            'status': 'To Check Out',
            'room': self.room,
            'check_in_id': self.check_in_id
        })
        for laundry_order in room_laundry_order_list:
            laundry_order_dict = {}
            laundry_order_doc = frappe.get_doc(
                'Room Laundry Order', laundry_order.name)
            laundry_order_dict['name'] = laundry_order_doc.name
            laundry_order_dict['date'] = laundry_order_doc.posting_date
            laundry_order_dict['source'] = laundry_order_doc.source
            laundry_order_dict['items'] = []
            # Looping through items
            for item in laundry_order_doc.items:
                laundry_item_dict = {}
                laundry_item_dict['item'] = item.item
                laundry_item_dict['qty'] = item.qty
                laundry_item_dict['rate'] = item.rate
                laundry_item_dict['amount'] = item.amount
                laundry_order_dict['items'].append(laundry_item_dict)
            laundry_order_list.append(laundry_order_dict)
        stay_days = frappe.utils.data.date_diff(self.check_out, self.check_in)
        return [stay_days, check_in_dict, food_order_list, laundry_order_list]
