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
	stated_total=0
	computed_total=0
	hours_total=0
	display_items=[]
	
	class display_line_item:
		def __init__(self,line_item,stated_amount,computed_amount):
			self.line_item=line_item
			self.stated_amount=stated_amount
			self.computed_amount=computed_amount
	
	for line_item in relevant_invoice_lineitems:
		current_stated_amount=line_item.StatedAmount()
		current_computed_amount=line_item.ComputedAmount()
		
		display_items.append(display_line_item(line_item=line_item,stated_amount=round(current_stated_amount,2)
		,computed_amount=round(current_computed_amount,2)))
		
		stated_total=stated_total+current_stated_amount
		computed_total=computed_total+current_computed_amount
		hours_total=hours_total+line_item.TotalHours
	
	#display
	context=({"invoice" : relevant_invoice, 
	"stated_total" : stated_total, 
	"computed_total" : computed_total,
	"invoice_line_items": display_items, 
	"invoice_hours_total":hours_total}) 
	
	return context