from django.template import loader,Context, Template
from .models import PartnerInvoice,CustomerInvoice,PartnerInvoice
from django.http import HttpResponse
from django.shortcuts import render
from .side_by_side_summary import get_customer_side_by_side_data 
from .models import Customer

def side_by_side_all(request):
	template=loader.get_template('InvoicingWeb/SideBySideAll.html')
	
	context = prepare_side_by_side_data_all()
	
	return HttpResponse(template.render(context,request)) 

	
def prepare_side_by_side_data_all():
	customers=Customer.objects.all().values_list("CustomerName",flat=True)
	
	side_by_side_all_list=[]
	#overall totals -- find a cleaner way to sum all revenue
	revenue_total=0
	for customer in customers:
		current_datapoint=get_customer_side_by_side_data(customer)
		revenue_total=revenue_total+current_datapoint["customer_revenue_total"]
		side_by_side_all_list.append(current_datapoint)
	
	context={"side_by_side_all_list" : side_by_side_all_list,
	"revenue_total":revenue_total}
	
	return context