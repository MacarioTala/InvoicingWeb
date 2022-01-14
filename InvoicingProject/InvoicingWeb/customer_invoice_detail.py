from django.template import loader,Context, Template
from .models import Customer,CustomerInvoice,PartnerInvoice,CustomerInvoiceLineItem
from django.http import HttpResponse
from django.db.models import Sum, Q
from djmoney.money import Money
from django.shortcuts import render

def customer_invoice_detail(request,invoice_number):
	context = get_customer_invoice_detail_data(invoice_number)
	return render(request=request, template_name='InvoicingWeb/CustomerInvoiceDetail.html',context=context)

def get_customer_invoice_detail_data(invoice_number):
	#data
	relevant_invoice = CustomerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems = CustomerInvoiceLineItem.objects.filter(CustomerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber)
	invoice_total = relevant_invoice.get_invoice_total()["invoice_total"]
	hours_total = relevant_invoice.get_invoice_total()["hours_total"]#refactor this later to its own method
	partner_invoice="" #is there a better way to do empty strings in Python?

	if PartnerInvoice.objects.filter(CustomerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber).exists():
		partner_invoice = PartnerInvoice.objects.filter(CustomerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber).get()
	
	class customer_invoice_line_item:
		def __init__ (self,invoice_line_item,amount):
			self.invoice_line_item=invoice_line_item
			self.amount=amount
	
	display_line_items=[]
	
	for line_item in relevant_invoice_lineitems:
		current_rate = line_item.get_resource_rate()['rate_to_customer']
		total_amount = line_item.TotalHours * current_rate
		display_line_items.append(customer_invoice_line_item(invoice_line_item=line_item,amount=round(total_amount,2)))
		
	#display
	context=({"invoice" : relevant_invoice, 
	"invoice_total" : invoice_total,
	"invoice_line_items": display_line_items,
	"invoice_hours_total":hours_total,
	"partner_invoice": partner_invoice}) 
	return context

def customer_invoice_totals(invoice_number):#This is very DB heavy, refactor this later. This is one hit per line_item
	relevant_invoice = CustomerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems = CustomerInvoiceLineItem.objects.filter(CustomerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber)
	
	class rate_adjusted_line_item:
		def __init__(self,CustomerInvoiceLineItem,TotalAmount):
			self.CustomerInvoiceLineItem=CustomerInvoiceLineItem
			self.TotalAmount=TotalAmount
	rate_adjusted_line_items= []
	
	for line_item in relevant_invoice_lineitems: 
			current_rate = line_item.get_resource_rate()['rate_to_customer']
			total_amount = line_item.TotalHours * current_rate
			current_item = rate_adjusted_line_item(rate_adjusted_line_item,total_amount)
			rate_adjusted_line_items.append(current_item)
	
	invoice_total = sum(rate_adjusted_line_item.TotalAmount for rate_adjusted_line_item in rate_adjusted_line_items)
	hours_total = relevant_invoice_lineitems.aggregate(Sum('TotalHours'))['TotalHours__sum']
	
	#totals 
	totals=({"invoice_total" : Money(invoice_total,'USD'),#remove hardcode of USD later
	"hours_total": round(hours_total,2)})
	return totals