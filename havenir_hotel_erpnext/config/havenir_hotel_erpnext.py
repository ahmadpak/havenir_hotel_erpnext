from __future__ import unicode_literals
import frappe
from frappe import _


def get_data():
    return[
        {
            "label": _("Rooms Management"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Rooms",
                    "label": _("Rooms"),
                    "description": _("Create new rooms"),
                    "onboard": 1,
                },

                {
                    "type": "doctype",
                    "name": "Room Type",
                    "label": _("Room Type"),
                    "description": _("Create new Room Type"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Room Facility Type",
                    "label": _("Room Facilty Type"),
                    "description": _("Create new Room Facility Type"),
                    "onboard": 1,
                },
            ]
        },
        {
            "label": _("Guest Stay"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Hotel Check In",
                    "label": _("Hotel Check In"),
                    "description": _("Create new Hotel Check In"),
                    "onboard": 1,
                },

                {
                    "type": "doctype",
                    "name": "Hotel Check Out",
                    "label": _("Hotel Check Out"),
                    "description": _("Create new Hotel Check Out"),
                    "onboard": 1,
                },

                {
                    "type": "doctype",
                    "name": "Hotel Guests",
                    "label": _("Hotel Guests"),
                    "description": _("Create new Hotel Guests"),
                    "onboard": 1,
                },

                {
                    "type": "doctype",
                    "name": "Hotel Payment Entry",
                    "label": _("Hotel Payment Entry"),
                    "description": _("Create new Hotel Payment Entry"),
                    "onboard": 1,
                },
            ]
        },
        {
            "label": _("Orders"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Hotel Food Order",
                    "label": _("Hotel Food Order"),
                    "description": _("Create new Hotel Food Order"),
                    "onboard": 1,
                },

                {
                    "type": "doctype",
                    "name": "Restaurant Tables",
                    "label": _("Restaurant Tables"),
                    "description": _("Create Restaurant Tables"),
                    "onboard": 1,
                },
                
                {
                    "type": "doctype",
                    "name": "Hotel Laundry Order",
                    "label": _("Hotel Laundry Order"),
                    "description": _("Create new Hotel Laundry Order"),
                    "onboard": 1,
                },
                
            ]
        },
        {
            "label": _("Settings"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Hotel Management Settings",
                    "label": _("Hotel Management Settings"),
                    "description": _("Create Hotel Management Settings"),
                    "onboard": 1,
                }
            ]
        }
    ]
