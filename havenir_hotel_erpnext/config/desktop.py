# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "module_name": "Havenir Hotel Management",
            "category": "Modules",
            "label": _("Hotel Management"),
            "color": "blue",
            "icon": "octicon octicon-calendar",
            "type": "module",
            "onboard_present": 1
        }
    ]
