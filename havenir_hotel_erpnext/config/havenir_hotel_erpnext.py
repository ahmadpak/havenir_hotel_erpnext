from __future__ import unicode_literals
import frappe
from frappe import _


def get_data():
    return[
        {
            "label": _("Rooms"),
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
                }
            ]
        },
    ]
