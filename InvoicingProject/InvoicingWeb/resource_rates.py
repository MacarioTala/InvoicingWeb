from django.template import loader,Context, Template
from django.shortcuts import render
from .models import ResourceRate,Customer

def resource_rates(request,customer_name=""):
	template_name = 'InvoicingWeb/ResourceRate.html'
	
	if(customer_name):
		resource_rates=Customer.objects.filter(CustomerName=customer_name).first().get_resource_rates()
	else:
		resource_rates=ResourceRate.objects.all()
	
	context={'resource_rates': resource_rates}
	
	return render(request=request,template_name=template_name,context=context)