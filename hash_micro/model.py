from openerp import models, fields, api
from openerp.exceptions import ValidationError


class quotationProposal(models.Model):
	"""Quotation to proposal"""
	
	_name = 'sale.order'
	_inherit = 'sale.order'

	def generate_proposal_number(self):
		print "Generating proposal Number"


	# need this function to compute the new total price which is 
	# total invoice price = price of line + price of custom line
	@api.multi
	@api.depends('sale_order_ids.quantity_delivered', 
		'sale_order_ids.unit_price', 
		'sale_order_ids.quantity_ordered',

		'order_line.price_subtotal')
	def evaluate_all(self):
		print "\n\n\nComputing total price\n\n\n"
		custom_total = 0
		for i in self:
			for j in i.sale_order_ids:
				custom_total += j.sub_total
			self.custom_total = custom_total
			self.amount_total = self.custom_total + (self.amount_untaxed - self.amount_tax)
			
	test = fields.Text('Test field')
	proposal_number = fields.Text('Proposal Number', help="Auto Generated Proposal Number")
	tc = fields.Many2one('sale.config.settings', help="Terms and conditions for the Proposal")

	_sql_constraints = [
	    ('proposal_number_un', 'unique(proposal_number)', 'unique proposal number')
	]

	sale_order_ids = fields.One2many('sale.order.custom.line', 'sale_order_id')

	custom_total = fields.Float('Custom Total')

	# generate proposal
	def print_proposal(self, cr, uid, ids, context=None):
		print "Generating proposal"


class custom_sale_order_line(models.Model):
	"""Transactions for the particular id"""
	
	_name = 'sale.order.custom.line'
	
	@api.onchange('quantity_delivered', 'unit_price', 'quantity_ordered')
	def _onchange_quantity_delivered(self):
		self.sub_total = self.quantity_ordered * self.unit_price
		print "Sub Total is " + str(self.sub_total)


	sale_order_id = fields.Many2one('sale.order')

	product_name = fields.Char('Product')
	description = fields.Char('Description')
	quantity_ordered = fields.Float('Quantity Qty')
	quantity_delivered = fields.Float('Delivered')
	invoiced = fields.Float("Invoiced")
	unit_price = fields.Float('Unit Price')

	tax_id = fields.Many2many('account.tax', stting="Tax")

	sub_total = fields.Float('SubTotal')



class termsAndConditions_config(models.Model):
	"""This is the configuration for terms and conditions"""
	
	_inherit = 'sale.config.settings'
	_name = 'sale.config.settings'

	tc = fields.Text('Terms and Conditions', 
		default="This is the default terms and conditions for the sales management")
		