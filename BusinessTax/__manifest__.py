{
    "name": "BusinessTax",
    "version": "1.0", 
    "depends": [
        'base',
        'web',
        'mail',
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
    "views/BusinessTax_Basic_views.xml",
    "views/BusinessTax_Method_views.xml",
     "views/BusinessTax_Profix_views.xml",
    "views/BusinessTax_Year_views.xml",
"views/BusinessTax_Period_views.xml",
"views/BusinessTax_Profix_Type_views.xml",
"views/BusinessTax_Certificate_Category_views.xml",
"views/BusinessTax_Status_views.xml",
"views/BusinessTax_Vat_Declare_Code_views.xml",
"views/BusinessTax_Type_views.xml",
"views/BusinessTax_Tax_Code_Type_views.xml",
"views/BusinessTax_Declare_Deduction_views.xml",
"views/BusinessTax_Through_Custom_views.xml",
"views/BusinessTax_Declare_Type_views.xml",
"views/BusinessTax_HD_Type_views.xml",
"views/BusinessTax_Book_views.xml",
"views/BusinessTax_Invoice_views.xml",
"views/BusinessTax_Purchase_views.xml",
"views/BusinessTax_Vat_Declare_Mapping_views.xml",
"views/BusinessTax_Output_TextFile_views.xml",
"data/BusinessTax_Config_Data.xml",
    ],   
'license': 'AGPL-3',
	'installable': True,
	'application': False,
	'auto_install': False,
}