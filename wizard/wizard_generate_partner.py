# -*- encoding: utf-8 -*-
import odoo.addons.decimal_precision as dp
from odoo import models, fields, api, exceptions, _
from datetime import date, datetime


class PartnerTreasuryForecast(models.TransientModel):
    _name = 'treasury.forecast.partner'
    _description = 'Detalle de facturas'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    @api.one
    @api.constrains('end_date', 'start_date')
    def check_date(self):
        if self.start_date > self.end_date:
            raise exceptions.Warning(
                _('Error!:: End date is lower than start date.'))

    @api.multi
    def delete_sale(self):
        treasury_sale_order_obj = self.env['forecast.partner.sale.order'].search([('id', '!=', 0)])
        for picking in treasury_sale_order_obj:
            picking.unlink()

    @api.multi
    def button_calculate(self):
        self.delete_sale()
        self.calculate_sale_order()
        self.ensure_one()
        ctx = dict(self._context)

        action = self.env['ir.model.data'].xmlid_to_object('treasury_forecast.action_forecast_partner')
        if not action:
            action = {
                'view_type': 'tree',
                'view_mode': 'tree,graph,pivot',
                'res_model': 'forecast.partner',
                'type': 'ir.actions.act_window',
                'domain': [],
            }
        else:
            action = action[0].read()[0]
        action['name'] = _('Sale Order')
        action['context'] = ctx
        return action

    @api.one
    def calculate_sale_order(self):
        sale_order_obj = self.env['sale.order']
        treasury_sale_order_obj = self.env['forecast.partner.sale.order']
        state = []
        state.append("sale")
        state.append("done")
        sale_ids = sale_order_obj.search([('date_order', '>=', self.start_date), ('date_order', '<=', self.end_date), ('state', 'in', tuple(state))])
        for order_o in sale_ids:
            values = {
                'name': order_o.name,
                'date_order': order_o.date_order,
                'partner_id': order_o.partner_id.id,
                'total_amount': order_o.amount_total,
                'state_order': order_o.invoice_status,
                'invoice_id': order_o.invoice_ids.id,
            }
            for delivery in order_o.picking_ids:
                if delivery.state != 'cancel':
                    values["delivery_id"] = delivery.name
                    values["state_delivery"] = delivery.state
                    values["guia_rem"] = delivery.carrier_tracking_ref
                    values["numero_paquetes"] = delivery.number_of_packages
            new_id = treasury_sale_order_obj.create(values)

        return True
