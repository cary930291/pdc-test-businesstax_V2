{
    "name": "Expense inherit",
    "version": "1.0", 
    "depends": [
        'base',
        'web',
        'mail',
        'hr_expense',
        'hr'
    ], 
    "author": "Eric Tang",
    "website": "",
    "category": "Test",
    "description": """\

Features
======================================================================
 'installable': True,
    'auto_install': False,
* 

""",
 "data": [
            "security/ir.model.access.csv",
            "views/hr_department_view_inherit.xml",
            "views/hr_expense_mapping_view.xml"
    ],   
'license': 'AGPL-3',
	'installable': True,
	'application': False,
	'auto_install': False,
}