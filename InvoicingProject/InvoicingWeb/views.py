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
	customer_invoice_list=CustomerInvoice.objects.filter(InvoiceCustomer__CustomerName=customer_name)
	template=loader.get_template('InvoicingWeb/CustomerInvoice.html')
	context = {"customer_invoice_list" : customer_invoice_list,
	"customer_name":customer_name}
	return HttpResponse(template.render(context,request))

#get all invoices billed to a partner for a customer. e.g. what are the invoices billed to Marici(partner_name) for BeamReaders(customer_name)
def partner_invoices(request,partner_name,customer_name):
	partner_invoice_list=PartnerInvoice.objects.filter(InvoiceCustomer__PartnerName=partner_name)#This is a bug, change this to get all invoices to a partner for a customer.
	template=loader.get_template('InvoicingWeb/PartnerInvoice.html')
	context = {"partner_invoice_list" : partner_invoice_list,
	"partner_name":partner_name}
	return HttpResponse(template.render(context,request))
	
def partner_invoice_detail(request,invoice_number):
	#data
	relevant_invoice = PartnerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems=PartnerInvoiceLineItem.objects.filter(PILineItemInvoice__InvoiceNumber=invoice_number)
	invoice_total=relevant_invoice_lineitems.aggregate(sum=Sum('PILineItemAmount')).values 
	hours_total=relevant_invoice_lineitems.aggregate(sum=Sum('PILineItemHours')).values
	
	#display
	context=({"invoice" : relevant_invoice, 
	"invoice_total" : invoice_total, 
	"invoice_line_items": relevant_invoice_lineitems,
	"invoice_hours_total":hours_total}) 
	
	return render(request=request,template_name='InvoicingWeb/PartnerInvoiceDetail.html',context=context)

def customer_invoice_totals(invoice_number):
	relevant_invoice = CustomerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems = CustomerInvoiceLineItem.objects.filter(CustomerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber)
	invoice_total = relevant_invoice_lineitems.aggregate(Sum('CInvoiceLineItemAmount'))['CInvoiceLineItemAmount__sum'] 
	hours_total = relevant_invoice_lineitems.aggregate(Sum('CInvoiceLineItemHours'))['CInvoiceLineItemHours__sum']
	
	#totals 
	totals=({"invoice_total" : invoice_total,
	"hours_total": hours_total})
	return totals
	
def customer_invoice_detail(request,invoice_number):
	#data
	relevant_invoice = CustomerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems = CustomerInvoiceLineItem.objects.filter(CustomerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber)
	invoice_total = customer_invoice_totals(invoice_number)["invoice_total"]
	hours_total = customer_invoice_totals(invoice_number)["hours_total"]
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
	#check if invoice_number is a customer or partner invoice
	customer_invoice_exists=CustomerInvoice.objects.filter(InvoiceNumber=invoice_number).exists()
	partner_invoice_exists=PartnerInvoice.objects.filter(InvoiceNumber=invoice_number).exists()
	
	if (customer_invoice_exists):
		customer_invoice=CustomerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
		partner_invoice=PartnerInvoice.objects.filter(CustomerInvoice__InvoiceNumber=customer_invoice.InvoiceNumber).get()
	elif (partner_invoice_exists):
		partner_invoice=PartnerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
		customer_invoice=partner_invoice.CustomerInvoice
	else: #!customer_invoice_exists && !partner_invoice_exists
		customer_invoice=None
		partner_invoice=None
	#totals
	customer_invoice_total = customer_invoice_totals(invoice_number)["invoice_total"]
	customer_hours_total = customer_invoice_totals(invoice_number)["hours_total"]
	
	
	#display
	context=({"customer_invoice" :customer_invoice,
	"customer_invoice_total": customer_invoice_total,
	"customer_hours_total": customer_hours_total,
	"partner_invoice":partner_invoice	
	})
	
	return render(request=request, template_name='InvoicingWeb/SideBySide.html',context=context)