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
		def __init__(self,EffectiveYear,EffectiveMonth, CustomerInvoice, PartnerInvoice, PartnerComputedAmount,PartnerStatedAmount, Margin):
			self.CustomerInvoice=CustomerInvoice
			self.PartnerInvoice=PartnerInvoice
			self.PartnerComputedAmount=PartnerComputedAmount
			self.PartnerStatedAmount=PartnerStatedAmount
			self.Margin=Margin
			self.EffectiveMonth=EffectiveMonth
			self.EffectiveYear=EffectiveYear
			
	customer_invoices=get_customer_invoice_data(customer_name)["invoice_list"]
	
	side_by_side_list=[]
	#you are here trying to get a left outer join
	for customer_invoice in customer_invoices:
		customer_amount=customer_invoice.InvoiceTotal
		if hasattr(customer_invoice,"PartnerInvoice") and customer_invoice.PartnerInvoice is not None:
			partner_computed_amount=customer_invoice.PartnerInvoice.get_rate_computed_invoice_total()['invoice_total']
			partner_stated_amount=customer_invoice.PartnerInvoice.AmountOnInvoice
			margin=round(((customer_amount.amount-partner_stated_amount.amount)/customer_amount.amount*100),2)
			partner_invoice=customer_invoice.PartnerInvoice
		else:
			partner_invoice=None
			partner_computed_amount=0
			partner_stated_amount=0
			margin=0
	
		side_by_side_item=side_by_side_row(EffectiveYear=customer_invoice.EffectiveYear,
		EffectiveMonth=customer_invoice.EffectiveMonth,
		CustomerInvoice=customer_invoice,
		PartnerInvoice=partner_invoice, 
		PartnerStatedAmount=partner_stated_amount,
		PartnerComputedAmount=partner_computed_amount,
		Margin=margin)

		side_by_side_list.append(side_by_side_item)
			
	#Annual Totals
	class annual_total:
		def __init__(self,Year,RevenueTotal,StatedPartnerTotal,ComputedPartnerTotal):
			self.Year=Year
			self.RevenueTotal=RevenueTotal
			self.StatedPartnerTotal=StatedPartnerTotal
			self.ComputedPartnerTotal=ComputedPartnerTotal
			
	annual_totals=[]
	for item in side_by_side_list:
		if item.EffectiveYear not in (temp.Year for temp in annual_totals):
			revenue_total = sum((item.CustomerInvoice.InvoiceTotal for item in [x for x in side_by_side_list if x.EffectiveYear==item.CustomerInvoice.EffectiveYear]))
			stated_partner_total=sum((item.PartnerStatedAmount for item in [x for x in side_by_side_list if x.EffectiveYear==item.CustomerInvoice.EffectiveYear])) 
			computed_partner_total=sum((item.PartnerComputedAmount for item in [x for x in side_by_side_list if x.EffectiveYear==item.CustomerInvoice.EffectiveYear])) 
			current_total=annual_total(Year=item.EffectiveYear,RevenueTotal=revenue_total,StatedPartnerTotal=stated_partner_total,ComputedPartnerTotal=computed_partner_total)
			annual_totals.append(current_total)

	#Customer Totals
	customer_revenue_total=sum(item.RevenueTotal for item in [x for x in annual_totals])
	partner_stated_amount_total=sum(item.StatedPartnerTotal for item in [x for x in annual_totals])
	partner_computed_amount_total=sum(item.ComputedPartnerTotal for item in [x for x in annual_totals])
	if customer_revenue_total == 0:
		margin=0
	else:
		margin=round(((customer_revenue_total-partner_stated_amount_total)/customer_revenue_total)*100,2)
	
	context= {"side_by_side_list" : side_by_side_list,
	"annual_totals" : annual_totals,
	"customer_name" : customer_name,
	"partner_stated_amount_total":partner_stated_amount_total,
	"partner_computed_amount_total":partner_computed_amount_total,
	"customer_revenue_total": customer_revenue_total,
	"margin":margin}
	
	
	return context