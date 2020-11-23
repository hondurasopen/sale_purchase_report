# -*- encoding: utf-8 -*-
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime


class Productsmargin(models.TransientModel):
    _name = 'bi.producto.ventas'
    _description = 'Productos'
    _order = 'ventas_neta desc'

    treasury_id = fields.Many2one("bi.producto.sale", "Forecast")
    product_id = fields.Many2one("product.product", "Product")
    units_sold = fields.Float("Unidades Vendidas")
    ventas_neta = fields.Float("Total de Ventas")



class AccountTreasuryForecast(models.TransientModel):
    _name = 'bi.producto.sale'
    _description = 'Ventas Clientes'

    def get_currency(self):
        return self.env.user.company_id.currency_id.id

    currency_id = fields.Many2one("res.currency", "Moneda", domain=[('active', '=', True)], default=get_currency)
    name = fields.Char(string="Description", default="Ventas")

    #Borrar
    state = fields.Selection([('draft','Draft'),('progress','Progress'),('done','Done')], string='State',default='draft')
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    product_ids = fields.One2many("bi.producto.ventas", "treasury_id", "Products")


    total_qty = fields.Float("Unidades Vendidas", readonly=True)
    total_incoming = fields.Float(string="Total Ventas", readonly=True)



    @api.one
    @api.constrains('end_date', 'start_date')
    def check_date(self):
        if self.start_date > self.end_date:
            raise exceptions.Warning(
                _('Error!:: End date is lower than start date.'))

    @api.one
    def restart(self):
        if self.product_ids:
            for products in self.product_ids:
                products.unlink()
        return True

    @api.multi
    def button_calculate(self):
        self.restart()
        self.get_product()
        self.calculate_total()


    @api.one
    def get_product(self):
        obj_product = self.env["product.product"].search([('sale_ok', '=', True)])
        obj_forecast_product = self.env["bi.producto.ventas"] 
        for product in obj_product:
            value = {
                'product_id': product.id,
                'treasury_id': self.id,
            }
            id_forecast_prod = obj_forecast_product.create(value)

            if id_forecast_prod:
                invoice_ids = self.env["account.invoice.line"].search([('invoice_id.state', 'not in', ['draft', 'cancel']), ('invoice_id.date_invoice', '>=', self.start_date), 
                    ('invoice_id.date_invoice', '<=', self.end_date), ('invoice_id.type', '=', 'out_invoice'), ('product_id', '=', product.id)]) 

                ventas = 0.0
                unidades = 0.0
                for bi_product in invoice_ids:
                    ventas += (bi_product.price_subtotal)
                    unidades += bi_product.quantity

                id_forecast_prod.ventas_neta = ventas 
                id_forecast_prod.units_sold = unidades    


    def calculate_total(self):
        if self.product_ids:
            amount = 0.0
            unidades = 0.0
            for line in self.product_ids:
                amount += line.ventas_neta
                unidades += line.units_sold

            #POS HOTSALE
            self.total_qty = unidades
            self.total_incoming = amount



    @api.multi
    def action_draft(self):
        self.write({'state' : 'draft'})

    @api.multi
    def action_progress(self):
        self.write({'state':'progress'})

    @api.multi
    def action_done(self):
        self.write({'state':'done'})

