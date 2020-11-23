# -*- encoding: utf-8 -*-
##############################################################################

{
    "name": "Analisis de Ventas",
    "depends": [
        "product",
        "sale",
        "account",
        "purchase",
        "sale_margin",
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
    ],
    'demo': [],
    'installable': True,
}
