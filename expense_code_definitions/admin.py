from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from expense_code_definitions.models import *
from expense_code_definitions.forms import *


class TubValueAdmin(admin.ModelAdmin):
    save_on_top = True
    form = TubValueForm
    search_fields = ('desc', 'value', )
    list_filter = ('enabled_flag', 'owning_tub_or_object',)
    
    list_display = ('value', 'desc', 'owning_tub_or_object', 'prefix', 'enabled_flag', 'coa_create_date', 'last_update',  )
admin.site.register(TubValue, TubValueAdmin)

    

class OrgValueAdmin(admin.ModelAdmin):
    save_on_top = True
    form = OrgValueForm
    search_fields = ('desc', 'value', )
    list_filter = ('enabled_flag', 'owning_tub_or_object',)
    
    list_display = ('value', 'desc', 'owning_tub_or_object', 'prefix', 'enabled_flag', 'coa_create_date', 'last_update',  )
admin.site.register(OrgValue, OrgValueAdmin)

    

class ObjectValueAdmin(admin.ModelAdmin):
    save_on_top = True
    form = ObjectValueForm
    search_fields = ('desc', 'value', )
    list_filter = ('enabled_flag', 'owning_tub_or_object',)
    
    list_display = ('value', 'desc', 'owning_tub_or_object', 'prefix', 'enabled_flag', 'coa_create_date', 'last_update',  )
admin.site.register(ObjectValue, ObjectValueAdmin)

    

class FundValueAdmin(admin.ModelAdmin):
    save_on_top = True
    form = FundValueForm
    search_fields = ('desc', 'value', )
    list_filter = ('enabled_flag', 'owning_tub_or_object',)
    
    list_display = ('value', 'desc', 'owning_tub_or_object', 'prefix', 'enabled_flag', 'coa_create_date', 'last_update',  )
admin.site.register(FundValue, FundValueAdmin)

    

class ActivityValueAdmin(admin.ModelAdmin):
    save_on_top = True
    form = ActivityValueForm
    search_fields = ('desc', 'value', )
    list_display = ('value', 'desc', 'owning_tub_or_object', 'prefix', 'enabled_flag', 'coa_create_date', 'last_update',  )
    list_filter = ('enabled_flag', 'owning_tub_or_object')
admin.site.register(ActivityValue, ActivityValueAdmin)

    

class SubActivityValueAdmin(admin.ModelAdmin):
    save_on_top = True
    form = SubActivityValueForm
    search_fields = ('desc', 'value', )
    list_filter = ('enabled_flag', 'owning_tub_or_object',)
    list_display = ('value', 'desc', 'owning_tub_or_object', 'parent_value', 'prefix', 'enabled_flag', 'coa_create_date', 'last_update',  )
admin.site.register(SubActivityValue, SubActivityValueAdmin)

    

class RootValueAdmin(admin.ModelAdmin):
    save_on_top = True
    form = RootValueForm
    search_fields = ('desc', 'value',  )
    list_filter = ('enabled_flag', 'owning_tub_or_object',)
    list_display = ('value', 'desc', 'owning_tub_or_object', 'prefix', 'enabled_flag', 'coa_create_date', 'last_update', 'effective_start_date', 'effective_end_date',  )
admin.site.register(RootValue, RootValueAdmin)





'''
def get_class_def(model, digits):
    return """
class %sValueAdmin(admin.ModelAdmin):
    save_on_top = True
    form = %sValueForm
    search_fields = ('desc', 'value', )
    list_display = ('value', 'desc', )
admin.site.register(%sValue, %sValueAdmin)

    """ % (model, model, model, model)

lst = 'Tub Org Object Fund Activity SubActivity Root'.split()
lst2 = '3 5 4 6 6 4 5'.split()
for idx in range(0, len(lst)):
    print get_class_def(lst[idx], lst2[idx])


'''

