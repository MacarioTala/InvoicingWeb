from django.urls import path
from . import views

#add invoicingWeb view routes here. 

urlpatterns=[path('',views.index,name='Index'),
	path('Partner/Invoice/<invoice_number>',views.partner_invoice_detail,name='Partner Invoice Detail'),
	path('Customer/Invoice/<invoice_number>',views.customer_invoice_detail,name='Customer Invoice Detail'),
	path('Invoices/<customer_name>',views.customer_invoices,name='Customer Invoices'),
	path('Partners/Invoices/<partner_name>',views.partner_invoices,name='Partner Invoices'),
	path('Customers',views.customers,name='Customers'),
	path('Partners',views.partners,name='Partners'),
	path('Customers/<customer_name>',views.customer_detail,name='Customer Detail'),
	path('SideBySide/<invoice_number>',views.side_by_side,name='Side By Side'),
	path('SideBySideSummary/<customer_name>',views.customer_invoices_side_by_side,name='Side By Side Summary'),
	path('GeneratePartnerInvoice/<customer_invoice_number>',views.generated_partner_invoice,name='Generate Partner Invoice')
	]
	