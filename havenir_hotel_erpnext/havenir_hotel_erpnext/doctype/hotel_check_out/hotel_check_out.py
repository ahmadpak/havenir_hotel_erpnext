# -*- coding: utf-8 -*-
# Copyright (c) 2020, Havenir and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class HotelCheckOut(Document):
    def validate(self):
        room_doc = frappe.get_doc('Rooms', self.room)
        if room_doc.room_status != 'Checked In' and room_doc.check_in_id == self.check_in_id:
            frappe.throw('Room Status is not Checked In')

    def on_submit(self):
        room_doc = frappe.get_doc('Rooms',self.room)
        room_doc.db_set('room_status','Available')
        room_doc.db_set('check_in_id',None)
        check_in_doc = frappe.get_doc('Hotel Check In',self.check_in_id)
        all_checked_out = 1

        # Setting Food Orders to Complete
        room_food_order_list = frappe.get_list('Hotel Food Order', filters={
            'status': 'To Check Out',
            'room': self.room,
            'check_in_id': self.check_in_id
        })

        for food_order in room_food_order_list:
            food_order_doc = frappe.get_doc('Hotel Food Order', food_order.name)
            food_order_doc.db_set('status','Completed')

        # Setting Laundry Orders to Complete
        room_laundry_order_list = frappe.get_list('Hotel Laundry Order', filters={
            'status': 'To Check Out',
            'room': self.room,
            'check_in_id': self.check_in_id
        })

        for laundry_order in room_laundry_order_list:
            laundry_order_doc = frappe.get_doc('Hotel Laundry Order', laundry_order.name)
            laundry_order_doc.db_set('status','Completed')

        # Setting Check In doc to Complete
        for room in check_in_doc.rooms:
            if frappe.db.get_value('Rooms',room.room_no,'room_status') == 'Checked In':
                all_checked_out = 0
        if all_checked_out == 1:
            check_in_doc.db_set('status','Completed')

        # Creating Additional Hotel Payment Vouchers
        if self.amount_paid > 0 and self.customer == 'Hotel Walk In Customer':
            payment_doc = frappe.new_doc('Hotel Payment Entry')
            payment_doc.room = self.room
            payment_doc.amount_paid = self.amount_paid - self.refund
            payment_doc.guest_id = self.guest_id
            payment_doc.check_in_id = self.check_in_id
            payment_doc.guest_name = self.guest_name
            payment_doc.contact_no = self.contact_no
            payment_doc.save()
            payment_doc.submit()
        
        if self.amount_paid == 0 and self.refund > 0:
            hotel_refund_entry = frappe.new_doc('Hotel Payment Entry')
            hotel_refund_entry.company = self.company
            hotel_refund_entry.posting_date = self.posting_date
            hotel_refund_entry.entry_type = 'Refund'
            hotel_refund_entry.room = self.room
            hotel_refund_entry.amount_paid = self.refund
            hotel_refund_entry.guest_id = self.guest_id
            hotel_refund_entry.check_in_id = self.check_in_id
            hotel_refund_entry.guest_name = self.guest_name
            hotel_refund_entry.save()
            hotel_refund_entry.submit()



        # Creating Sales Invoice
        create_sales_invoice(self, all_checked_out)
        
        
        

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
                check_in_dict['room'] = room.room_no
                check_in_dict['price'] = room.price

        # Geting Hotel Food Order Details
        total_food_discount = 0
        total_service_charges = 0
        food_order_list = []
        room_food_order_list = frappe.get_list('Hotel Food Order', filters={
            'status': 'To Check Out',
            'room': self.room,
            'check_in_id': self.check_in_id,
            'is_paid': 0
        })
        for food_order in room_food_order_list:
            food_order_dict = {}
            food_order_doc = frappe.get_doc('Hotel Food Order', food_order.name)
            food_order_dict['name'] = food_order_doc.name
            food_order_dict['date'] = food_order_doc.posting_date
            food_order_dict['order_type'] = food_order_doc.order_type
            food_order_dict['items'] = []
            total_service_charges += food_order_doc.service_charges
            total_food_discount += food_order_doc.discount_amount
            # Looping through items
            for item in food_order_doc.items:
                food_item_dict = {}
                food_item_dict['item'] = item.item
                food_item_dict['qty'] = item.qty
                food_item_dict['rate'] = item.rate
                food_item_dict['amount'] = item.amount
                food_order_dict['items'].append(food_item_dict)
            food_order_list.append(food_order_dict)

        # Getting Hotel Laundry Order Details
        laundry_order_list = []
        room_laundry_order_list = frappe.get_list('Hotel Laundry Order', filters={
            'status': 'To Check Out',
            'room': self.room,
            'check_in_id': self.check_in_id
        })
        for laundry_order in room_laundry_order_list:
            laundry_order_dict = {}
            laundry_order_doc = frappe.get_doc(
                'Hotel Laundry Order', laundry_order.name)
            laundry_order_dict['name'] = laundry_order_doc.name
            laundry_order_dict['date'] = laundry_order_doc.posting_date
            laundry_order_dict['order_type'] = laundry_order_doc.order_type
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

        # Getting Payments
        payment_entry_list = []
        room_payment_entry_list = frappe.get_list('Hotel Payment Entry',filters={
            'check_in_id' : self.check_in_id,
            'docstatus': 1,
            'room': self.room
        }, order_by='name asc')

        for payment in room_payment_entry_list:
            payment_entry_dict = {}
            payment_doc = frappe.get_doc('Hotel Payment Entry', payment)
            payment_entry_dict['payment_entry'] = payment_doc.name
            if payment_doc.entry_type == 'Receive':
                payment_entry_dict['amount_paid'] = payment_doc.amount_paid
            else:
                payment_entry_dict['amount_paid'] = -payment_doc.amount_paid
            payment_entry_dict['posting_date'] = payment_doc.posting_date
            payment_entry_list.append(payment_entry_dict)

        return [stay_days, check_in_dict, food_order_list, laundry_order_list, payment_entry_list, total_food_discount, total_service_charges]


def create_sales_invoice(self, all_checked_out):
    # Sales Invoice for Hotel Walk In Customer
    if self.customer == 'Hotel Walk In Customer':
        # Creating Sales Invoice
        sales_invoice_doc = frappe.new_doc('Sales Invoice')
        company = frappe.get_doc('Company', self.company)
        sales_invoice_doc.discount_amount = 0

        sales_invoice_doc.customer = self.customer
        sales_invoice_doc.check_in_id = self.check_in_id
        sales_invoice_doc.check_in_date = frappe.get_value('Hotel Check In', self.check_in_id, 'check_in')
        sales_invoice_doc.due_date = frappe.utils.data.today()
        sales_invoice_doc.debit_to = company.default_receivable_account

        # Looping through the check out items
        for item in self.items:
            item_doc = frappe.get_doc('Item', item.item)

            # Getting Item default Income Account
            default_income_account = None
            for item_default in item_doc.item_defaults:
                if item_default.company == self.company:
                    if item_default.income_account:
                        default_income_account = item_default.income_account
                    else:
                        default_income_account = company.default_income_account

            # Adding Items to Sales Invoice
            sales_invoice_doc.append('items',{
                'item_code': item_doc.item_code,
                'item_name': item_doc.item_name,
                'description': item_doc.description,
                'qty': item.qty,
                'uom': item_doc.stock_uom,
                'rate': item.rate,
                'amount': item.amount,
                'income_account': default_income_account
            })
        if self.discount != 0:
            sales_invoice_doc.discount_amount += self.discount
        if self.food_discount != 0:
            sales_invoice_doc.discount_amount += self.food_discount
        if self.service_charges != 0:
            item_doc = frappe.get_doc('Item', 'SERVICE CHARGES')

            # Getting Item default Income Account
            default_income_account = None
            for item_default in item_doc.item_defaults:
                if item_default.company == self.company:
                    if item_default.income_account:
                        default_income_account = item_default.income_account
                    else:
                        default_income_account = company.default_income_account

            # Adding Items to Sales Invoice
            sales_invoice_doc.append('items',{
                'item_code': item_doc.item_code,
                'item_name': item_doc.item_name,
                'description': item_doc.description,
                'qty': 1,
                'uom': item_doc.stock_uom,
                'rate': self.service_charges,
                'amount': self.service_charges,
                'income_account': default_income_account
            })
        sales_invoice_doc.insert(ignore_permissions=True)
        sales_invoice_doc.submit()
    if all_checked_out == 1 or self.customer != 'Hotel Walk In Customer': 
        create_walk_in_invoice = 0
        for item in self.items:
            if item.is_pos == 1:
                create_walk_in_invoice = 1
        if create_walk_in_invoice == 1:
            # Creating Sales Invoice
            sales_invoice_doc = frappe.new_doc('Sales Invoice')
            company = frappe.get_doc('Company', self.company)
            sales_invoice_doc.discount_amount = 0

            sales_invoice_doc.customer = 'Hotel Walk In Customer'
            sales_invoice_doc.check_in_id = self.check_in_id
            sales_invoice_doc.check_in_date = frappe.get_value('Hotel Check In', self.check_in_id, 'check_in')
            sales_invoice_doc.due_date = frappe.utils.data.today()
            sales_invoice_doc.debit_to = company.default_receivable_account

            # Looping through the check out items
            for item in self.items:
                if item.is_pos == 1:
                    item_doc = frappe.get_doc('Item', item.item)

                    # Getting Item default Income Account
                    default_income_account = None
                    for item_default in item_doc.item_defaults:
                        if item_default.company == self.company:
                            if item_default.income_account:
                                default_income_account = item_default.income_account
                            else:
                                default_income_account = company.default_income_account

                    # Adding Items to Sales Invoice
                    sales_invoice_doc.append('items',{
                        'item_code': item_doc.item_code,
                        'item_name': item_doc.item_name,
                        'description': item_doc.description,
                        'qty': item.qty,
                        'uom': item_doc.stock_uom,
                        'rate': item.rate,
                        'amount': item.amount,
                        'income_account': default_income_account
                    })
            if self.discount:
                sales_invoice_doc.discount_amount = self.discount
            if self.food_discount != 0:
                sales_invoice_doc.discount_amount += self.food_discount

            if self.service_charges != 0:
                item_doc = frappe.get_doc('Item', 'SERVICE CHARGES')

                # Getting Item default Income Account
                default_income_account = None
                for item_default in item_doc.item_defaults:
                    if item_default.company == self.company:
                        if item_default.income_account:
                            default_income_account = item_default.income_account
                        else:
                            default_income_account = company.default_income_account

                # Adding Items to Sales Invoice
                sales_invoice_doc.append('items',{
                    'item_code': item_doc.item_code,
                    'item_name': item_doc.item_name,
                    'description': item_doc.description,
                    'qty': 1,
                    'uom': item_doc.stock_uom,
                    'rate': self.service_charges,
                    'amount': self.service_charges,
                    'income_account': default_income_account
                })

            sales_invoice_doc.insert(ignore_permissions=True)
            sales_invoice_doc.submit()

            # Creating Additional Payment Vouchers
            if self.total_pos_charges - self.total_payments > 0:
                payment_doc = frappe.new_doc('Hotel Payment Entry')
                payment_doc.room = self.room
                payment_doc.amount_paid = self.total_pos_charges - self.total_payments - self.discount
                payment_doc.guest_id = self.guest_id
                payment_doc.check_in_id = self.check_in_id
                payment_doc.guest_name = self.guest_name
                payment_doc.contact_no = self.contact_no
                payment_doc.save()
                payment_doc.submit()

        
        # Getting list of check_out with same check in id and is not Hotel Walk In Customer
        check_out_list = frappe.get_list('Hotel Check Out', filters={
            'docstatus': 1,
            'check_in_id': self.check_in_id,
            'customer': ['not like', 'Hotel Walk In Customer']
        },
        order_by = 'name asc')
        if all_checked_out == 1 and check_out_list:
            # Creating Sales Invoice
            sales_invoice_doc = frappe.new_doc('Sales Invoice')
            company = frappe.get_doc('Company', self.company)
            sales_invoice_doc.discount_amount = 0
            
            # Looping through the list
            for check_out_name in check_out_list:
                check_out_doc = frappe.get_doc('Hotel Check Out', check_out_name)
                if sales_invoice_doc.customer == None:
                    sales_invoice_doc.customer = check_out_doc.customer
                    sales_invoice_doc.check_in_id = check_out_doc.check_in_id
                    sales_invoice_doc.check_in_date = frappe.get_value('Hotel Check In', self.check_in_id, 'check_in')
                    sales_invoice_doc.due_date = frappe.utils.data.today()
                    sales_invoice_doc.debit_to = company.default_receivable_account
                
                # Looping through the check out items
                exclude_discount = 0
                for item in check_out_doc.items:
                    if item.is_pos == 0:
                        item_doc = frappe.get_doc('Item', item.item)
                        # Getting Item default Income Account
                        default_income_account = None
                        for item_default in item_doc.item_defaults:
                            if item_default.company == check_out_doc.company:
                                if item_default.income_account:
                                    default_income_account = item_default.income_account
                                else:
                                    default_income_account = company.default_income_account

                        # Adding Items to Sales Invoice
                        sales_invoice_doc.append('items',{
                            'item_code': item_doc.item_code,
                            'item_name': item_doc.item_name,
                            'description': item_doc.description,
                            'qty': item.qty,
                            'uom': item_doc.stock_uom,
                            'rate': item.rate,
                            'amount': item.amount,
                            'income_account': default_income_account
                        })
                    else:
                        exclude_discount = 1

                if check_out_doc.discount != 0 and exclude_discount == 0:
                    sales_invoice_doc.discount_amount += check_out_doc.discount
                if self.food_discount != 0 and exclude_discount == 0:
                    sales_invoice_doc.discount_amount += self.food_discount
            sales_invoice_doc.insert(ignore_permissions=True)
            sales_invoice_doc.submit()