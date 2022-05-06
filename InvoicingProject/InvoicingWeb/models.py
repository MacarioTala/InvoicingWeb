from django.db import models
from ckeditor.fields import RichTextField
from djmoney.models.fields import MoneyField,Money
from django.db.models import Sum, Q


# Create your models here.
class Resource(models.Model):
	ResourceId=models.AutoField(primary_key=True)
	ResourceName=models.CharField(max_length=100,unique=True)
	ResourceEmail=models.CharField(max_length=100,unique=True)
	
	def __str__(self) -> str:
		return self.ResourceName
	
class Remittance(models.Model):
	RemittanceId=models.AutoField(primary_key=True)
	RemittanceDate=models.DateField(null=True)
	RemittanceConfirmationCode=models.CharField(blank=True,max_length=50)
	RemittanceAmount=models.DecimalField(max_digits=12,decimal_places=2,default=0.00)
	
	def __str__(self)-> str:
		return str(self.RemittanceDate) + "-" + str(self.RemittanceAmount)

#customer stuff	
class Customer(models.Model):
	CustomerId=models.AutoField(primary_key=True)
	CustomerName=models.CharField(max_length=100,unique=True)
	CustomerAcronym=models.CharField(max_length=10)
	
	def __str__(self) -> str:
		return self.CustomerName
	
	def get_resource_rates(self):
		return ResourceRate.objects.filter(Customer__CustomerId=self.CustomerId)
	
class CustomerInvoice(models.Model):
	InvoiceId=models.AutoField(primary_key=True)
	InvoiceNumber=models.CharField(max_length=30)
	InvoiceIssueDate=models.DateField(null=True)
	InvoiceFromDate=models.DateField(null=True)
	InvoiceToDate=models.DateField(null=True)
	InvoicePaidDate=models.DateField(null=True)
	InvoiceCustomer=models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
	InvoiceURL=models.URLField(max_length=200)
	AmountOnInvoice=MoneyField(max_digits=14, decimal_places=2, default_currency='USD',null=True)
	
	def just_the_invoice_number(self)->int:
		mts='MTS-'
		acronym=self.InvoiceCustomer.CustomerAcronym
		start_of_invoice_number=len(mts)+len(acronym)+1
		
		return int(self.InvoiceNumber[start_of_invoice_number:])
	
	def __str__(self) -> str:
		return self.InvoiceNumber
	
	def get_next_customer_invoice_number(self) ->str:
		invoice_numbers=[]
		for x in self.objects.all():
			invoice_numbers.append(x.just_the_invoice_number())
		return max(invoice_numbers)+1
	
	def get_invoice_total(self):
		relevant_invoice_lineitems = CustomerInvoiceLineItem.objects.filter(CustomerInvoice__InvoiceNumber=self.InvoiceNumber)
		
		class rate_adjusted_line_item:
			def __init__(self,CustomerInvoiceLineItem,TotalAmount):
				self.CustomerInvoiceLineItem=CustomerInvoiceLineItem
				self.TotalAmount=TotalAmount
		
		rate_adjusted_line_items= []
		
		for line_item in relevant_invoice_lineitems: 
			current_rate = line_item.get_resource_rate()['rate_to_customer']
			total_amount = line_item.TotalHours * current_rate
			current_item = rate_adjusted_line_item(rate_adjusted_line_item,total_amount)
			rate_adjusted_line_items.append(current_item)
	
		invoice_total = sum(rate_adjusted_line_item.TotalAmount for rate_adjusted_line_item in rate_adjusted_line_items)
		hours_total = relevant_invoice_lineitems.aggregate(Sum('TotalHours'))['TotalHours__sum']
		
		#totals 
		totals=({"invoice_total" : Money(invoice_total,'USD'),#remove hardcode of USD later
		"hours_total": round(hours_total,2)})
		return totals	

class CustomerInvoiceLineItem(models.Model):
	CInvoiceLineItemId=models.AutoField(primary_key=True)
	CustomerInvoice=models.ForeignKey(CustomerInvoice,on_delete=models.CASCADE)
	Resource=models.ForeignKey(Resource, on_delete=models.DO_NOTHING,null=True)
	TotalHours=models.DecimalField(max_digits=12,decimal_places=2)
	Comments=models.CharField(max_length=127,null=True,blank=True)
	
	def get_resource_rate(self):
		try:
			relevant_ResourceRate_object = ResourceRate.objects.get(Q(Customer__CustomerId=self.CustomerInvoice.InvoiceCustomer.CustomerId) 
			& Q(Resource__ResourceId=self.Resource.ResourceId))
		except ResourceRate.DoesNotExist:
			relevant_ResourceRate_object = None
		rate_to_customer=relevant_ResourceRate_object.RateToCustomer if relevant_ResourceRate_object is not None else 0
		transfer_rate=relevant_ResourceRate_object.TransferRate if relevant_ResourceRate_object is not None else 0
		context= { "rate_to_customer" : rate_to_customer,"transfer_rate" : transfer_rate}
		return context

#partner stuff
class Partner(models.Model):
	PartnerId=models.AutoField(primary_key=True)
	PartnerName=models.CharField(max_length=30)
	
	def __str__(self) -> str:
		return self.PartnerName

class PartnerInvoice(models.Model):
	InvoiceId=models.AutoField(primary_key=True)
	InvoiceNumber=models.CharField(max_length=30)
	InvoiceIssueDate=models.DateField(null=True)
	InvoiceFromDate=models.DateField(null=True)
	InvoiceToDate=models.DateField(null=True)
	InvoicePartner=models.ForeignKey(Partner, on_delete=models.DO_NOTHING)
	InvoiceURL=models.URLField(max_length=200)
	CustomerInvoice=models.OneToOneField(CustomerInvoice,on_delete=models.DO_NOTHING)
	CoveredByRemittance=models.ForeignKey(Remittance,on_delete=models.DO_NOTHING,null=True,blank=True)
	AmountOnInvoice=MoneyField(max_digits=14, decimal_places=2, default_currency='USD',null=True)
		
	def __str__(self) -> str:
		return self.InvoiceNumber
	
	def get_rate_computed_invoice_total(self):
		relevant_invoice_lineitems = PartnerInvoiceLineItem.objects.filter(PartnerInvoice__InvoiceNumber=self.InvoiceNumber)
		current_customer_id=relevant_invoice_lineitems.first().PartnerInvoice.CustomerInvoice.InvoiceCustomer.CustomerId
	
		class rate_adjusted_line_item:
			def __init__(self, InvoiceLineItem, TotalAmount):
				self.InvoiceLineItem=InvoiceLineItem
				self.TotalAmount=TotalAmount
			
		rate_adjusted_line_items=[]
	
		for line_item in relevant_invoice_lineitems: #you are here
			current_rate = line_item.get_resource_rate()
			
			current_matching_customer_line_item=line_item.get_matching_customer_invoice_line_item()
			total_amount = (line_item.get_matching_customer_invoice_line_item().TotalHours * current_rate ) if current_matching_customer_line_item else 0
			
			current_item = rate_adjusted_line_item(rate_adjusted_line_item,total_amount)
			rate_adjusted_line_items.append(current_item)
	
		invoice_total = sum(rate_adjusted_line_item.TotalAmount for rate_adjusted_line_item in rate_adjusted_line_items)
	
		hours_total = relevant_invoice_lineitems.aggregate(Sum('TotalHours'))['TotalHours__sum']
	
		#totals 
		totals=({"invoice_total" : Money(invoice_total,'USD'),#remove hardcode of USD later,
		"hours_total": round(hours_total,2)})
		return totals	

class PartnerInvoiceLineItem(models.Model):
	PILineItemId=models.AutoField(primary_key=True)
	PartnerInvoice=models.ForeignKey(PartnerInvoice,on_delete=models.CASCADE)
	Resource=models.ForeignKey(Resource, on_delete=models.DO_NOTHING)
	TotalHours=models.DecimalField(max_digits=12,decimal_places=2)
	Rate=models.DecimalField(max_digits=14,decimal_places=2)
	TotalAmount=models.DecimalField(max_digits=14,decimal_places=2)
	Comments=models.CharField(max_length=127,null=True,blank=True)	
    
	def StatedAmount(self):
		return self.TotalHours*self.Rate
	
	def	ComputedAmount(self):
		relevant_line_item=self.get_matching_customer_invoice_line_item()
		return relevant_line_item.TotalHours * self.get_resource_rate()
	
	def get_resource_rate(self):
		try:
			relevant_ResourceRate_object = ResourceRate.objects.get(Q(Customer__CustomerId=self.PartnerInvoice.CustomerInvoice.InvoiceCustomer.CustomerId) 
			& Q(Resource__ResourceId=self.Resource.ResourceId))
		except ResourceRate.DoesNotExist:
			relevant_ResourceRate_object = None
		
		rate_to_customer=relevant_ResourceRate_object.RateToCustomer if relevant_ResourceRate_object is not None else 0
		transfer_rate=relevant_ResourceRate_object.TransferRate if relevant_ResourceRate_object is not None else 0
		
		return transfer_rate
		
	def get_matching_customer_invoice_line_item(self):
		try:
			matching_line_item=self.PartnerInvoice.CustomerInvoice.customerinvoicelineitem_set.filter(Resource__ResourceId=self.Resource.ResourceId).get()
		except PartnerInvoice.DoesNotExist:
			matching_line_item=None
		except CustomerInvoiceLineItem.DoesNotExist:
			matching_line_item=None
		return matching_line_item
	

#project Stuff
class Project(models.Model):
	ProjectId=models.AutoField(primary_key=True)
	ProjectName=models.CharField(max_length=200, blank=False,null=False)
	ProjectCustomer=models.ForeignKey(Customer,on_delete=models.DO_NOTHING)
	
	def __str__(self) -> str:
		return self.ProjectName
	
class ResourceRate(models.Model):
	ProjectResourceId=models.AutoField(primary_key=True)
	Resource=models.ForeignKey(Resource, on_delete=models.DO_NOTHING)
	Project=models.ForeignKey(Project,on_delete=models.DO_NOTHING,null=True)
	Customer=models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
	RateToCustomer=models.DecimalField(max_digits=14,decimal_places=2)
	TransferRate=models.DecimalField(max_digits=14,decimal_places=2)
	FromDate=models.DateField(null=True)
	ToDate=models.DateField(null=True)

	def __str__(self) -> str:
		return self.Resource.ResourceName + " " + self.Customer.CustomerName