# -*- coding: utf-8 -*-
{
    'name': "ticket_extended",

    'summary': """
        Additional fields for tickets""",

    'description': """
        Long description of module's purpose
    """,

    'author': "XIBIX",
    'website': "https://odoo.xibix.de",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk', 'website_helpdesk_form'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/new_fields.xml',
    ]
}