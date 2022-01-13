from django.template import loader,Context, Template
from .models import Partner,PartnerInvoice,PartnerInvoiceLineItem
from django.http import HttpResponse
from django.db.models import Sum, Q
from djmoney.money import Money
from django.shortcuts import render

def partner_invoice_detail(request,invoice_number):
	context = get_partner_invoice_detail_data(invoice_number)
	template_name='InvoicingWeb/PartnerInvoiceDetail.html'
	
	return render(request=request,template_name=template_name,context=context)

def get_partner_invoice_detail_data(invoice_number):
	#data
	relevant_invoice = PartnerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems=PartnerInvoiceLineItem.objects.filter(PartnerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber)
	computed_total=0
	hours_total=0
	display_items=[]
	
	class display_line_item:
		def __init__(self,line_item,amount):
			self.line_item=line_item
			self.amount=amount
	
	for line_item in relevant_invoice_lineitems:
		current_amount=line_item.ComputedAmount()
		
		display_items.append(display_line_item(line_item=line_item,amount=current_amount))
		
		computed_total=computed_total+(current_amount)
		hours_total=hours_total+(line_item.TotalHours)
	
	#display
	context=({"invoice" : relevant_invoice, 
	"computed_total" : computed_total, 
	"invoice_line_items": display_items, #this is somehow not being sent to the view
	"invoice_hours_total":hours_total}) 
	
	return context