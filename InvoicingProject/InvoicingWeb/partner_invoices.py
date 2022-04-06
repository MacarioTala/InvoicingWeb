from django.template import loader,Context, Template
from .models import Customer,CustomerInvoice,PartnerInvoice
from django.http import HttpResponse

#get all invoices of a customer

def partner_invoices(request,partner_name):
	partner_invoice_list=PartnerInvoice.objects.filter(InvoicePartner__PartnerName=partner_name)
	
	template=loader.get_template('InvoicingWeb/PartnerInvoice.html')
	
	context = get_partner_invoice_data(partner_name)
	
	return HttpResponse(template.render(context,request))
	

def get_partner_invoice_data(partner_name):
	partner_invoice_list=PartnerInvoice.objects.filter(InvoicePartner__PartnerName=partner_name).order_by('InvoiceFromDate')
	
	class inner_invoice:
		def __init__(self,EffectiveYear,EffectiveMonth,InvoiceNumber,CustomerInvoice,ComputedTotal,StatedTotal):
			self.InvoiceNumber=InvoiceNumber
			self.CustomerInvoice=PartnerInvoice
			self.EffectiveMonth=EffectiveMonth
			self.EffectiveYear=EffectiveYear
			self.ComputedTotal=ComputedTotal
			self.StatedTotal=StatedTotal
			
	invoice_list=[]
	for partner_invoice in partner_invoice_list:
		customer_invoice=partner_invoice.CustomerInvoice
		current_year=partner_invoice.InvoiceFromDate.year
		current_month=partner_invoice.InvoiceFromDate.month
		
		current_invoice=inner_invoice(InvoiceNumber=partner_invoice.InvoiceNumber, CustomerInvoice=partner_invoice.CustomerInvoice,
		EffectiveYear=current_year, EffectiveMonth=current_month,StatedTotal=partner_invoice.AmountOnInvoice,ComputedTotal=partner_invoice.get_rate_computed_invoice_total()["invoice_total"])
		
		invoice_list.append(current_invoice)
	
	#Effective Years
	effective_years=[]
	for invoice in invoice_list:
		if invoice.EffectiveYear not in effective_years:
			effective_years.append(invoice.EffectiveYear)
	
	context = {	"partner_name":partner_name,
	"invoice_list" : invoice_list,
	"effective_years" : effective_years}
	return context