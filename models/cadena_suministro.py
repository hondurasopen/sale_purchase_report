# -*- encoding: utf-8 -*-
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime


class ForecastCategorias(models.TransientModel):
    _name = "forecast.category"
    _order = 'total_venta desc'

    name = fields.Many2one("product.category", "Categoria")
    total_venta = fields.Float("Total de Ventas")
    unidades = fields.Float("Total Unidades")
    treasury_id = fields.Many2one("treasury.forecast", "Forecast")
    porcentaje_venta = fields.Float("% Total Ventas")

class ForecastFacturas(models.TransientModel):
    _name = 'forecast.product'
    _description = 'Productos'
    _order = 'total_venta desc, porcentaje_sale desc'

    treasury_id = fields.Many2one("treasury.forecast", "Forecast")
    product_id = fields.Many2one("product.product", "Producto")
    unidades = fields.Float("Total Unidades")
    total_venta = fields.Float("Total de Ventas")
    porcentaje_sale = fields.Float("Ventas %")
    porcentaje_unidades = fields.Float("Producto %")
    category_id = fields.Many2one("product.category", "Categoria")
    qty = fields.Float("Inventario Actual")

class ForecastFacturas(models.TransientModel):
    _name = 'forecast.invoice'
    _description = 'Facturas de Clientes'
    _order = 'invoice_date asc'

    treasury_id = fields.Many2one("treasury.forecast","Forecast")
    invoice_id = fields.Many2one("account.invoice", string="No. Factura")
    invoice_date = fields.Date("Fecha de Factura")
    date_due = fields.Date(string="Fecha de Vencimiento")
    partner_id = fields.Many2one("res.partner", string="Cliente")
    state = fields.Selection([('draft', 'Borrador'), ('proforma', 'Pro-forma'),
                              ('proforma2', 'Pro-forma'), ('open', 'Abierta'),
                              ('paid', 'Pagada'), ('cancel', 'Cancelada')],
                             string="State")

    total_amount = fields.Float(string=" Total Factura", digits_compute=dp.get_precision('Account'))
    subtotal = fields.Float("SubTotal", digits_compute=dp.get_precision('Account'))
    isv = fields.Float(string="ISV", digits_compute=dp.get_precision('Account'))
    residual_amount = fields.Float(string="Saldo Pendiente", digits_compute=dp.get_precision('Account'))
    utilidad = fields.Float(string="Utilidad por factura",
                                   digits_compute=dp.get_precision('Account'))
    costo = fields.Float("Totol Costo")


class AccountTreasuryForecast(models.TransientModel):
    _name = 'treasury.forecast'
    _description = 'Cadena de Suministro'
    _rec_name = 'start_date'

    def get_currency(self):
        return self.env.user.company_id.currency_id.id

    currency_id = fields.Many2one("res.currency", "Moneda", domain=[('active', '=', True)], default=get_currency)
    name = fields.Char(string="Description")
    total_incoming = fields.Float(string="Total Ventas Brutas", readonly=True, help="Totales de las facturas de clientes")
    #Borrar
    state = fields.Selection([('draft','Borrador'),('progress','Progreso'),('done','Finalizado')], string='Estado',default='draft')
    start_date = fields.Date(string="Fecha de Inicio", required=True)
    end_date = fields.Date(string="Fecha Final", required=True)
    check_draft = fields.Boolean(string="Borrador")
    check_proforma = fields.Boolean(string="Esperando Aprobación")
    check_done = fields.Boolean(string="Pagadas", default=1)
    check_open = fields.Boolean(string="Abiertas", default=1)
    out_invoice_ids = fields.One2many("forecast.invoice", "treasury_id", "Facturas de Clientes")

    product_forecast_ids = fields.One2many("forecast.product", "treasury_id", "Venta de Productos")
    category_ids = fields.One2many("forecast.category", "treasury_id", "Categorias de Productos")

    total_costo = fields.Float("Total Costos", readonly=True)
    total_isv = fields.Float("Total Impuesto", readonly=True)
    utilidad_bruta = fields.Float("Utilidad Bruta", readonly=True)

    total_ventas_may = fields.Float("Ventas Netas", readonly=True)
    count_facturas =  fields.Integer("# Facturas", readonly=True)

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
        if self.product_forecast_ids:
            for prods in self.product_forecast_ids:
                prods.unlink()
        if self.category_ids:
            for categ in self.category_ids:
                categ.unlink()
        return True

    @api.multi
    def button_calculate(self):
        self.restart()
        self.calculate_invoices()
        self.get_product()
        self.getcategorias()
        self.calculate_total()


    @api.one
    def getcategorias(self):
        categ_id = self.env["product.category"].search([('id', '>=', 0)])
        obj_forecast_categ = self.env["forecast.category"]
        obj_forecast_product = self.env["forecast.product"].search([('treasury_id', '=', self.id)])
        for categ in categ_id:
            value = {
                'name': categ.id,
                'treasury_id': self.id,
            }
            id_forecast_categ = obj_forecast_categ.create(value)
            if id_forecast_categ:
                sum_line = 0.0
                qty = 0.0
                for forecast in obj_forecast_product:
                    if categ.id == forecast.category_id.id:
                        sum_line += forecast.total_venta
                        qty += forecast.unidades
                id_forecast_categ.write({'total_venta': sum_line, 'unidades': qty})

    @api.one
    def get_product(self):
        obj_product = self.env["product.product"].search([('sale_ok', '=', True)])
        obj_forecast_product = self.env["forecast.product"]
        treasury_invoice_obj = self.env['forecast.invoice'].search([('treasury_id', '=', self.id)])
        for product in obj_product:
            value = {
            'product_id': product.id,
            'treasury_id': self.id,
            'category_id': product.categ_id.id,
            'qty': product.qty_available,
                }
            id_forecast_prod = obj_forecast_product.create(value)
            if id_forecast_prod:
                sum_line = 0.0
                qty = 0.0
                for forecast in treasury_invoice_obj:
                    for line in forecast.invoice_id.invoice_line_ids:
                        if line.product_id.id == product.id:
                            sum_line += line.price_subtotal
                            qty += line.quantity
                id_forecast_prod.write({'total_venta': sum_line, 'unidades': qty})


    def calculate_total(self):
        if self.out_invoice_ids:
            saldo = 0.0
            amount = 0.0
            costo = 0.0
            unidades = 0.0
            contador = 0.0
            isv = 0.0
            net = 0.0
            for line in self.out_invoice_ids:
                saldo += line.residual_amount
                amount += line.total_amount
                costo += line.costo
                contador += 1
                net += line.subtotal
                isv += line.isv
            self.total_ventas_may = net
            self.total_isv = isv
            self.count_facturas = contador
            self.total_incoming = amount
            self.total_costo = costo
            self.utilidad_bruta = self.total_incoming - self.total_costo -self.total_isv
            for line in self.category_ids:
                if self.total_ventas_may > 0:
                    line.porcentaje_venta = (line.total_venta / self.total_ventas_may) * 100
            for line in self.product_forecast_ids:
                if self.total_ventas_may > 0:
                    line.porcentaje_sale = (line.total_venta / self.total_ventas_may) * 100

    @api.one
    def calculate_invoices(self):
        invoice_obj = self.env['account.invoice']
        treasury_invoice_obj = self.env['forecast.invoice']
        state = []
        self.total_incoming = 0
        self.total_invoice_out = 0
        if self.check_open:
            state.append("open")
        if self.check_done:
            state.append("paid")
        invoice_ids = invoice_obj.search([('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date), ('type', '=','out_invoice'), ('state', 'in', tuple(state))])
        pedido_ventas_id = False
        for invoice_o in invoice_ids:
            values = {
                'treasury_id': self.id,
                'invoice_id': invoice_o.id,
                'isv': invoice_o.amount_tax,
                'subtotal': invoice_o.amount_untaxed,
                'date_due': invoice_o.date_due,
                'invoice_date': invoice_o.date_invoice,
                'partner_id': invoice_o.partner_id.id,
                'state': invoice_o.state,
                'total_amount': invoice_o.amount_total,
                'residual_amount': invoice_o.residual,
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

