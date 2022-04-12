from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader,Context, Template
from django.db.models import Sum, Q
from .models import Customer,CustomerInvoice,CustomerInvoiceLineItem
from .models import Partner,PartnerInvoice,PartnerInvoiceLineItem,ResourceRate
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from django.db.models import Max

#the views below are in files with the same names
from .customer_invoices import customer_invoices,get_customer_invoice_data
from .partner_invoices import partner_invoices,get_partner_invoice_data
from .generated_partner_invoice import generated_partner_invoice
from .partner_invoice_detail import partner_invoice_detail
from .customer_invoice_detail import customer_invoice_detail
from .resource_rates import resource_rates
from .side_by_side import side_by_side
from .side_by_side_summary import customer_invoices_side_by_side
from .side_by_side_all import side_by_side_all

# Create your views here.

def index(request):
	#data
	#display
	context=({})
	return render(request=request, template_name='InvoicingWeb/Index.html',context=context)

#get all customers
def customers(request):
	#data
	customer_list=Customer.objects.order_by('CustomerName')
	
	#display
	context=({"customer_list": customer_list})

	return render(request=request,template_name='InvoicingWeb/Customers.html',context=context)
	
#get all partners
def partners(request):
	#data
	partner_list=Partner.objects.order_by('PartnerName')
	
	#display
	context=({"partner_list": partner_list})

	return render(request=request,template_name='InvoicingWeb/Partners.html',context=context)
		

def customer_detail(request,customer_name):
	#data
	customer=Customer.objects.filter(CustomerName=customer_name).get()
	
	#display
	context=({"customer":customer})
	
	return render(request=request,template_name='InvoicingWeb/CustomerDetail.html',context=context)
	

#functions	
