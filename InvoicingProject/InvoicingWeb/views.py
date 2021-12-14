from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader,Context, Template
from django.db.models import Sum, Q
from .models import Customer,CustomerInvoice,CustomerInvoiceLineItem
from .models import Partner,PartnerInvoice,PartnerInvoiceLineItem,ResourceRate
from djmoney.models.fields import MoneyField
from djmoney.money import Money
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
	
#get all invoices of a customer
def customer_invoices(request,customer_name):
	template=loader.get_template('InvoicingWeb/CustomerInvoice.html')
	
	context = get_customer_invoice_data(customer_name)
	
	return HttpResponse(template.render(context,request))
	
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
	
def partner_invoice_detail(request,invoice_number):
	context = get_partner_invoice_detail_data(invoice_number)
	template_name='InvoicingWeb/PartnerInvoiceDetail.html'
	
	return render(request=request,template_name=template_name,context=context)

def customer_invoice_detail(request,invoice_number):
	#data
	relevant_invoice = CustomerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems = CustomerInvoiceLineItem.objects.filter(CustomerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber)
	invoice_total = customer_invoice_totals(invoice_number)["invoice_total"]
	hours_total = customer_invoice_totals(invoice_number)["hours_total"]
	partner_invoice="" #is there a better way to do empty strings in Python?
	if PartnerInvoice.objects.filter(CustomerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber).exists():
		partner_invoice = PartnerInvoice.objects.filter(CustomerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber).get()
	
	#display
	context=({"invoice" : relevant_invoice, 
	"invoice_total" : invoice_total,
	"invoice_line_items": relevant_invoice_lineitems,
	"invoice_hours_total":hours_total,
	"partner_invoice": partner_invoice}) 
	return render(request=request, template_name='InvoicingWeb/CustomerInvoiceDetail.html',context=context)

def customer_detail(request,customer_name):
	#data
	customer=Customer.objects.filter(CustomerName=customer_name).get()
	
	#display
	context=({"customer":customer})
	
	return render(request=request,template_name='InvoicingWeb/CustomerDetail.html',context=context)
	
def side_by_side(request,invoice_number):
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

def get_customer_invoice_data(customer_name):
	customer_invoice_list=CustomerInvoice.objects.filter(InvoiceCustomer__CustomerName=customer_name)
	#we currently also need to grab all the partner invoices, because the relationship starts at partner invoice not yet sure if a better way exists. 
	partner_invoice_list=PartnerInvoice.objects.filter(CustomerInvoice__InvoiceCustomer__CustomerName=customer_name)
	
	class inner_invoice:
		def __init__(self,CustomerInvoiceNumber,PartnerInvoiceNumber):
			self.CustomerInvoiceNumber=CustomerInvoiceNumber
			self.PartnerInvoiceNumber=PartnerInvoiceNumber
			
	invoice_list=[]
	for customer_invoice in customer_invoice_list:
		partner_invoice_number=partner_invoice_list.filter(CustomerInvoice__InvoiceNumber=customer_invoice.InvoiceNumber).first()		
		current_invoice=inner_invoice(CustomerInvoiceNumber=customer_invoice.InvoiceNumber, PartnerInvoiceNumber=partner_invoice_number)
		invoice_list.append(current_invoice)
	
	context = {	"customer_name":customer_name,
	"invoice_list" : invoice_list}
	return context

def get_partner_invoice_detail_data(invoice_number):
	#data
	relevant_invoice = PartnerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems=PartnerInvoiceLineItem.objects.filter(PartnerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber)
	invoice_total=partner_invoice_totals(invoice_number)["invoice_total"] 
	hours_total=partner_invoice_totals(invoice_number)["hours_total"] 
	
	#display
	context=({"invoice" : relevant_invoice, 
	"invoice_total" : invoice_total, 
	"invoice_line_items": relevant_invoice_lineitems,
	"invoice_hours_total":hours_total}) 
	
	return context
	
def get_resource_rate(resource_id, customer_id):
	relevant_ResourceRate_object = ResourceRate.objects.get(Q(Customer__CustomerId=customer_id) & Q(Resource__ResourceId=resource_id))
	rate_to_customer=relevant_ResourceRate_object.RateToCustomer
	transfer_rate=relevant_ResourceRate_object.TransferRate
	
	context= { "rate_to_customer" : rate_to_customer,
	"transfer_rate" : transfer_rate}
	
	return context

def customer_invoice_totals(invoice_number):
	relevant_invoice = CustomerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems = CustomerInvoiceLineItem.objects.filter(CustomerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber)
	
	class rate_adjusted_line_item:
		def __init__(self,CustomerInvoiceLineItem,TotalAmount):
			self.CustomerInvoiceLineItem=CustomerInvoiceLineItem
			self.TotalAmount=TotalAmount
	rate_adjusted_line_items= []
	
	for line_item in relevant_invoice_lineitems: #This is very DB heavy, refactor this later. This is one hit per line_item
			current_rate = get_resource_rate(customer_id=line_item.CustomerInvoice.InvoiceCustomer.CustomerId,
			resource_id=line_item.Resource.ResourceId)['rate_to_customer']
			total_amount = line_item.TotalHours * current_rate
			current_item = rate_adjusted_line_item(rate_adjusted_line_item,total_amount)
			rate_adjusted_line_items.append(current_item)
	
	invoice_total = sum(rate_adjusted_line_item.TotalAmount for rate_adjusted_line_item in rate_adjusted_line_items)
	hours_total = relevant_invoice_lineitems.aggregate(Sum('TotalHours'))['TotalHours__sum']
	
	#totals 
	totals=({"invoice_total" : Money(invoice_total,'USD'),#remove hardcode of USD later
	"hours_total": round(hours_total,2)})
	return totals

def partner_invoice_totals(invoice_number):
	relevant_invoice = PartnerInvoice.objects.filter(InvoiceNumber=invoice_number).get()
	relevant_invoice_lineitems = PartnerInvoiceLineItem.objects.filter(PartnerInvoice__InvoiceNumber=relevant_invoice.InvoiceNumber)
	current_customer_id=relevant_invoice_lineitems.first().PartnerInvoice.CustomerInvoice.InvoiceCustomer.CustomerId
	
	class rate_adjusted_line_item:
		def __init__(self, InvoiceLineItem, TotalAmount):
			self.InvoiceLineItem=InvoiceLineItem
			self.TotalAmount=TotalAmount
	rate_adjusted_line_items=[]
	
	for line_item in relevant_invoice_lineitems: #This is very DB heavy, refactor this later. This is one hit per line_item
			current_rate = get_resource_rate(customer_id=current_customer_id,
			resource_id=line_item.Resource.ResourceId)['transfer_rate']
			total_amount = line_item.TotalHours * current_rate
			current_item = rate_adjusted_line_item(rate_adjusted_line_item,total_amount)
			rate_adjusted_line_items.append(current_item)
	
	invoice_total = sum(rate_adjusted_line_item.TotalAmount for rate_adjusted_line_item in rate_adjusted_line_items)
	hours_total = relevant_invoice_lineitems.aggregate(Sum('TotalHours'))['TotalHours__sum']
	
	#totals 
	totals=({"invoice_total" : Money(invoice_total,'USD'),#remove hardcode of USD later
	"hours_total": round(hours_total,2)})
	return totals	
	
