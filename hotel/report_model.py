# -*- coding: utf-8 -*-

from openerp import models, fields, api
import time
from datetime import datetime, timedelta
import random

# REPORT 				REPORT 				REPORT 				REPORT 

class FullReport(models.Model):
	"""This is the full report for the hotel system"""
	_name = 'hotel.custom_reservation_report'
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
		self.env.cr.execute(reservation_cost_q + v_status[] + group_by_status)
		self.res_pen_cost = self.env.cr.fetchone()[0]
			#2. checked in
		self.env.cr.execute(reservation_cost_q + v_status[] + group_by_status)
		self.res_cin_cost = self.env.cr.fetchone()[0]
			#3. checked out
		self.env.cr.execute(reservation_cost_q + v_status[] + group_by_status)
		self.res_cout_cost = self.env.cr.fetchone()[0]
			#4. paid
		self.env.cr.execute(reservation_cost_q + v_status[] + group_by_status)
		self.res_paid_cost = self.env.cr.fetchone()[0]
			#5. cancelled
		self.env.cr.execute(reservation_cost_q + v_status[] + group_by_status)
		self.res_cncl_cost = self.env.cr.fetchone()[0]



