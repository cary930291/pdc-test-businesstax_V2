# -*- coding: utf-8 -*-
{
    'name': "hr_expense_inherit",

    'summary': """
    费用模块扩展
        """,

    'description': """
        1,添加审核
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_expense', 'base_approval'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/rules.xml',
        # 'wizard/hr_expense_sheet_wizard.xml',
        # 'report/advance_payment_report_template.xml',
        # 'report/hr_expense_sheet_report.xml',
        # 'wizard/account_advance_payment_wizard.xml',

        # 'data/sequence.xml',
        # 'views/assets.xml',
        # 'views/hide_menu.xml',
        'views/data.xml',
        'views/hr_expense_views.xml',
        'views/hr_expense_sheet.xml',
        # 'views/account_advance_payment_view.xml',
        # 'views/hr_employee.xml',
        # 'views/sale_order.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': ['static/src/xml/*.xml']

}
