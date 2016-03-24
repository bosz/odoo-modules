from openerp import models, fields, api
from openerp.exceptions import ValidationError

# manage the gps invoice in total
class gpsInvoice_account_invoice(models.Model):
	"""I want to add a field to hold the total number of gps devices on each and every invoice"""
	# @api.depends('invoice_line_ids.product_id')

	_name = "account.invoice"
	_inherit = "account.invoice"

	invoice_type = fields.Selection(string='Invoice Type', store=True,
		 selection=[('tracker', 'Tracker'), ('garrage', 'Garrage'), 
		 ('transport', 'Transport'), ('other', 'Others')],  
		 help="If this field is true, then we know this record is for a gps invoice", 
		 default='other')

	@api.depends('partner_id', 'invoice_line_ids.product_id')
	def _compute_totalDevices(self):
		for x in self:
			cnt = 0
			for j in x.invoice_line_ids:
				cnt += 1
			x.total_devices = cnt
			print '\n\nTotal number of devices is ' + str(x.total_devices) + " devices \n\n"

	total_devices = fields.Integer('Total Number of Devices', store=True, compute="_compute_totalDevices", default=0)


	# GARRAGE GARRAGE GARRAGE GARRAGE 
	mechanic_id = fields.Many2one('hr.employee', string="Mechanic's In Charge")
	commission = fields.Float(string="Mechanic's Commision", default=0)

	expected_repair_start = fields.Date('Repair Started On')
	expected_repaid_end   = fields.Date('Repair Ended on')

	complaint = fields.Text('Complaint')
	color = fields.Integer()

	@api.multi
	def calculate_commission(self):
		print "Calculating Mechanic's Commission for the job"
		self.commission = self.amount_total * self.mechanic_id.commission_percentage
		print "Done calculating mechanic's commission "

		

	summary_id = fields.One2many('account.invoice.summary', 'invoice_id',
	 string="tracker summary", help="Holds the id that links this model to the summary model")
	@api.multi
	def summarize_gps_invoice(self, cr):
		print "summarizing the gps invoice"
		# Fields to update/insert into : 
		# 		invoice_id, tot_price, category_id, quantity
		tot = 0
		summary = {}
		for product in self.invoice_line_ids:
			tot = tot + 1

			invoice_id = self.id
			category_id = product.product_id.product_tmpl_id.categ_id.id
			quantity = 1
			price = product.price_subtotal
			tot_price = product.price_subtotal


			is_id = 'iv_id' + str(invoice_id) + 'ct_id' + str(category_id)
			if is_id in summary: #record already exists, update quantity and total price
				summary[is_id]['tot_price'] += tot_price
				summary[is_id]['quantity'] += 1
			else:  #record not found, so create new one
				summary.update(
						{is_id:{
							'invoice_id': invoice_id, 
							'category_id': category_id, 
							'quantity': quantity, 
							'price': price, 
							'tot_price': tot_price
						}}
					)

		# update the total number of devices
		self.total_devices = tot

		print summary
		
		self.ensure_one()
		# clean the table
		self.env.cr.execute("DELETE from account_invoice_summary where invoice_id = %d" % (self.id))
		# ttt = self.env.cr.fetchone()[0]

		# now, we are going to iterate over the fields and add those new records we have created
		for x in summary:
			self.env.cr.execute(
				"INSERT INTO account_invoice_summary(invoice_id, category_id, quantity, price, tot_price)" + 
				"VALUES (%d, %d, %d, %d, %d) " % 
					(int(summary[x]['invoice_id']), int(summary[x]['category_id']), 
					int(summary[x]['quantity']), int(summary[x]['price']), 
					int(summary[x]['tot_price']))
				)




# manage the individual gps on the invoice
class gpsInvoice_product_template(models.Model):
	"""  Add the imea number to product line so that on adding a new product to the 
	sales invoice, you select the product id and the imea is automatically filled  """

	_name = "account.invoice.line"
	_inherit = "account.invoice.line"
	
	@api.depends('product_id')
	def _compute_imea(self):
		siz = 0
		for product in self:
			product.imea_number = product.product_id.product_tmpl_id.imea_number
			siz = siz + 1
		print "we have number "
		print siz
		print " items on the invoice "
		# account.invoice.total_devices = siz

	imea_number = fields.Char("IMEI Number", compute='_compute_imea', default=0)
	car_number = fields.Char('Car Number')
	tracker_number = fields.Char("Tracker Num", help="Tracker number ( car-tracker pair ) ")

	_sql_constraints = [
	    ('track_invoice_imea_unique', 'unique(invoice_id, product_id)', 'Cannot Use one tracker twice!\nPlease, input a new imei to proceed')
	]




class GPS_product_template(models.Model):
	"""Add the imea numbe to the products table"""

	_name = "product.template"
	_inherit = "product.template"

	imea_number = fields.Char('IMEA Number')
	car_matricule = fields.Char("Matricule Number")

	_sql_constraints = [
	    ('imea_unique', 'unique(imea_number)', 'IMEI already exists!\nPlease, input a new imei to proceed')
	]

class summary_priceByQuantity(models.Model):

	_name = 'account.invoice.summary'

	"""This will hold the 
	invoice_id: the id of the invoice
	price: the price of the product
	quantity: the number of products that are of same price
	"""
	invoice_id = fields.Many2one('account.invoice', help="The identificatio of the invoice")
	category_id = fields.Many2one('product.category', string="The category", 
		help="The category that has this record")
	price = fields.Integer('group price')
	quantity = fields.Integer('number of of that price')	
	tot_price = fields.Integer('Total Price')

		

class MechanicAsAn_hr_employee(models.Model):
	"""Adding the commission percentage per mechanic"""
	
	_name = "hr.employee"
	_inherit = "hr.employee"

	commission_percentage = fields.Float(string="Commission Percentage", 
		help="Percentage of commision to be used on the employee to calculate part of his/her salary", 
		default=0)




# TRANSPORT MODULES
class transport(models.Model):
	"""Transport Main invoice """

	_inherit = 'mail.thread'
	_name = 'transport.invoice'	

	driver_id = fields.Many2one('hr.employee', string="Driver")
	truck_id = fields.Many2one('product.product', string="Truck")

	start_date = fields.Date('Transaction Start Date')
	end_date = fields.Date('Transaction End Date')

	commision = fields.Float('Drivers\' Commission percentage')
	controller_cost = fields.Integer('Controller Cost')

	transport_invoice_ids = fields.One2many('transport.invoice.line', 'transaction_id')
	state = fields.Selection(selection=[('draft', 'Draft'), ('open', 'Open'), ('closed', 'Closed')], default="draft")

	@api.multi
	@api.depends('transport_invoice_ids.inc_amount', 
				 'transport_invoice_ids.exp_amount')
	def evaluate_transport(self):
		print "computing transport information"

		total_expense_no_affect_salary = 0
		total_expense_affects_salary = 0
		total_income = 0
		deficit = 0
		for i in self:
			for j in i.transport_invoice_ids:
				deficit += j.deficit
				total_income += j.inc_amount
				print str(j.inc_amount) + "is income amount"
				if j.affects_salary:
					total_expense_affects_salary += j.exp_amount
				else:
					total_expense_no_affect_salary += j.exp_amount
			i.total_expense = total_expense_no_affect_salary + total_expense_affects_salary
			i.total_expense_no_affect_salary = total_expense_no_affect_salary
			i.total_expense_affects_salary = total_expense_affects_salary
			i.total_income = total_income
			i.deficit = deficit

			i.drivers_salary = (i.total_income - i.total_expense_affects_salary) * (i.commision / 100) - i.deficit
			
			i.net_monthly_balance = i.total_income - i.total_expense - i.drivers_salary - i.controller_cost 
		
		print "Done with total income and total expense"

	@api.multi
	def validate_transport(self):
		self.state = 'open'

	@api.multi
	def close_transport(self):
		self.state = 'closed'


	total_income = fields.Float('Total Income', compute="evaluate_transport", store=True)

	total_expense = fields.Float('Total Expenses', compute="evaluate_transport", store=True)
	total_expense_no_affect_salary = fields.Float('Total Expenses no affect salary', compute="evaluate_transport", store=True)
	total_expense_affects_salary = fields.Float('Total Expenses affects salary', compute="evaluate_transport", store=True)


	drivers_salary = fields.Float('Driver\'s Salary', compute="evaluate_transport", store=True)
	net_monthly_balance = fields.Float('Net Monthly Balance', compute="evaluate_transport", store=True)
	observation = fields.Text('Observation')







class transport_invoice_line(models.Model):
	"""Transactions for the particular id"""
	
	_name = 'transport.invoice.line'
	transaction_id = fields.Many2one('transport.invoice')
	deficit = fields.Float('Day\'s Deficit ')
	date = fields.Date('Date of Transaction')
	affects_salary = fields.Boolean('Affects Salary', 
		help="If checked, this field will affect the salary of the driver")


	# invocome
	inc_amount = fields.Float('Income Amount')
	inc_desc = fields.Text('Description of Income')

	# expenses
	exp_amount = fields.Float('Expense Amount')
	exp_desc = fields.Text('Expense Description')





# this is a test situation. 
# WHAT IF 
# MONTHS TRANSPORTATION (id, exp_id, cust_inc_id[a car is a customer])

# each month, create an expense

class trans(models.Model):
	_name = 'mse.transport'
	expense_line_ids = fields.One2many('account.invoice', 'transport_id')
	expense_line_ids = fields.One2many('hr.expense', 'transport_id')


class ttranspo_expense(models.Model):
 	_name = 'hr.expense'
 	_inherit = 'hr.expense'

 	is_salariable = fields.Boolean('Affects Salary', help="If this expense affects the staff's salary")
 	transport_id = fields.Many2one('mse.transport')


class acc_invoice(models.Model):
	_inherit = 'account.invoice'
	transport_id = fields.Many2one('mse.transport', string='Invoice Reference',
        ondelete='cascade', index=True)
		

