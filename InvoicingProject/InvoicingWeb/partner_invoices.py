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
	
	#Annual Totals
	class annual_total:
		def __init__(self,year,stated_total,computed_total):
			self.year=year
			self.stated_total=stated_total
			self.computed_total=computed_total
			
	annual_totals=[]
	for invoice in invoice_list:
		if invoice.EffectiveYear not in (temp.year for temp in annual_totals):
			current_stated_total=sum((invoice.StatedTotal for invoice in [x for x in invoice_list if x.EffectiveYear==invoice.EffectiveYear]))
			current_computed_total=sum((invoice.ComputedTotal for invoice in [x for x in invoice_list if x.EffectiveYear==invoice.EffectiveYear]))
			current_total=annual_total(year=invoice.EffectiveYear, computed_total=current_computed_total ,stated_total= current_stated_total)
			annual_totals.append(current_total)
	
	context = {	"partner_name":partner_name,
	"invoice_list" : invoice_list,
	"annual_totals" : annual_totals}
	return context