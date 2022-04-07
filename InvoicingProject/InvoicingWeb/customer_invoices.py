from django.template import loader,Context, Template
from .models import Customer,CustomerInvoice,PartnerInvoice
from django.http import HttpResponse

#get all invoices of a customer
def customer_invoices(request,customer_name):
	template=loader.get_template('InvoicingWeb/CustomerInvoice.html')
	
	context = get_customer_invoice_data(customer_name)
	
	return HttpResponse(template.render(context,request))

def get_customer_invoice_data(customer_name):
	customer_invoice_list=CustomerInvoice.objects.filter(InvoiceCustomer__CustomerName=customer_name).order_by('InvoiceFromDate')
	#we currently also need to grab all the partner invoices, because the relationship starts at partner invoice not yet sure if a better way exists. 
	partner_invoice_list=PartnerInvoice.objects.filter(CustomerInvoice__InvoiceCustomer__CustomerName=customer_name)
	
	class inner_invoice:
		def __init__(self,EffectiveYear,EffectiveMonth, CustomerInvoiceNumber,PartnerInvoice,InvoiceTotal):
			self.CustomerInvoiceNumber=CustomerInvoiceNumber
			self.PartnerInvoice=PartnerInvoice
			self.EffectiveMonth=EffectiveMonth
			self.EffectiveYear=EffectiveYear
			self.InvoiceTotal=InvoiceTotal
			
	invoice_list=[]
	for customer_invoice in customer_invoice_list:
		partner_invoice=customer_invoice.partnerinvoice
		current_year=customer_invoice.InvoiceFromDate.year
		current_month=customer_invoice.InvoiceFromDate.month
		current_invoice=inner_invoice(CustomerInvoiceNumber=customer_invoice.InvoiceNumber, PartnerInvoice=partner_invoice,
		EffectiveYear=current_year, EffectiveMonth=current_month,InvoiceTotal=customer_invoice.get_invoice_total()["invoice_total"])
		invoice_list.append(current_invoice)
	
	#Annual Totals
	class annual_total:
		def __init__(self,Year,Total):
			self.Year=Year
			self.Total=Total
			
	annual_totals=[]
	for invoice in invoice_list:
		if invoice.EffectiveYear not in (temp.Year for temp in annual_totals):
			current_total=annual_total(Year=invoice.EffectiveYear,Total=sum((invoice.InvoiceTotal for invoice in [x for x in invoice_list if x.EffectiveYear==invoice.EffectiveYear])))
			annual_totals.append(current_total)
			
	
	context = {	"customer_name":customer_name,
	"invoice_list" : invoice_list,
	"annual_totals" : annual_totals}
	return context