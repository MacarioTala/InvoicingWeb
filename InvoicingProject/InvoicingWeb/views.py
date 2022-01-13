from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader,Context, Template
from django.db.models import Sum, Q
from .models import Customer,CustomerInvoice,CustomerInvoiceLineItem
from .models import Partner,PartnerInvoice,PartnerInvoiceLineItem,ResourceRate
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from django.db.models import Max

#the views below are in files with the same names
from .customer_invoices import customer_invoices,get_customer_invoice_data
from .generated_partner_invoice import generated_partner_invoice
from .partner_invoice_detail import partner_invoice_detail
from .customer_invoice_detail import customer_invoice_detail

# Create your views here.

def index(request):
	#data
	#display
	context=({})
	return render(request=request, template_name='InvoicingWeb/Index.html',context=context)

#get all customers
def customers(request):
	#data
	customer_list=Customer.objects.order_by('CustomerName')
	
	#display
	context=({"customer_list": customer_list})

	return render(request=request,template_name='InvoicingWeb/Customers.html',context=context)
	
#get all partners
def partners(request):
	#data
	partner_list=Partner.objects.order_by('PartnerName')
	
	#display
	context=({"partner_list": partner_list})

	return render(request=request,template_name='InvoicingWeb/Partners.html',context=context)
		
def customer_invoices_side_by_side(request,customer_name):
	template=loader.get_template('InvoicingWeb/SideBySideSummary.html')
	
	context = get_customer_side_by_side_data(request,customer_name)
	
	return HttpResponse(template.render(context,request)) 

def partner_invoices(request,partner_name):
	partner_invoice_list=PartnerInvoice.objects.filter(InvoicePartner__PartnerName=partner_name)
	template_name='InvoicingWeb/PartnerInvoice.html'
	
	context = {"invoice_list" : partner_invoice_list,
	"partner_name":partner_name}
	
	return render(request=request,template_name=template_name,context=context)

def customer_detail(request,customer_name):
	#data
	customer=Customer.objects.filter(CustomerName=customer_name).get()
	
	#display
	context=({"customer":customer})
	
	return render(request=request,template_name='InvoicingWeb/CustomerDetail.html',context=context)
	
def side_by_side(request,invoice_number):
	context=get_side_by_side_data(invoice_number)
	
	return render(request=request, template_name='InvoicingWeb/SideBySide.html',context=context)


#functions	
def get_customer_side_by_side_data(request,customer_name):
	class side_by_side_row:
		def __init__(self, CustomerInvoiceNumber, CustomerAmount, PartnerInvoiceNumber,PartnerAmount, Margin):
			self.CustomerInvoiceNumber=CustomerInvoiceNumber
			self.CustomerAmount=CustomerAmount
			self.PartnerInvoiceNumber=PartnerInvoiceNumber
			self.PartnerAmount=PartnerAmount
			self.Margin=Margin
			
	customer_invoices=get_customer_invoice_data(customer_name)["invoice_list"]
	
	side_by_side_list=[]
	
	for customer_invoice in customer_invoices:
		customer_amount=customer_invoice_totals(customer_invoice.CustomerInvoiceNumber)["invoice_total"]
		partner_amount=partner_invoice_totals(customer_invoice.PartnerInvoiceNumber)["invoice_total"] 
		margin=round(((customer_amount.amount-partner_amount.amount)/customer_amount.amount*100),2)
		side_by_side_item=side_by_side_row(CustomerInvoiceNumber=customer_invoice.CustomerInvoiceNumber,PartnerInvoiceNumber=customer_invoice.PartnerInvoiceNumber,CustomerAmount=customer_amount, PartnerAmount=partner_amount,Margin=margin)
		side_by_side_list.append(side_by_side_item)
	
	context= {"side_by_side_list" : side_by_side_list}
	
	return context
	
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
	
	customer_invoice_total = customer_invoice_totals(customer_invoice.InvoiceNumber)["invoice_total"]
	customer_hours_total = customer_invoice_totals(customer_invoice.InvoiceNumber)["hours_total"]
	
	partner_invoice_total = partner_invoice_totals(partner_invoice.InvoiceNumber)["invoice_total"]
	partner_hours_total = partner_invoice_totals(partner_invoice.InvoiceNumber)["hours_total"]
		
	#display
	context=({"customer_invoice" :customer_invoice,
	"customer_invoice_total": customer_invoice_total,
	"customer_hours_total": customer_hours_total ,
	"partner_invoice":partner_invoice,
	"partner_invoice_total": partner_invoice_total ,
	"partner_hours_total": partner_hours_total
	})
	
	return context


def partner_invoice_totals(invoice_number):#This is very DB heavy, refactor this later. This is one hit per line_item
	relevant_invoice = PartnerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems = PartnerInvoiceLineItem.objects.filter(PartnerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber)
	current_customer_id=relevant_invoice_lineitems.first().PartnerInvoice.CustomerInvoice.InvoiceCustomer.CustomerId
	
	
	class rate_adjusted_line_item:
		def __init__(self, InvoiceLineItem, TotalAmount,CalculatedAmountFromInvoiceData):
			self.InvoiceLineItem=InvoiceLineItem
			self.TotalAmount=TotalAmount
			self.CalculatedAmountFromInvoiceData=CalculatedAmountFromInvoiceData
			
	rate_adjusted_line_items=[]
	
	for line_item in relevant_invoice_lineitems: 
			current_rate = line_item.get_resource_rate()['transfer_rate']
			total_amount = line_item.TotalHours * current_rate 
			calculated_amount_from_invoice_data=line_item.TotalHours*line_item.rate.value
			current_item = rate_adjusted_line_item(rate_adjusted_line_item,total_amount)
			rate_adjusted_line_items.append(current_item)
	
	invoice_total = sum(rate_adjusted_line_item.TotalAmount for rate_adjusted_line_item in rate_adjusted_line_items)
	
	hours_total = relevant_invoice_lineitems.aggregate(Sum('TotalHours'))['TotalHours__sum']
	
	#totals 
	totals=({"invoice_total" : Money(invoice_total,'USD'),#remove hardcode of USD later,
	"hours_total": round(hours_total,2)})
	return totals	
	
