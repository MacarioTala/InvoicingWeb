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
	for line_item in relevant_invoice_lineitems:
		computed_total=computed_total+(line_item.ComputedAmount())
		hours_total=hours_total+(line_item.TotalHours)
	
	#display
	context=({"invoice" : relevant_invoice, 
	"computed_total" : computed_total, 
	"invoice_line_items": relevant_invoice_lineitems,
	"invoice_hours_total":hours_total}) 
	
	return context