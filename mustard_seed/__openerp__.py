{
    'name' : "Mustard Seed Engineering",
    'version' : "1.0",
    'description' : "Manage all mustard seed transactions",
    'author' : "Krys_Nuvadga, Martin_Fongoh, Piar Inc.",
    'depends' : ['point_of_sale', 'account_accountant', 'hr', 'sale'],
    'installable' : True,
    'data': [
    	'views/template.xml', 
    	'views/transport_expense_income.xml', 
        'views/transport_invoice.xml', 

        'views/trans-report.xml', 
    ]
}
	# 'views/transport_others.xml', 
 	# 'views/gps.xml',
        # 'views/garrage.xml',  
