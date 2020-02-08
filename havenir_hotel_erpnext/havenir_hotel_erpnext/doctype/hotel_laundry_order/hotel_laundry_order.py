# -*- coding: utf-8 -*-
# Copyright (c) 2020, Havenir and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class HotelLaundryOrder(Document):
  def validate(self):
    if self.order_type == 'Room':
      room_doc = frappe.get_doc('Rooms', self.room)
      if room_doc.room_status != 'Checked In' and room_doc.check_in_id == self.check_in_id:
          frappe.throw('Room Status is not Checked In')
        
  def on_submit(self):
    create_invoice(self)
    set_status(self)
  
  def on_cancel(self):
    self.status = "Cancelled"
    doc = frappe.get_doc('Hotel Laundry Order', self.name)
    doc.db_set('status','Cancelled')

def set_status(self):
  if self.order_type == 'Room':
      self.status = 'To Check Out'
      doc = frappe.get_doc('Hotel Laundry Order', self.name)
      doc.db_set('status','To Check Out')
  
  elif self.order_type in ['Hotel', 'Banquet Hall', 'Restaurant', 'Staff']:
      self.status = 'Completed'
      doc = frappe.get_doc('Hotel Laundry Order', self.name)
      doc.db_set('status','Completed')

def create_invoice(self):
    company = frappe.get_doc('Company', self.company)
    if self.order_type == 'Hotel':
      remarks = 'Hotel Room Washing'

      # Creating Sales Invoice 
      create_sales_invoice(self, customer = 'Hotel', company = company, remarks= remarks)
    
    if self.order_type == 'Banquet Hall':
      remarks = 'Banquet Hall Washing'

      # Creating Sales Invoice 
      create_sales_invoice(self, customer = 'Banquet Hall', company = company, remarks= remarks)
    
    if self.order_type == 'Restaurant':
      remarks = 'Restaurant Washing'

      # Creating Sales Invoice 
      create_sales_invoice(self, customer = 'Restaurant', company = company, remarks= remarks)
    
    if self.order_type == 'Staff':
      remarks = 'Staff Washing'

      # Creating Sales Invoice 
      create_sales_invoice(self, customer = 'Staff Entertainment', company = company, remarks= remarks)

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
    sales_invoice_doc.insert(ignore_permissions=True)
    sales_invoice_doc.submit()