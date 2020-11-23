# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _

class ProductCategory(models.Model):
    _inherit = 'product.category'

    category_landed_cost = fields.Boolean("Categoria Importaciones")

