from django.template import loader,Context, Template
from .models import PartnerInvoice,CustomerInvoice,PartnerInvoice
from django.http import HttpResponse
from django.shortcuts import render
from .customer_invoices import get_customer_invoice_data

def customer_invoices_side_by_side(request,customer_name):
	template=loader.get_template('InvoicingWeb/SideBySideSummary.html')
	
	context = get_customer_side_by_side_data(customer_name)
	
	return HttpResponse(template.render(context,request)) 
	
def get_customer_side_by_side_data(customer_name):
	class side_by_side_row:
		def __init__(self, CustomerInvoiceNumber, CustomerAmount, PartnerInvoiceNumber,PartnerStatedAmount,PartnerComputedAmount, Margin):
			self.CustomerInvoiceNumber=CustomerInvoiceNumber
			self.CustomerAmount=CustomerAmount
			self.PartnerInvoiceNumber=PartnerInvoiceNumber
			self.PartnerStatedAmount=PartnerStatedAmount
			self.PartnerComputedAmount=PartnerComputedAmount
			self.Margin=Margin
			
	customer_invoices=get_customer_invoice_data(customer_name)["invoice_list"]
	
	side_by_side_list=[]
	
	for customer_invoice in customer_invoices:
		customer_amount=customer_invoice.InvoiceTotal
		partner_computed_amount=customer_invoice.PartnerInvoice.get_rate_computed_invoice_total()['invoice_total']
		partner_stated_amount=customer_invoice.PartnerInvoice.AmountOnInvoice
		margin=round(((customer_amount.amount-partner_stated_amount.amount)/customer_amount.amount*100),2)
		
		side_by_side_item=side_by_side_row(CustomerInvoiceNumber=customer_invoice.CustomerInvoiceNumber,
		PartnerInvoiceNumber=customer_invoice.PartnerInvoice.InvoiceNumber,CustomerAmount=customer_amount, 
		PartnerStatedAmount=partner_stated_amount,PartnerComputedAmount=partner_computed_amount,Margin=margin)

		side_by_side_list.append(side_by_side_item)
	
	context= {"side_by_side_list" : side_by_side_list}
	
	return context