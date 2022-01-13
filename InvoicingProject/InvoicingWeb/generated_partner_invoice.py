from django.template import loader,Context, Template
from .models import Customer,CustomerInvoice,CustomerInvoiceLineItem
from django.http import HttpResponse
from django.db.models import Sum, Q
from djmoney.money import Money
from django.shortcuts import render

def generated_partner_invoice(request,customer_invoice_number): #note Currently not generating partner invoice numbers
	template_name='InvoicingWeb/GeneratedPartnerInvoice.html'
	context=generate_partner_invoice_from_customer_invoice(customer_invoice_number)
	
	return render(request=request,template_name=template_name,context=context)

def generate_partner_invoice_from_customer_invoice(customer_invoice_number):
	relevant_line_items=CustomerInvoiceLineItem.objects.filter(Q(CustomerInvoice__InvoiceNumber=customer_invoice_number))
	relevant_invoice=relevant_line_items.first().CustomerInvoice
	
	#generate line items
	line_items=[]
	
	class line_item:
		def __init__(self,customer_invoice_line_item,Amount,calculated_hours):
			self.customer_invoice_line_item=customer_invoice_line_item
			self.Amount=Amount
			self.calculated_hours=calculated_hours
	
	for relevant_line_item in relevant_line_items:
		rates=relevant_line_item.get_resource_rate()
		transfer_rate=rates['transfer_rate']
		rate_to_customer=rates['rate_to_customer']
		amount=transfer_rate*relevant_line_item.TotalHours
		amount=Money(amount,'USD')
		calculated_hours=round(amount.amount/rate_to_customer,2)
		current_item=line_item(customer_invoice_line_item=relevant_line_item,Amount=amount,calculated_hours=calculated_hours)
		line_items.append(current_item)
	
	invoice_total=sum(line_item.Amount.amount for line_item in line_items)
	
	context=({"customer_invoice" : relevant_invoice,
	"partner_invoice_line_items" : line_items,
	"total_amount" : Money(invoice_total,'USD')
	})
		
	return context