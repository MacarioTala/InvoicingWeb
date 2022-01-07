from django.db import models
from ckeditor.fields import RichTextField
from djmoney.models.fields import MoneyField


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

#customer stuff	
class Customer(models.Model):
    CustomerId=models.AutoField(primary_key=True)
    CustomerName=models.CharField(max_length=100,unique=True)
    CustomerAcronym=models.CharField(max_length=10)
	
    def __str__(self) -> str:
	    return self.CustomerName
	
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

class CustomerInvoiceLineItem(models.Model):
    CInvoiceLineItemId=models.AutoField(primary_key=True)
    CustomerInvoice=models.ForeignKey(CustomerInvoice,on_delete=models.CASCADE)
    Resource=models.ForeignKey(Resource, on_delete=models.DO_NOTHING,null=True)
    TotalHours=models.DecimalField(max_digits=12,decimal_places=2)
    Comments=models.CharField(max_length=127,null=True,blank=True)

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

class PartnerInvoiceLineItem(models.Model):
    PILineItemId=models.AutoField(primary_key=True)
    PartnerInvoice=models.ForeignKey(PartnerInvoice,on_delete=models.CASCADE)
    Resource=models.ForeignKey(Resource, on_delete=models.DO_NOTHING)
    TotalHours=models.DecimalField(max_digits=12,decimal_places=2)
    Rate=MoneyField(max_digits=14, decimal_places=2, default_currency='USD',null=True)
    TotalAmount=MoneyField(max_digits=14, decimal_places=2, default_currency='USD',null=True)
    Comments=models.CharField(max_length=127,null=True,blank=True)	

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