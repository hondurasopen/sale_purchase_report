# -*- encoding: utf-8 -*-
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime


class ForecastFacturaslinePos(models.TransientModel):
    _name = 'invoice.line.report'
    _description = 'Lineas de Facturas de Clientes'
    _order = 'date_order asc'

    treasury_id = fields.Many2one("treasury.forecast", "Forecast")
    invoice_id = fields.Many2one("account.invoice", "Factura")
    date_order = fields.Date("Fecha de Factura")
    product_id = fields.Many2one("product.product", "Producto")
    name = fields.Char("Nombre del Producto")
    partner_id = fields.Many2one("res.partner", string="Cliente")
    total_amount = fields.Float(string="Total",
                                digits_compute=dp.get_precision('Account'))
    qty = fields.Float("Cantidad")


class AccountTreasuryForecastLine(models.TransientModel):
    _name = 'treasury.forecast.line'
    _description = 'Cadena de Suministro'
    _rec_name = 'start_date'

    def get_currency(self):
        return self.env.user.company_id.currency_id.id

    currency_id = fields.Many2one("res.currency", "Moneda", domain=[('active', '=', True)], default=get_currency)
    name = fields.Char(string="Description")
    total_incoming = fields.Float(string="Total de Ventas", readonly=True, help="Totales de las facturas de clientes")
    partner_id = fields.Many2one("res.partner", "Cliente", domain=[('customer', '=', True)])
    #Borrar
    state = fields.Selection([('draft','Borrador'),('progress','Progreso'),('done','Finalizado')], string='Estado',default='draft')
    start_date = fields.Date(string="Fecha de Inicio", required=True)
    end_date = fields.Date(string="Fecha Final", required=True)
    check_draft = fields.Boolean(string="Borrador")
    check_proforma = fields.Boolean(string="Esperando Aprobación")
    check_done = fields.Boolean(string="Pagadas", default=1)
    check_open = fields.Boolean(string="Abiertas", default=1)
    out_invoice_ids = fields.One2many("invoice.line.report", "treasury_id", "Productos")
    total_unidades = fields.Float("Unidades Vendidas", readonly=True)

    @api.one
    @api.constrains('end_date', 'start_date')
    def check_date(self):
        if self.start_date > self.end_date:
            raise exceptions.Warning(
                _('Error!:: End date is lower than start date.'))

    @api.one
    @api.constrains('check_draft', 'check_proforma', 'check_open')
    def check_filter(self):
        if not self.check_draft and not self.check_proforma and not self.check_open and not self.check_done:
            raise exceptions.Warning(_('Error!:: There is no any filter checked.'))

    @api.one
    def restart(self):
        if self.out_invoice_ids:
            for invs in self.out_invoice_ids:
                invs.unlink()
        return True

    @api.multi
    def button_calculate(self):
        self.restart()
        self.calculate_invoices()
        self.calculate_total()


    def calculate_total(self):
        if self.out_invoice_ids:
            saldo = 0.0
            amount = 0.0
            unidades = 0.0
            for line in self.out_invoice_ids:
                amount += line.total_amount
                unidades += line.qty

            #POS HOTSALE
            self.total_unidades = unidades
            self.total_incoming = amount


    @api.one
    def calculate_invoices(self):
        invoice_obj = self.env['account.invoice']
        treasury_invoice_obj = self.env['invoice.line.report']
        state = []
        self.total_incoming = 0
        if self.check_open:
            state.append("open")
        if self.check_done:
            state.append("paid")
        invoice_ids = False
        if self.partner_id:
            invoice_ids = invoice_obj.search([('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date), 
            ('type', '=','out_invoice'), ('partner_id', '=', self.partner_id.id), ('state', 'in', tuple(state))])
        else:
            invoice_ids = invoice_obj.search([('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date), ('type', '=','out_invoice'), ('state', 'in', tuple(state))])
        for invoice_o in invoice_ids:
            for line in invoice_o.invoice_line_ids:
                values = {
                    'treasury_id': self.id,
                    'invoice_id': line.invoice_id.id,
                    'date_order': line.invoice_id.date_invoice,
                    'partner_id': line.invoice_id.partner_id.id,
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'qty': line.quantity,
                    'total_amount': line.price_subtotal,
                }
                new_id = treasury_invoice_obj.create(values)
        return True



    @api.multi
    def action_draft(self):
        self.write({'state' : 'draft'})

    @api.multi
    def action_progress(self):
        self.write({'state':'progress'})

    @api.multi
    def action_done(self):
        self.write({'state':'done'})

