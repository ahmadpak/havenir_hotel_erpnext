# -*- coding: utf-8 -*-
# Copyright (c) 2020, Havenir and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class HotelFoodOrder(Document):
    def validate(self):
        if self.room and self.order_type == 'Room':
            room_doc = frappe.get_doc('Rooms', self.room)
            if room_doc.room_status != 'Checked In' and room_doc.check_in_id == self.check_in_id:
                frappe.throw('Room Status is not Checked In')

    def on_submit(self):
        create_invoice(self)
        set_status(self)

    def on_cancel(self):
        self.status = "Cancelled"
        doc = frappe.get_doc('Hotel Food Order', self.name)
        doc.db_set('status', 'Cancelled')

    def get_price(self, item):
        item_price = frappe.get_value('Item Price', 
        {
            'price_list': 'Standard Selling',
            'item_code': item,
            'selling': 1 
        },
        [
            'price_list_rate'
        ])
        return item_price

def create_invoice(self):
    company = frappe.get_doc('Company', self.company)
    if self.order_type == 'Room' and self.is_complimentary == 1:
      remarks = 'Complimentary Room# ' + self.room

      # Creating Sales Invoice 
      create_sales_invoice(self, customer = 'Room Complimentary', company = company, check_in_id=self.check_in_id, remarks= remarks)

    elif self.order_type == 'Room' and self.is_paid == 1:
      remarks = 'POS Room# ' + self.room
      if self.table:
        remarks += ' Table# ' + self.table

      # Creating Sales Invoice 
      create_sales_invoice(self, customer = 'Hotel Walk In Customer', company = company, check_in_id=self.check_in_id, remarks= remarks)
      # Creating Additional Payment vouchers
      create_payment_voucher(self,customer = 'Hotel Walk In Customer', company = company, remarks = remarks )
    elif self.order_type == 'Take Away':
      remarks = 'Take Away '
      if self.room:
        remarks += 'Room# ' + self.room
      
      if self.department:
        remarks += 'Department: ' + self.department
      
      # Creating Sales Invoice 
      create_sales_invoice(self, customer = 'Take Away', company = company)
      # Creating Additional Payment vouchers
      create_payment_voucher(self,customer = 'Take Away', company = company, remarks = remarks )

    elif self.order_type == 'Restaurant':
      remarks = 'Restaurant Table# ' + self.table
      # Generate invoice
      create_sales_invoice(self, customer = 'Restaurant Walk In Customer', company = company)
      # Creating Additional Payment vouchers
      create_payment_voucher(self,customer = 'Restaurant Walk In Customer', company = company, remarks = remarks )

    elif self.order_type == 'Staff':
      remarks = 'Staff Entertainment Department: ' + self.department
      # Generate Invoice
      create_sales_invoice(self, customer = 'Staff Entertainment', company = company, remarks= remarks)
    
    elif self.order_type == 'Complimentary':
      remarks = 'Complimentary'
      # Generate Invoice
      create_sales_invoice(self, customer = 'Complimentary', company = company, remarks= remarks)
    



def set_status(self):
    if self.order_type == 'Room' and self.is_paid == 0:
        self.status = 'To Check Out'
        doc = frappe.get_doc('Hotel Food Order', self.name)
        doc.db_set('status', 'To Check Out')

    # elif self.order_type == 'Room' and self.is_complimentary == 1:
    #     self.status = 'Completed'
    #     doc = frappe.get_doc('Hotel Food Order', self.name)
    #     doc.db_set('status', 'Completed')
    
    elif self.order_type == 'Room' and self.is_paid == 1:
        self.status = 'Completed'
        doc = frappe.get_doc('Hotel Food Order', self.name)
        doc.db_set('status', 'Completed')

    elif self.order_type == 'Restaurant':
        self.status = 'Completed'
        doc = frappe.get_doc('Hotel Food Order', self.name)
        doc.db_set('status', 'Completed')
    
    elif self.order_type == 'Take Away':
        self.status = 'Completed'
        doc = frappe.get_doc('Hotel Food Order', self.name)
        doc.db_set('status', 'Completed')
    
    elif self.order_type == 'Staff':
        self.status = 'Completed'
        doc = frappe.get_doc('Hotel Food Order', self.name)
        doc.db_set('status', 'Completed')
    
    elif self.order_type == 'Complimentary':
        self.status = 'Completed'
        doc = frappe.get_doc('Hotel Food Order', self.name)
        doc.db_set('status', 'Completed')


def create_sales_invoice(self, customer, company, check_in_id = None, remarks = None):
    sales_invoice_doc = frappe.new_doc('Sales Invoice')
    sales_invoice_doc.discount_amount = 0
    sales_invoice_doc.customer = customer
    sales_invoice_doc.due_date = frappe.utils.data.today()
    sales_invoice_doc.debit_to = company.default_receivable_account

    if check_in_id:
      sales_invoice_doc.check_in_id = self.check_in_id
      sales_invoice_doc.check_in_date = frappe.get_value('Hotel Check In', self.check_in_id, 'check_in')

    if remarks:
      sales_invoice_doc.remarks = remarks

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
        sales_invoice_doc.append('items', {
            'item_code': item_doc.item_code,
            'item_name': item_doc.item_name,
            'description': item_doc.description,
            'qty': item.qty,
            'uom': item_doc.stock_uom,
            'rate': item.rate,
            'amount': item.amount,
            'income_account': default_income_account
        })
    if self.discount_amount != 0:
        sales_invoice_doc.discount_amount += self.discount_amount
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

        sales_invoice_doc.append('items', {
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

def create_payment_voucher(self, customer, company, remarks):
    payment_entry = frappe.new_doc('Payment Entry')
    payment_entry.payment_type = 'Receive'
    payment_entry.mode_of_payment = 'Cash'
    payment_entry.paid_to = company.default_cash_account
    payment_entry.paid_from = company.default_receivable_account
    payment_entry.party_type = 'Customer'
    payment_entry.party = customer
    payment_entry.received_amount = self.total_amount - self.discount_amount + self.service_charges
    payment_entry.paid_amount = self.total_amount - self.discount_amount + self.service_charges
    payment_entry.remarks = remarks
    payment_entry.insert(ignore_permissions=True)
    payment_entry.submit()
