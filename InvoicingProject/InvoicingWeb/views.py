from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader,Context, Template
from django.db.models import Sum
from .models import Customer,CustomerInvoice,CustomerInvoiceLineItem
from .models import Partner,PartnerInvoice,PartnerInvoiceLineItem
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
	
#get all invoices of a customer
def customer_invoices(request,customer_name):
	#data
	customer_invoice_list=CustomerInvoice.objects.filter(InvoiceCustomer__CustomerName=customer_name)
	#we currently also need to grab all the partner invoices, because the relationship starts at partner invoice not yet sure if a better way exists. 
	partner_invoice_list=PartnerInvoice.objects.filter(CustomerInvoice__InvoiceCustomer__CustomerName=customer_name)
	template=loader.get_template('InvoicingWeb/CustomerInvoice.html')
	
	class inner_invoice:
		def __init__(self,CustomerInvoiceNumber,PartnerInvoiceNumber):
			self.CustomerInvoiceNumber=CustomerInvoiceNumber
			self.PartnerInvoiceNumber=PartnerInvoiceNumber
			
	invoice_list=[]
	for customer_invoice in customer_invoice_list:
		partner_invoice_number=partner_invoice_list.filter(CustomerInvoice__InvoiceNumber=customer_invoice.InvoiceNumber).first()		
		current_invoice=inner_invoice(CustomerInvoiceNumber=customer_invoice.InvoiceNumber, PartnerInvoiceNumber=partner_invoice_number)
		invoice_list.append(current_invoice)
	
	#display
	context = {	"customer_name":customer_name,
	"invoice_list" : invoice_list}
	return HttpResponse(template.render(context,request))


def partner_invoices(request,partner_name,customer_name):
	partner_invoice_list=PartnerInvoice.objects.filter(InvoicePartner__PartnerName=partner_name)
	template=loader.get_template('InvoicingWeb/PartnerInvoice.html')
	context = {"partner_invoice_list" : partner_invoice_list,
	"partner_name":partner_name}
	return HttpResponse(template.render(context,request))

def customer_invoice_totals(invoice_number):
	relevant_invoice = CustomerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems = CustomerInvoiceLineItem.objects.filter(CustomerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber)
	invoice_total = relevant_invoice_lineitems.aggregate(Sum('CInvoiceLineItemAmount'))['CInvoiceLineItemAmount__sum'] 
	hours_total = relevant_invoice_lineitems.aggregate(Sum('CInvoiceLineItemHours'))['CInvoiceLineItemHours__sum']
	
	#totals 
	totals=({"invoice_total" : invoice_total,
	"hours_total": hours_total})
	return totals

def partner_invoice_totals(invoice_number):
	relevant_invoice = PartnerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems = PartnerInvoiceLineItem.objects.filter(PartnerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber)
	invoice_total = relevant_invoice_lineitems.aggregate(Sum('PILineItemAmount'))['PILineItemAmount__sum'] 
	hours_total = relevant_invoice_lineitems.aggregate(Sum('PILineItemHours'))['PILineItemHours__sum']
	
	#totals 
	totals=({"invoice_total" : invoice_total,
	"hours_total": hours_total})
	return totals	
	
def partner_invoice_detail(request,invoice_number):
	#data
	relevant_invoice = PartnerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems=PartnerInvoiceLineItem.objects.filter(PartnerInvoice__InvoiceNumber=invoice_number)
	invoice_total=partner_invoice_totals(invoice_number)["invoice_total"] 
	hours_total=partner_invoice_totals(invoice_number)["hours_total"] 
	
	#display
	context=({"invoice" : relevant_invoice, 
	"invoice_total" : invoice_total, 
	"invoice_line_items": relevant_invoice_lineitems,
	"invoice_hours_total":hours_total}) 
	
	return render(request=request,template_name='InvoicingWeb/PartnerInvoiceDetail.html',context=context)


def customer_invoice_detail(request,invoice_number):
	#data
	relevant_invoice = CustomerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems = CustomerInvoiceLineItem.objects.filter(CustomerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber)
	invoice_total = customer_invoice_totals(invoice_number)["invoice_total"]
	hours_total = customer_invoice_totals(invoice_number)["hours_total"]
	partner_invoice="" #is there a better way to do empty strings in Python?
	if PartnerInvoice.objects.filter(CustomerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber).exists():
		partner_invoice = PartnerInvoice.objects.filter(CustomerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber).get()
	
	#display
	context=({"invoice" : relevant_invoice, 
	"invoice_total" : invoice_total, 
	"invoice_line_items": relevant_invoice_lineitems,
	"invoice_hours_total":hours_total,
	"partner_invoice": partner_invoice}) 
	return render(request=request, template_name='InvoicingWeb/CustomerInvoiceDetail.html',context=context)

def customer_detail(request,customer_name):
	#data
	customer=Customer.objects.filter(CustomerName=customer_name).get()
	
	#display
	context=({"customer":customer})
	
	return render(request=request,template_name='InvoicingWeb/CustomerDetail.html',context=context)
	
def side_by_side(request,invoice_number):
	#data
	#check if invoice_number is a customer or partner invoice by seeing which type exists. 
	#each type of invoice has a different naming convention. 
	#checks inside are because the matching invoice might not exist
	customer_invoice_exists=CustomerInvoice.objects.filter(InvoiceNumber=invoice_number).exists()
	partner_invoice_exists=PartnerInvoice.objects.filter(InvoiceNumber=invoice_number).exists()
	
	if (customer_invoice_exists):
		customer_invoice=CustomerInvoice.objects.filter(InvoiceNumber=invoice_number).first()
		partner_invoice=PartnerInvoice.objects.filter(CustomerInvoice__InvoiceNumber=customer_invoice.InvoiceNumber).first()
		
	if (partner_invoice_exists):
		partner_invoice=PartnerInvoice.objects.filter(InvoiceNumber=invoice_number).first()
		customer_invoice=partner_invoice.CustomerInvoice
			
	#totals
	
	customer_invoice_total = customer_invoice_totals(customer_invoice.InvoiceNumber)["invoice_total"]
	customer_hours_total = customer_invoice_totals(customer_invoice.InvoiceNumber)["hours_total"]
	
	partner_invoice_total = partner_invoice_totals(partner_invoice.InvoiceNumber)["invoice_total"]
	partner_hours_total = partner_invoice_totals(partner_invoice.InvoiceNumber)["hours_total"]
		
	#display
	context=({"customer_invoice" :customer_invoice,
	"customer_invoice_total": customer_invoice_total,
	"customer_hours_total": customer_hours_total ,
	"partner_invoice":partner_invoice,
	"partner_invoice_total": partner_invoice_total ,
	"partner_hours_total": partner_hours_total
	})
	
	return render(request=request, template_name='InvoicingWeb/SideBySide.html',context=context)