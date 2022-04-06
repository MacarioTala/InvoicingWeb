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
		
def customer_invoices_side_by_side(request,customer_name):
	template=loader.get_template('InvoicingWeb/SideBySideSummary.html')
	
	context = get_customer_side_by_side_data(request,customer_name)
	
	return HttpResponse(template.render(context,request)) 

def customer_detail(request,customer_name):
	#data
	customer=Customer.objects.filter(CustomerName=customer_name).get()
	
	#display
	context=({"customer":customer})
	
	return render(request=request,template_name='InvoicingWeb/CustomerDetail.html',context=context)
	
def side_by_side(request,invoice_number):
	context=get_side_by_side_data(invoice_number)
	
	return render(request=request, template_name='InvoicingWeb/SideBySide.html',context=context)


#functions	
def get_customer_side_by_side_data(request,customer_name):
	class side_by_side_row:
		def __init__(self, CustomerInvoiceNumber, CustomerAmount, PartnerInvoiceNumber,PartnerStatedAmount,PartnerComputedAmount, Margin):
			self.CustomerInvoiceNumber=CustomerInvoiceNumber
			self.CustomerAmount=CustomerAmount
			self.PartnerInvoiceNumber=PartnerInvoiceNumber
			self.PartnerStatedAmount=PartnerStatedAmount
			self.PartnerComputedAmount=PartnerComputedAmount
			self.Margin=Margin
			
	customer_invoices=get_customer_invoice_data(customer_name)["invoice_list"]
	
	side_by_side_list=[]
	
	for customer_invoice in customer_invoices:
		customer_amount=customer_invoice.InvoiceTotal
		partner_computed_amount=customer_invoice.PartnerInvoice.get_rate_computed_invoice_total()['invoice_total']
		partner_stated_amount=customer_invoice.PartnerInvoice.AmountOnInvoice
		margin=round(((customer_amount.amount-partner_stated_amount.amount)/customer_amount.amount*100),2)
		
		side_by_side_item=side_by_side_row(CustomerInvoiceNumber=customer_invoice.CustomerInvoiceNumber,
		PartnerInvoiceNumber=customer_invoice.PartnerInvoice.InvoiceNumber,CustomerAmount=customer_amount, 
		PartnerStatedAmount=partner_stated_amount,PartnerComputedAmount=partner_computed_amount,Margin=margin)

		side_by_side_list.append(side_by_side_item)
	
	context= {"side_by_side_list" : side_by_side_list}
	
	return context
	
def get_side_by_side_data(invoice_number):
	#data
	#check if invoice_number is a customer or partner invoice by seeing which type exists. 
	#each type of invoice has a different naming convention. 
	#Note: This will fail if the view-side filter changes, because checking isn't very strict
	customer_invoice_exists=CustomerInvoice.objects.filter(InvoiceNumber=invoice_number).exists()
	partner_invoice_exists=PartnerInvoice.objects.filter(InvoiceNumber=invoice_number).exists()
	
	if (customer_invoice_exists):
		customer_invoice=CustomerInvoice.objects.filter(InvoiceNumber=invoice_number).first()
		partner_invoice=PartnerInvoice.objects.filter(CustomerInvoice__InvoiceNumber=customer_invoice.InvoiceNumber).first()
		
	if (partner_invoice_exists):
		partner_invoice=PartnerInvoice.objects.filter(InvoiceNumber=invoice_number).first()
		customer_invoice=partner_invoice.CustomerInvoice
			
	#totals
	
	customer_invoice_total = customer_invoice.get_invoice_total()["invoice_total"]
	customer_hours_total = customer_invoice.get_invoice_total()["hours_total"]
	
	partner_invoice_total = partner_invoice.get_rate_computed_invoice_total()["invoice_total"]
	partner_hours_total = partner_invoice.get_rate_computed_invoice_total()["hours_total"]
		
	#display
	context=({"customer_invoice" :customer_invoice,
	"customer_invoice_total": customer_invoice_total,
	"customer_hours_total": customer_hours_total ,
	"partner_invoice":partner_invoice,
	"partner_invoice_total": partner_invoice_total ,
	"partner_hours_total": partner_hours_total
	})
	
	return context


	
