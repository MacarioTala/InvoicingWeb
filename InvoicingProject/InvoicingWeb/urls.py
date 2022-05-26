from django.urls import path
from . import views

#add invoicingWeb view routes here. 

urlpatterns=[path('',views.index,name='Index'),
	path('Customer/Invoice/<invoice_number>',views.customer_invoice_detail,name='Customer Invoice Detail'),
	path('Customers',views.customers,name='Customers'),
	path('Customers/<customer_name>',views.customer_detail,name='Customer Detail'),
	path('GeneratePartnerInvoice/<customer_invoice_number>',views.generated_partner_invoice,name='Generate Partner Invoice'),
	path('Invoices/<customer_name>',views.customer_invoices,name='Customer Invoices'),
	path('Partner/Invoice/<invoice_number>',views.partner_invoice_detail,name='Partner Invoice Detail'),
	path('Partners',views.partners,name='Partners'),
	path('Partners/Invoices/<partner_name>',views.partner_invoices,name='Partner Invoices'),
	path('SideBySide/',views.side_by_side_all,name='Side By Side - All'),
	path('SideBySide/<invoice_number>',views.side_by_side,name='Side By Side - Customer'),
	path('SideBySideSummary/<customer_name>',views.customer_invoices_side_by_side,name='Side By Side Summary'),
	path('ResourceRate/<customer_name>',views.resource_rates,name='Resource Rates'),
	path('ResourceRate/',views.resource_rates,name='Resource Rates')
	]
	
	