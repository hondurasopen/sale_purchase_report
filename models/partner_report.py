# -*- encoding: utf-8 -*-
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime


class ForecastFacturaslinePos(models.TransientModel):
    _name = 'forecast.partner.sale.order'
    _description = 'Facturas por Clientes'
    _order = 'date_order asc'

    name = fields.Char("Sale Order")
    date_order = fields.Date("Date Order")
    partner_id = fields.Many2one("res.partner", string="Customer")
    total_amount = fields.Float(string="Total Amount",
                                digits_compute=dp.get_precision('Account'))
    state_order = fields.Selection([('invoiced', 'Fully Invoiced'), ('to invoice', 'Pending to Invoicing'), ('no', 'Pending to delivery order')], string="Order State")
    #delivery_id = fields.Many2one("stock.picking", "Delivery", domain=[('state', '!=', 'cancel')])
    delivery_id = fields.Char("Delivery")
    invoice_id = fields.Many2one("account.invoice", "Factura")
    guia_rem = fields.Char("Guia de remisión")
    state_delivery = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting Another Operation'), ('confirmed', 'Waiting Availability'), ('partially_available', 'Partially Availability'), ('assigned', 'Available'), ('done', 'Done')], string="Dilvery State")
    numero_paquetes = fields.Integer("Número de paquetes")