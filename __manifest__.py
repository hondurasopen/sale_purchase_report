# -*- encoding: utf-8 -*-
##############################################################################

{
    "name": "Analisis y reporte de empresas",
    "depends": [
        "product",
        "sale",
        "account",
        "purchase",
    ],
    "author": "César Alejandro Rodriguez, Honduras",
    "category": "Accounting",
    "description": """
       Wizard para reporteria de ventas, compras e inventario.
    """,
    'data': [
        'security/groups.xml',
        #'security/ir.model.access.csv',
        "views/cadena_suministro_view.xml",
        "views/partner_view.xml",
        "views/Ventas_linea.xml",
        "views/compra_linea.xml",
        #"wizard/wizard_generate_detail.xml",
        "views/product_ventas.xml",
        "views/product_category.xml",
    ],
    'demo': [],
    'installable': True,
}
