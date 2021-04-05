# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError


class account_move(models.Model):
    _inherit = 'account.move'
   
    def calc_discount(self):
        for calculate in self:
            calculate._calculate_discount()

    @api.depends('discount_amount')
    def _calculate_discount(self):
        res = discount = 0.0
        for self_obj in self:
            if self_obj.discount_type == 'global':
                if self_obj.discount_method == 'fix':
                    res = self_obj.discount_amount
                elif self_obj.discount_method == 'per':
                    res = self_obj.amount_untaxed * (self_obj.discount_amount/ 100)
            else:
                res = discount
        return res

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state','discount_method','discount_amount')
    def _compute_amount(self):
        move_ids = [move.id for move in self if move.id and move.is_invoice(include_receipts=True)]
        self.env['account.payment'].flush(['state'])
        if move_ids:
            self._cr.execute(
                '''
                    SELECT move.id
                    FROM account_move move
                    JOIN account_move_line line ON line.move_id = move.id
                    JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                    JOIN account_move_line rec_line ON
                        (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                        OR
                        (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                    JOIN account_payment payment ON payment.id = rec_line.payment_id
                    JOIN account_journal journal ON journal.id = rec_line.journal_id
                    WHERE move.state IN ('posted')
                    AND move.id IN %s
                ''', [tuple(move_ids)]
            )
            in_payment_set = set(res[0] for res in self._cr.fetchall())
        else:
            in_payment_set = {}

        for move in self:
            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = set()

            for line in move.line_ids:
                if line.currency_id:
                    currencies.add(line.currency_id)

                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            if move.state == 'posted':
                posted_total = move.amount_total
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.type == 'entry' else -total
            move.amount_residual_signed = total_residual
            res = move._calculate_discount()
            move.discount_amt = res
            move.amount_total = move.amount_untaxed - res + move.amount_tax

            currency = len(currencies) == 1 and currencies.pop() or move.company_id.currency_id
            is_paid = currency and currency.is_zero(move.amount_residual) or not move.amount_residual

            # Compute 'payment_state'.
            if move.type == 'entry':
                move.payment_state = False
            elif move.state == 'posted' and is_paid:
                if move.id in in_payment_set:
                    move.payment_state = 'in_payment'
                else:
                    move.payment_state = 'paid'
            else:
                move.payment_state = 'not_paid'

        res_config= self.env['res.config.settings'].search([],order="id desc", limit=1)
        if res_config:
            for rec in self:
                if res_config.tax_discount_policy == 'tax':
                    if rec.discount_type == 'line':
                        rec.discount_amt = 0.00
                        total = 0
                        if self._context.get('default_type') == 'out_invoice' :
                            if rec.discount_amount_line > 0.0:
                                rec.discount_amt_line = rec.discount_amount_line
                        rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt_line
            
                    elif rec.discount_type == 'global':
                        if rec.discount_method == 'fix':
                            rec.discount_amt = rec.discount_amount
                            rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt
                        elif rec.discount_method == 'per':
                            rec.discount_amt = (rec.amount_untaxed) * (rec.discount_amount / 100.0)
                            rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt
                        else:
                            rec.amount_total = rec.amount_tax + rec.amount_untaxed
                    else:
                        rec.amount_total = rec.amount_tax + rec.amount_untaxed
                elif res_config.tax_discount_policy == 'untax':
                    sums = 0.00
                    if rec.discount_type == 'line':
                        total = 0
                        if self._context.get('default_type') == 'out_invoice' :
                            if rec.discount_amount_line > 0.0:
                                rec.discount_amt_line = rec.discount_amount_line

                        rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt_line        
                        rec.discount_amt = 0.00   
                    elif rec.discount_type == 'global':
                        if rec.discount_method == 'fix':
                            if rec.invoice_line_ids:
                                for line in rec.invoice_line_ids:
                                    if line.tax_ids:
                                        if rec.amount_untaxed:
                                            final_discount = ((rec.discount_amt*line.price_subtotal)/rec.amount_untaxed)
                                            discount = line.price_subtotal - final_discount
                                            taxes = line.tax_ids.compute_all(discount, rec.currency_id, 1.0,
                                                                            line.product_id,rec.partner_id)
                                            sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            rec.amount_total = sums + rec.amount_untaxed - rec.discount_amt
                            rec.amount_tax = sums
                    
                        elif rec.discount_method == 'per':
                            if rec.invoice_line_ids:
                                for line in rec.invoice_line_ids:
                                    if line.tax_ids:
                                        final_discount = ((rec.discount_amount*line.price_subtotal)/100.0)
                                        discount = line.price_subtotal - final_discount
                                        taxes = line.tax_ids.compute_all(discount, rec.currency_id, 1.0,
                                                                        line.product_id,rec.partner_id)
                                        sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                        
                            rec.amount_total = sums + rec.amount_untaxed - rec.discount_amt
                            rec.amount_tax = sums
                        else:
                            rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt    
                    else:
                        rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt
                else:
                    rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.discount_amt    

                for record in self:
                    for line in record.invoice_line_ids:
                        if line.product_id:
                            rec.discount_account_id = line.account_id.id 
        for move_items in self:
            if move_items.state == 'posted':
                move_items.update({'amount_total': posted_total })                       

    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')],'Discount Method')
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Float(string='- Discount', readonly=True, compute='_compute_amount')
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, tracking=True,
        compute='_compute_amount')
    amount_tax = fields.Monetary(string='Tax', store=True, readonly=True,
        compute='_compute_amount')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True,
        compute='_compute_amount',
        inverse='_inverse_amount_total')
    
    discount_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')], 'Discount Applies to',default='global')
    discount_account_id = fields.Many2one('account.account', 'Discount Account',compute='_compute_amount',store=True)
    discount_amt_line = fields.Float(compute='_compute_amount', string='- Line Discount', digits='Discount', store=True, readonly=True)
    discount_amount_line = fields.Float(string="Discount Line")
   
    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        ''' Compute the dynamic tax lines of the journal entry.

        :param lines_map: The line_ids dispatched by type containing:
            * base_lines: The lines having a tax_ids set.
            * tax_lines: The lines having a tax_line_id set.
            * terms_lines: The lines generated by the payment terms of the invoice.
            * rounding_lines: The cash rounding lines of the invoice.
        '''
        self.ensure_one()
        in_draft_mode = self != self._origin

        def _serialize_tax_grouping_key(grouping_dict):
            ''' Serialize the dictionary values to be used in the taxes_map.
            :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
            :return: A string representing the values.
            '''
            return '-'.join(str(v) for v in grouping_dict.values())

        def _compute_base_line_taxes(base_line):
            ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
            amount_currency & balance could not be the same as the expected currency rate.
            The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
            :param base_line:   The account.move.line owning the taxes.
            :return:            The result of the compute_all method.
            '''
            move = base_line.move_id

            if move.is_invoice(include_receipts=True):
                sign = -1 if move.is_inbound() else 1
                quantity = base_line.quantity
                if base_line.currency_id:
                    price_unit_foreign_curr = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
                    price_unit_comp_curr = base_line.currency_id._convert(price_unit_foreign_curr, move.company_id.currency_id, move.company_id, move.date)
                else:
                    price_unit_foreign_curr = 0.0
                    price_unit_comp_curr = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
            else:
                quantity = 1.0
                price_unit_foreign_curr = base_line.amount_currency
                price_unit_comp_curr = base_line.balance

            res_config= self.env['res.config.settings'].search([],order="id desc", limit=1)
            if res_config:
                for rec in self:
                    if res_config.tax_discount_policy == 'untax':
                        if rec.discount_type == 'line':
                            if base_line.discount_method == 'fix':
                                price_unit_comp_curr = base_line.price_subtotal - base_line.discount_amount
                            elif base_line.discount_method == 'per':
                                price_unit_comp_curr = base_line.price_subtotal * (1 - (base_line.discount_amount / 100.0))
                            else:
                                price_unit_comp_curr = -(price_unit_comp_curr)    

                        elif rec.discount_type == 'global':
                            if rec.discount_method != False and rec.discount_amount != False:
                                if rec.amount_untaxed != 0.0:
                                    final_discount = ((rec.discount_amt*base_line.price_subtotal)/rec.amount_untaxed)
                                    price_unit_comp_curr = base_line.price_subtotal - rec.currency_id.round(final_discount)
                                else:
                                    final_discount = (rec.discount_amt*base_line.price_subtotal)/1.0
                                    discount = base_line.price_subtotal - rec.currency_id.round(final_discount)
                            else:
                                price_unit_comp_curr = -(price_unit_comp_curr)                 
                    else:
                        if self._context.get('default_type') in ('out_invoice','out_refund','out_receipt'):
                            sign = -(sign)
                        else:
                            pass    
                price_unit_comp_curr = sign*price_unit_comp_curr       
                               
               
            balance_taxes_res = base_line.tax_ids._origin.compute_all(
                price_unit_comp_curr,
                currency=base_line.company_currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=self.type in ('out_refund', 'in_refund'),
            )

            if base_line.currency_id:
                # Multi-currencies mode: Taxes are computed both in company's currency / foreign currency.
                amount_currency_taxes_res = base_line.tax_ids._origin.compute_all(
                    price_unit_foreign_curr,
                    currency=base_line.currency_id,
                    quantity=quantity,
                    product=base_line.product_id,
                    partner=base_line.partner_id,
                    is_refund=self.type in ('out_refund', 'in_refund'),
                )
                for b_tax_res, ac_tax_res in zip(balance_taxes_res['taxes'], amount_currency_taxes_res['taxes']):
                    tax = self.env['account.tax'].browse(b_tax_res['id'])
                    b_tax_res['amount_currency'] = ac_tax_res['amount']

                    # A tax having a fixed amount must be converted into the company currency when dealing with a
                    # foreign currency.
                    if tax.amount_type == 'fixed':
                        b_tax_res['amount'] = base_line.currency_id._convert(b_tax_res['amount'], move.company_id.currency_id, move.company_id, move.date)
            return balance_taxes_res

        taxes_map = {}

        # ==== Add tax lines ====
        to_remove = self.env['account.move.line']
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                # A line with the same key does already exist, we only need one
                # to modify it; we have to drop this one.
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    'tax_line': line,
                    'balance': 0.0,
                    'amount_currency': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                }
        self.line_ids -= to_remove

        # ==== Mount base lines ====
        for line in self.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab):
            # Don't call compute_all if there is no tax.
            if not line.tax_ids:
                line.tag_ids = [(5, 0, 0)]
                continue

            compute_all_vals = _compute_base_line_taxes(line)                

            # Assign tags on base line
            line.tax_tag_ids = compute_all_vals['base_tags']

            tax_exigible = True
            for tax_vals in compute_all_vals['taxes']:
                grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

                if tax.tax_exigibility == 'on_payment':
                    tax_exigible = False

                taxes_map_entry = taxes_map.setdefault(grouping_key, {
                    'tax_line': None,
                    'balance': 0.0,
                    'amount_currency': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                })
                taxes_map_entry['balance'] += tax_vals['amount']
                taxes_map_entry['amount_currency'] += tax_vals.get('amount_currency', 0.0)
                taxes_map_entry['tax_base_amount'] += tax_vals['base']
                taxes_map_entry['grouping_dict'] = grouping_dict
            line.tax_exigible = tax_exigible

        # ==== Process taxes_map ====
        for taxes_map_entry in taxes_map.values():
            # Don't create tax lines with zero balance.
            if self.currency_id.is_zero(taxes_map_entry['balance']) and self.currency_id.is_zero(taxes_map_entry['amount_currency']):
                taxes_map_entry['grouping_dict'] = False

            tax_line = taxes_map_entry['tax_line']
            tax_base_amount = -taxes_map_entry['tax_base_amount'] if self.is_inbound() else taxes_map_entry['tax_base_amount']

            if not tax_line and not taxes_map_entry['grouping_dict']:
                continue
            elif tax_line and recompute_tax_base_amount:
                tax_line.tax_base_amount = tax_base_amount
            elif tax_line and not taxes_map_entry['grouping_dict']:
                # The tax line is no longer used, drop it.
                self.line_ids -= tax_line
            elif tax_line:
                tax_line.update({
                    'amount_currency': taxes_map_entry['amount_currency'],
                    'debit': taxes_map_entry['balance'] > 0.0 and taxes_map_entry['balance'] or 0.0,
                    'credit': taxes_map_entry['balance'] < 0.0 and -taxes_map_entry['balance'] or 0.0,
                    'tax_base_amount': tax_base_amount,
                })
            else:
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
                tax_line = create_method({
                    'name': tax.name,
                    'move_id': self.id,
                    'partner_id': line.partner_id.id,
                    'company_id': line.company_id.id,
                    'company_currency_id': line.company_currency_id.id,
                    'quantity': 1.0,
                    'date_maturity': False,
                    'amount_currency': taxes_map_entry['amount_currency'],
                    'debit': taxes_map_entry['balance'] > 0.0 and taxes_map_entry['balance'] or 0.0,
                    'credit': taxes_map_entry['balance'] < 0.0 and -taxes_map_entry['balance'] or 0.0,
                    'tax_base_amount': tax_base_amount,
                    'exclude_from_invoice_tab': True,
                    'tax_exigible': tax.tax_exigibility == 'on_invoice',
                    **taxes_map_entry['grouping_dict'],
                })    
            if in_draft_mode:
                tax_line._onchange_amount_currency()
                tax_line._onchange_balance()

    

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for val in vals_list:

    #         if 'flag' in val:
    #             val.pop('flag')
    #             return super(account_move,self).create(vals_list)
                
    #         else:
    #             res = super(account_move,self).create(vals_list)
    #             for line in res.line_ids:
    #                 name = line.name
    #             if res.discount_type == 'line':

    #                 price = res.discount_amt_line
    #             elif res.discount_type == 'global':
    #                 price = res.discount_amt
    #             else:
    #                 price = 0  
    #             if name != 'Discount':

    #                 if res.discount_account_id:       
    #                     discount_vals = {
    #                             'account_id': res.discount_account_id, 
    #                             'quantity': 1,
    #                             'price_unit': -price,
    #                             'name': "Discount", 
    #                             'exclude_from_invoice_tab': True,
    #                             }            
    #                     res.with_context(check_move_validity=False).write({
    #                             'invoice_line_ids' : [(0,0,discount_vals)]
    #                             })
    #                 else:
    #                     pass    
    #             return res

    @api.onchange('invoice_line_ids','discount_amount','discount_method')
    def _onchange_invoice_line_ids(self):
        current_invoice_lines = self.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab)
        others_lines = self.line_ids - current_invoice_lines
        if others_lines and current_invoice_lines - self.invoice_line_ids:
            others_lines[0].recompute_tax_line = True
        self.line_ids = others_lines + self.invoice_line_ids
        self._onchange_recompute_dynamic_lines() 
        if self._context.get('default_type') == 'out_invoice' :
            total = 0.0
            for line in self.invoice_line_ids:
                if line.discount_method == 'per':
                    total += line.price_subtotal * (line.discount_amount/ 100)
                elif line.discount_method == 'fix':
                    total += line.discount_amount
            self.discount_amount_line = total
    

    @api.depends('discount_amount','discount_method')
    def write(self,vals):

        res = super(account_move,self).write(vals)
        for rec in self.line_ids:
            if self.discount_type != 'line':
                if rec.name == "Discount":
                    rec.with_context(check_move_validity=False).write({'price_unit':-self.discount_amt})

            if self._context.get('default_type') == 'out_invoice' :
                amount_total = self.amount_tax + self.amount_untaxed - self.discount_amount_line

                if self.discount_type == 'line':
                    if rec.name == "Discount":
                        if self.discount_amount_line > 0.0:
                            rec.with_context(check_move_validity=False).write({'debit':self.discount_amount_line})
                            rec.with_context(check_move_validity=False).write({'credit':0.0})
                    if rec.name == False or rec.name == '':
                        if self.discount_amount_line > 0.0:
                            rec.with_context(check_move_validity=False).write({'debit':amount_total})
                else:
                    if rec.name == False or rec.name == '':
                        rec.with_context(check_move_validity=False).write({'debit':self.amount_total})

            else:
                pass  

        return res  
    @api.onchange('discount_amount','discount_method')
    def _onchange_taxes(self):
        ''' Recompute the dynamic onchange based on taxes.
        If the edited line is a tax line, don't recompute anything as the user must be able to
        set a custom value.
        '''
        for line in self.line_ids:
            if not line.tax_repartition_line_id:
                line.recompute_tax_line = True
    
class account_payment(models.Model):
    _inherit = "account.payment"

    def _prepare_payment_moves(self): 

        res = super(account_payment,self)._prepare_payment_moves()
        for rec in res:
            rec.update({'flag':True})        
        return res
    

class account_move_line(models.Model):
    _inherit = 'account.move.line'
 
    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
    discount_type = fields.Selection(related='move_id.discount_type', string="Discount Applies to")
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Float('Discount Final Amount')

    @api.onchange('discount_method','discount_amount','amount_currency', 'currency_id', 'debit', 'credit', 'tax_ids', 'account_id',)
    def _onchange_mark_recompute_taxes(self):
        ''' Recompute the dynamic onchange based on taxes.
        If the edited line is a tax line, don't recompute anything as the user must be able to
        set a custom value.
        '''
        for line in self:
            if not line.tax_repartition_line_id:
                line.recompute_tax_line = True

