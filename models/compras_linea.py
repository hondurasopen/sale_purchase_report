# -*- encoding: utf-8 -*-
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime


class ForecastPurchase(models.TransientModel):
    _name = 'forecast.purchase.line'
    _description = 'Lineas de Compras de Productos'
    _order = 'date_order asc'

    treasury_id = fields.Many2one("treasury.forecast", "Forecast")
    order_id = fields.Many2one("purchase.order", string="Purchase Order")
    date_order = fields.Date("Order Date")
    product_id = fields.Many2one("product.product", "Producto")
    name = fields.Char("Product Name")
    partner_id = fields.Many2one("res.partner", string="Supplier")
    total_amount = fields.Float(string="Total",
                                digits_compute=dp.get_precision('Account'))
    precio_compra = fields.Float("Unit Price")
    qty = fields.Float("Cantidad")
    currency_id = fields.Many2one("res.currency", "Currency", domain=[('active', '=', True)])

class AccountTreasuryForecastLine(models.TransientModel):
    _name = 'treasury.forecast.purchase'
    _description = 'Purchases Lines'

    def get_currency(self):
        return self.env.user.company_id.currency_id.id

    currency_id = fields.Many2one("res.currency", "Moneda", domain=[('active', '=', True)], default=get_currency)
    name = fields.Char(string="Purchasing analysis", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    purchase_ids = fields.One2many("forecast.purchase.line", "treasury_id", "Purchase Detail")
    num_purchase = fields.Float("# Purchases", readonly=True)
    check_open = fields.Boolean("Purchases Done", default=True)
    check_done = fields.Boolean("Purchases Confirmed", default=True)

    @api.one
    @api.constrains('end_date', 'start_date')
    def check_date(self):
        if self.start_date > self.end_date:
            raise exceptions.Warning(
                _('Error!:: End date is lower than start date.'))

    @api.one
    def restart(self):
        if self.out_purchase_ids:
            for invs in self.out_purchase_ids:
                invs.unlink()
        return True

    @api.multi
    def button_calculate(self):
        self.restart()

