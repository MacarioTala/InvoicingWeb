from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.
class Resource(models.Model):
    ResourceId=models.AutoField(primary_key=True)
    ResourceName=models.CharField(max_length=100)
    ResourceEmail=models.CharField(max_length=100)
	
    def __str__(self) -> str:
	    return self.ResourceName

class Customer(models.Model):
    CustomerId=models.AutoField(primary_key=True)
    CustomerName=models.CharField(max_length=100)
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
	
    def __str__(self) -> str:
	    return self.InvoiceNumber

class CustomerInvoiceLineItem(models.Model):
    CInvoiceLineItemId=models.AutoField(primary_key=True)
    CustomerInvoice=models.ForeignKey(CustomerInvoice,on_delete=models.CASCADE)
    CInvoiceLineItemAmount=models.DecimalField(max_digits=12,decimal_places=2)
    CInvoiceLineItemResource=models.ForeignKey(Resource, on_delete=models.DO_NOTHING)
    CInvoiceLineItemHours=models.DecimalField(max_digits=12,decimal_places=2)
    CInvoiceLineItemComments=models.CharField(max_length=127,null=True,blank=True)

class Project(models.Model):
    ProjectId=models.AutoField(primary_key=True)
    ProjectName=models.CharField(max_length=200, blank=False,null=False)
    ProjectCustomer=models.ForeignKey(Customer,on_delete=models.DO_NOTHING)
	
    def __str__(self) -> str:
	    return self.ProjectName
	
class ProjectResource(models.Model):
    ProjectResourceId=models.AutoField(primary_key=True)
    ProjectResourceProject=models.ForeignKey(Project,on_delete=models.DO_NOTHING)
    ProjectResourceRateToCustomer=models.DecimalField(max_digits=12,decimal_places=2)
    ProjectResourceTransferRate=models.DecimalField(max_digits=12,decimal_places=2)
	

class Partner(models.Model):
    PartnerId=models.AutoField(primary_key=True)
    PartnerName=models.CharField(max_length=30)
	
    def __str__(self) -> str:
	    return self.PartnerName

class Remittance(models.Model):
    RemittanceId=models.AutoField(primary_key=True)
    RemittanceDate=models.DateField(null=True)
    RemittanceConfirmationCode=models.CharField(blank=True,max_length=50)
    RemittanceAmount=models.DecimalField(max_digits=12,decimal_places=2,default=0.00)

class PartnerInvoice(models.Model):
    InvoiceId=models.AutoField(primary_key=True)
    InvoiceNumber=models.CharField(max_length=30)
    InvoiceIssueDate=models.DateField(null=True)
    InvoiceFromDate=models.DateField(null=True)
    InvoiceToDate=models.DateField(null=True)
    InvoicePartner=models.ForeignKey(Partner, on_delete=models.DO_NOTHING)
    InvoiceURL=models.URLField(max_length=200)
    CustomerInvoice=models.ForeignKey(CustomerInvoice,on_delete=models.DO_NOTHING)
    CoveredByRemittance=models.ForeignKey(Remittance,on_delete=models.DO_NOTHING,null=True,blank=True)
		
    def __str__(self) -> str:
	    return self.InvoiceNumber

class PartnerInvoiceLineItem(models.Model):
    PILineItemId=models.AutoField(primary_key=True)
    PILineItemInvoice=models.ForeignKey(PartnerInvoice,on_delete=models.CASCADE)
    PILineItemAmount=models.DecimalField(max_digits=12,decimal_places=2)
    PILineItemResource=models.ForeignKey(Resource, on_delete=models.DO_NOTHING)
    PILineItemHours=models.DecimalField(max_digits=12,decimal_places=2)
    PILineItemComments=models.CharField(max_length=127,null=True,blank=True)
	

	