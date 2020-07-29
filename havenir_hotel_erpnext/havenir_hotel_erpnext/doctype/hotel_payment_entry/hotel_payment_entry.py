# -*- coding: utf-8 -*-
# Copyright (c) 2020, Havenir and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.core.doctype.sms_settings.sms_settings import send_sms

class HotelPaymentEntry(Document):
  def before_submit(self):
    self.create_payment_entry()
  
  def on_submit(self):
    pass
    # send_payment_sms(self)
  
  def get_room_details(self):
    check_in_id = frappe.get_value('Rooms',self.room,'check_in_id')
    check_in_doc = frappe.get_doc('Hotel Check In',check_in_id)
    result = [check_in_doc.guest_id,check_in_doc.guest_name,check_in_doc.name, check_in_doc.contact_no]
    return result

  def get_advance_payments(self):
    hotel_payment_vouchers = frappe.get_list('Hotel Payment Entry', filters = {
      'room': self.room,
      'check_in_id': self.check_in_id,
      'guest_id': self.guest_id,
      'docstatus': 1
    }, fields=['name', 'entry_type','amount_paid'])

    total_advance = 0 
    for payments in hotel_payment_vouchers:
      if payments.entry_type == 'Receive':
        total_advance += payments.amount_paid
      else:
        total_advance -= payments.amount_paid
    
    return total_advance    

  def create_payment_entry(self):
    company = frappe.get_doc('Company',self.company)
    if self.entry_type == 'Receive':
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
    
    else:
      total_advance = self.get_advance_payments()
      self.advance = total_advance
      
      if self.amount_paid <= total_advance:
        #  Creating JV for Refund
        jv = frappe.new_doc('Journal Entry')
        jv.voucher_type = 'Journal Entry'
        jv.naming_series = 'ACC-JV-.YYYY.-'
        jv.posting_date = frappe.utils.data.today()
        jv.company = self.company
        jv.user_remark = 'Refund for Room {} Check In ID: {}'.format( self.room, self.check_in_id)


        # Entry For Hotel Walk In Customer
        jv.append('accounts', {
                  'account': company.default_receivable_account,
                  'party_type': 'Customer',
                  'party': 'Hotel Walk In Customer',
                  'debit_in_account_currency': self.amount_paid
              })
        # Entry For Cash Account
        jv.append('accounts', {
                  'account': company.default_cash_account,
                  'credit_in_account_currency': self.amount_paid
              })
        
        jv.insert(ignore_permissions=True)
        jv.submit()
      
      else:
        frappe.throw('Cannot refund more than advance amount')
  
  def send_payment_sms(self):
    sms_settings = frappe.get_doc('SMS Settings')
    if sms_settings.sms_gateway_url:
      msg = 'Dear '
      msg += self.guest_name
      msg += ',\nThank you for your payment. Amount received PKR '
      msg += str(self.amount_paid)
      msg += ' on '
      msg += str(self.posting_date)
      send_sms([self.contact_no], msg = msg)