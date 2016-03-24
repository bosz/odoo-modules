# -*- coding: utf-8 -*-

from openerp import models, fields, api
import time
from datetime import datetime, timedelta
import random



# class hotel(models.Model):
#     _name = 'hotel.hotel'

#     name = fields.Char()

class Customer(models.Model):
    _name = 'hotel.customer'
    name = fields.Char(string='Customer\'s name', required=True)
    description = fields.Text()




class Feature(models.Model):
	_name = 'hotel.feature'
	name = fields.Char(string='Name', required=True)




class Type(models.Model):
    _name = 'hotel.type'
    name = fields.Char(string='Room Type name', required=True)
    description = fields.Text()
    price = fields.Integer(string="Price of room type", required=True)
    feature_id = fields.Many2one('hotel.feature', string="Room Feature(s)")



class Room(models.Model):
	_name = 'hotel.room'
	name = fields.Char(string="Room Name", required=False)
	number = fields.Char(string='No', required=True)
	floor = fields.Integer(string='Room Floor Number')
	type_id = fields.Many2one('hotel.type',
     ondelete='set null', string="Room Type", index=True)




class Reservation(models.Model):
	"""docstring for Reservation when a cutomer comes to use hotel services """
	_name = 'hotel.reservation'
	
	date_Format = "%Y-%m-%d %H:%M:%S"

	def default_reservation_name(self):
		print "Setting default reservation Name"

		for res in self:
			print res
			# print res.id
			# return res.id
		return 'RSV '

	def default_roomPrice(self):
		print "Default room price"
		for room in self.room_id:
			for room_type in room.type_id:
				self.room_price = room_type.price



	name = fields.Char(string='Reservation Identification', required=True, default=default_reservation_name)
	checkIn_date = fields.Datetime()
	checkout_date = fields.Datetime()
	cust_id = fields.Many2one('hotel.customer',
     ondelete='set null', string="Customer info", index=True, required=True)
	room_id = fields.Many2one('hotel.room',
     ondelete='set null', string="Choose Your Room", index=True)
	
	status = fields.Selection(selection=[
		('draft', 'Creating New Reservation'), 
		('pending', 'Pending'),
		('checkedin', 'Checked In'),
		('checkedout', 'Checked Out'),
		('paid', 'Paid'),
		('cancelled', 'Cancelled')
		], string="Status of Reservation")
	
	date_paid = fields.Datetime(string="Date reservation was paid")
	
	room_price =  fields.Integer(string="Cost of room per day is ", computed="compute_roomPrice")
	num_of_days = fields.Integer(string="Number of days the client has been in lodged in the hotel", computed="compute_numOfDays")
	total_price = fields.Integer(string="Total cost from checked in date to checkout date", computed="compute_totalPrice")

	use_rs_id = fields.One2many('hotel.use_room_services', 
		'res_id', string='Used Room Service Id')

	rs_total_price = fields.Integer(string="Cost of all used room services ", computed="compute_usedRoomServiceCost")
	res_grand_total = fields.Integer(string="Grand total cost of reservation", computed="compute_grand_totalReservationCost")
	@api.depends('checkIn_date', 'checkout_date', 'room_id')
	def compute_roomPrice(self):
		print "computing Room Cost"
		for room in self.room_id:
			for room_type in room.type_id:
				print(self.room_price + " is the room price " )
				self.room_price = room_type.price

	@api.one
	@api.depends('checkIn_date', 'checkout_date')
	def compute_numOfDays(self):
		print "computing number of days lodged"
		self.num_of_days = 122

	@api.one
	@api.depends('checkIn_date', 'checkout_date', 'type_id')
	def compute_totalPrice(self):
		print "computing the total price"
		self.total_price = random.randint(1, 1e6)

	@api.one
	@api.depends('checkIn_date', 'checkout_date', 'use_rs_id')
	def compute_usedRoomServiceCost(self):
		print "Computing total price for all used room services"
		res_id = self.id
		self.env.cr.execute(
			'select sum(cost) as total from hotel_use_room_services, hotel_reservation where hotel_reservation.id = %d' %(res_id))
		vala = self.env.cr.fetchone()[0]
		print vala
	# CALCULATE 
	# 		room price
	# 		total price for lodging
	# 		number of days customer has lodged
	@api.onchange('checkIn_date', 'checkout_date', 'room_id')
	def _onchange_checkIn_date(self):
		print "making neccesary changes to price, number of days and cost"
		
		if self.room_id:
			# settings
			print "room id has been set"
			for room in self.room_id:
				for room_type in room.type_id:
					self.room_price = room_type.price
					print "changed the total price"

			# verify that checkin have been set, ie, the status is checkout
			if self.checkIn_date :
				print('checkin date is ' + self.checkIn_date)
				print('checkout date is ' + self.checkout_date)
				# compute number of days difference and set value to num_of_days field
				a = datetime.strptime(self.checkIn_date, self.date_Format)
				if self.checkout_date:
					b = datetime.strptime(self.checkout_date, self.date_Format) #customer has already checkout
				else:
					b = datetime.strptime(time.strftime(self.date_Format), self.date_Format) #customer has not yet checkout
				
				d = (b - a)
				days = d.days
				hours = d.seconds / 3600

				diff = days;
				if hours >= 2:
					diff += 1

				self.num_of_days = int(diff)

				# compute total price as product of num_of_days by date diff
				self.total_price = self.room_price * int(diff)
			else:
				print "Reservation still in pending state"
				self.num_of_days = 0
				self.total_price = 0
			
		else:
			print "room Id has not yet been set"


	# this method ensures that checkin date should not be greater than check out date
	def _check_startDate_lessthan_endDate(self, cr , uid , ids , context=None):
		for res in self.browse(self, cr , uid , ids , context=None):
			if res.checkIn_date > res.checkout_date:
				print res.checkIn_date
				print res.ckeckout_date
				return False
			return True



	def status_to_pending(self, cr, uid, name, context=None):
		print "I am changing status"
		print self.name
		return True


	#Below is the list of defaults on this model 
	_defaults = {
		'status': 'pending',
		'total_price': 0, 
		'num_of_days': 0,
	}
	# _constraints=[(_check_startDate_lessthan_endDate, 
	# 	'checkIn date cannot be greater than check Out date' , 
	# 	['checkIn_date','checkout_date'])]



	# 	CHANGE STATUS OF RESERVATION
	# 		CHANGE TO 
	# 			- checked in
	# 			- checked out
	# 			- paid 
	@api.multi
	def status_to_checkin(self):
		self.status = 'checkedin'
		self.checkout_date = ''
		self.checkIn_date = time.strftime(self.date_Format)
	@api.multi
	def status_to_checkout(self):
		self.status = 'checkedout'
		self.checkout_date = time.strftime(self.date_Format)
	@api.multi
	def status_to_paid(self):
		self.status = 'paid'
		self.date_paid = time.strftime(self.date_Format)
	@api.multi
	def status_to_cancelled(self):
		print 'cancelling reservation'
		self.status = 'cancelled'
	@api.multi
	def modal_useRoomService(self):
		# print 'loading the use room service modal'
	    # return {
	    #     'type': 'ir.actions.act_window',
	    #     'name': 'action_useRoomService',
	    #     'res_model': 'hotel.use_room_services',
	    #     # 'res_id': id ,
	    #     'view_type': 'form',
	    #     'view_mode': 'form',
	    #     'target' : 'new',
	    #     }
	    return {
              'name': 'action_useRoomService',
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'hotel',
              'type': 'ir.actions.act_window',
              'target': 'new',
              }

	@api.multi
	def update_duration_and_cost_of_reservation(self):
		print 'Updating the reservation cost, duration and total cost'


		for room in self.room_id:
			for room_type in room.type_id:
				self.room_price = room_type.price

		# verify that checkin have been set, ie, the status is checkout
		if self.checkIn_date :
			# compute number of days difference and set value to num_of_days field
			a = datetime.strptime(self.checkIn_date, self.date_Format)
			if self.checkout_date:
				b = datetime.strptime(self.checkout_date, self.date_Format) #customer has already checkout
			else:
				b = datetime.strptime(time.strftime(self.date_Format), self.date_Format) #customer has not yet checkout
			d = (b - a)
			days = d.days
			hours = d.seconds / 3600

			diff = days
			if hours >= 2:
				diff += 1

			self.num_of_days = int(diff)

			# compute total price as product of num_of_days by date diff
			self.total_price = self.room_price * int(diff)
			# print(" Number of Days = " . diff + " Cost of room category = " . self.room_price)
		else:
			print "Reservation still in pending state"
			self.num_of_days = 0
			self.total_price = 0



		print "Computing total price for all used room services"
		res_id = self.id
		self.env.cr.execute(
			'select sum(cost) as total from hotel_use_room_services, hotel_reservation where hotel_reservation.id = %d' %(res_id))
		vala = self.env.cr.fetchone()[0]
		print vala
		if vala:
			self.rs_total_price = vala

		print "computing Grand Total"
		self.res_grand_total = self.rs_total_price + self.total_price


class RoomService(models.Model):
	_name = 'hotel.room_service'
	name = fields.Char(string="Service Name" , required=True)
	description = fields.Text(string="Service Description")







class RoomServicesUsed(models.Model):
	"""docstring for RoomServicesUsed"""
	_name = 'hotel.use_room_services'
	description = fields.Text(string="Description of the room service used", required=True)
	res_id = fields.Many2one('hotel.reservation', string="Service Reservation")
	rs_id = fields.Many2one('hotel.room_service', string="Room Service", required=True)
	cost = fields.Integer(string="Total Cost", required=True)






# REPORT REPORT REPORT REPORT REPORT REPORT REPORT REPORT REPORT REPORT 
# REPORT REPORT REPORT REPORT REPORT REPORT REPORT REPORT REPORT REPORT
# REPORT REPORT REPORT REPORT REPORT REPORT REPORT REPORT REPORT REPORT


class FullReport(models.Model):
	"""This is the full report for the hotel system"""
	_name = 'hotel.full_hotel_report'
	_inherit='hotel.reservation'
	# def __init__(self, arg):
	# 	super(FullReport, self).__init__()
	# 	self.arg = arg

	v_status = ['pending', 'checkedin', 'checkedout', 'paid', 'cancelled']
	group_by_status = ' group by status '

	reservation_count_q = 'SELECT count(*) from hotel_reservation where status = '
	
	reservation_cost_q = 'SELECT sum(hotel_reservation_total_price) from hotel_reservation where status = ' 
	#Dont forget to append a "group by status" at the end of the final query
	
	room_count_q = 'SELECT count(*)  from hotel_rooms where status = '

	room_cost_q = 'SELECT sum(hotel_type.price) from hotel_type, hotel_rooms where hotel_rooms.type_id = hotel_type.id and status = '
	#Dont forget to append a "group by status" at the end of the final query


				# FIELDS
			# reservation count
	res_pen_count = fields.Integer(string="Total Number of pending reservations", computed="computeAll")
	res_cin_count = fields.Integer(string="Total Number of pending reservations", computed="computeAll")
	res_cout_count = fields.Integer(string="Total Number of pending reservations", computed="computeAll")
	res_paid_count = fields.Integer(string="Total Number of pending reservations", computed="computeAll")
	res_cncl_count = fields.Integer(string="Total Number of pending reservations", computed="computeAll")
			# reservation cost
	res_pen_cost = fields.Integer(string="Total Number of pending reservations", computed="computeAll")
	res_cin_cost = fields.Integer(string="Total Number of pending reservations", computed="computeAll")
	res_cout_cost = fields.Integer(string="Total Number of pending reservations", computed="computeAll")
	res_paid_cost = fields.Integer(string="Total Number of pending reservations", computed="computeAll")
	res_cncl_cost = fields.Integer(string="Total Number of pending reservations", computed="computeAll")


	def computeAll(self):
				#RESERVATION COUNT
			#1. pending
		self.env.cr.execute(reservation_count_q + v_status[0])		
		self.res_pen_count = self.env.cr.fetchone()[0]
			#2. checked in
		self.env.cr.execute(reservation_count_q + v_status[1])		
		self.res_cin_count = self.env.cr.fetchone()[0]
			#3. checked out
		self.env.cr.execute(reservation_count_q + v_status[2])		
		self.res_cout_count = self.env.cr.fetchone()[0]
			#4. paid
		self.env.cr.execute(reservation_count_q + v_status[3])		
		self.res_paid_count = self.env.cr.fetchone()[0]
			#5. cancelled
		self.env.cr.execute(reservation_count_q + v_status[4])		
		self.res_cncl_count = self.env.cr.fetchone()[0]


				#RESERVATION COSTS
			#1. pending
		self.env.cr.execute(reservation_cost_q + v_status[0] + group_by_status)
		self.res_pen_cost = self.env.cr.fetchone()[0]
			#2. checked in
		self.env.cr.execute(reservation_cost_q + v_status[1] + group_by_status)
		self.res_cin_cost = self.env.cr.fetchone()[0]
			#3. checked out
		self.env.cr.execute(reservation_cost_q + v_status[2] + group_by_status)
		self.res_cout_cost = self.env.cr.fetchone()[0]
			#4. paid
		self.env.cr.execute(reservation_cost_q + v_status[3] + group_by_status)
		self.res_paid_cost = self.env.cr.fetchone()[0]
			#5. cancelled
		self.env.cr.execute(reservation_cost_q + v_status[4] + group_by_status)
		self.res_cncl_cost = self.env.cr.fetchone()[0]





# custom report
# class ParticularReport(models.AbstractModel):
#     _name = 'report.hotel.reservation_custom_report'
#     @api.multi
#     def render_html(self, data=None):
#         report_obj = self.env['report']
#         report = report_obj._get_report_from_name('<<module.reportname>>')
#         docargs = {
#             'doc_ids': self._ids,
#             'doc_model': report.model,
#             'docs': self,
#         }
#         return report_obj.render('<<module.reportname>>', docargs)