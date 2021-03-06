from django.contrib import admin
from .models import Project,Resource,Customer,CustomerInvoice,CustomerInvoiceLineItem,ResourceRate,Partner,PartnerInvoice,PartnerInvoiceLineItem
from .models import Remittance

#Inlines and custom admins
class PartnerInvoiceLineItemInline(admin.TabularInline):
    model=PartnerInvoiceLineItem
	
class PartnerInvoiceAdmin(admin.ModelAdmin):
    admin.ModelAdmin.actions_on_top
    date_hierarchy='InvoiceIssueDate'
    exclude=('InvoiceAmount',)
    inlines = [PartnerInvoiceLineItemInline]

class CustomerInvoiceLineItemInline(admin.TabularInline):
    model=CustomerInvoiceLineItem

class CustomerInvoiceAdmin(admin.ModelAdmin):
    admin.ModelAdmin.actions_on_top
    exclude=('InvoiceAmount',)
    inlines=[CustomerInvoiceLineItemInline]

# Register your models here.
admin.site.register(Project)
admin.site.register(Resource)
admin.site.register(Customer)
admin.site.register(CustomerInvoice,CustomerInvoiceAdmin)
admin.site.register(ResourceRate)
admin.site.register(PartnerInvoice,PartnerInvoiceAdmin)
admin.site.register(Partner)
admin.site.register(Remittance)