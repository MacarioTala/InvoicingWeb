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
		def __init__(self,EffectiveYear,EffectiveMonth, CustomerInvoiceNumber,PartnerInvoiceNumber):
			self.CustomerInvoiceNumber=CustomerInvoiceNumber
			self.PartnerInvoiceNumber=PartnerInvoiceNumber
			self.EffectiveMonth=EffectiveMonth
			self.EffectiveYear=EffectiveYear
			
	invoice_list=[]
	for customer_invoice in customer_invoice_list:
		partner_invoice_number=partner_invoice_list.filter(CustomerInvoice__InvoiceNumber=customer_invoice.InvoiceNumber).first()		
		current_year=customer_invoice.InvoiceFromDate.year
		current_month=customer_invoice.InvoiceFromDate.month
		current_invoice=inner_invoice(CustomerInvoiceNumber=customer_invoice.InvoiceNumber, PartnerInvoiceNumber=partner_invoice_number,
		EffectiveYear=current_year, EffectiveMonth=current_month)
		invoice_list.append(current_invoice)
	
	context = {	"customer_name":customer_name,
	"invoice_list" : invoice_list}
	return context