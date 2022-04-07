from django.template import loader,Context, Template
from .models import PartnerInvoice,CustomerInvoice,PartnerInvoice
from django.http import HttpResponse
from django.shortcuts import render

def side_by_side(request,invoice_number):
	context=get_side_by_side_data(invoice_number)
	
	return render(request=request, template_name='InvoicingWeb/SideBySide.html',context=context)
	
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