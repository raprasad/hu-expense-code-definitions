from django.db import models

class CommonCOAInfo(models.Model):
    """
    common fields for the tub, org, obj, fund, act, sub, root classes
    """
    desc = models.CharField('description', max_length=240)
    prefix = models.CharField(max_length=240)
    owning_tub_or_object = models.CharField('Owning Tub or Reclass Object Code', max_length=4, blank=True)
    enabled_flag = models.BooleanField()
    coa_create_date = models.DateField()
    last_update = models.DateField()
    effective_start_date = models.DateField(null=True, blank=True)
    effective_end_date = models.DateField(null=True, blank=True)
    
    class Meta:
        abstract = True

class TubValue(CommonCOAInfo):
    value = models.CharField(max_length=3, unique=True, db_index=True, help_text='3 digits')
    #owning_tub = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    
    def __unicode__(self):
        return '%s - %s' % (self.value, self.desc)   
    
    def save(self, *args, **kwargs):
        super(TubValue, self).save(*args, **kwargs)

    class Meta:
        ordering = ('value',)
        verbose_name = '1 - Tub'
        verbose_name_plural = verbose_name
        db_table = 'ec_defn_tubvalue'

class OrgValue(CommonCOAInfo):
    value = models.CharField(max_length=5, unique=True, db_index=True, help_text='5 digits')
    #owning_tub = models.ForeignKey(TubValue, null=True, blank=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return '%s - %s' % (self.value, self.desc)   

    def save(self, *args, **kwargs):
        super(OrgValue, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ('value',)
        verbose_name = '2 - Org'
        verbose_name_plural = verbose_name
        db_table = 'ec_defn_orgvalue'        



class ObjectValue(CommonCOAInfo):
    value = models.CharField(max_length=4, unique=True, db_index=True, help_text='4 digits')
    #reclass_object_code = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return '%s - %s' % (self.value, self.desc)   

    def save(self, *args, **kwargs):
        super(ObjectValue, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ('value',)
        verbose_name = '3 - Object'
        verbose_name_plural = verbose_name
        db_table = 'ec_defn_objectvalue'     



class FundValue(CommonCOAInfo):
    value = models.CharField(max_length=6, unique=True, db_index=True, help_text='6 digits')
    #owning_tub = models.ForeignKey(TubValue, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        super(FundValue, self).save(*args, **kwargs)


    def __unicode__(self):
        return '%s - %s' % (self.value, self.desc)   

    class Meta:
        ordering = ('value',)
        verbose_name = '4 - Fund'
        verbose_name_plural = verbose_name
        db_table = 'ec_defn_fundvalue'       


class ActivityValue(CommonCOAInfo):
    value = models.CharField(max_length=6, unique=True, db_index=True, help_text='6 digits')
    #owning_tub = models.ForeignKey(TubValue, null=True, blank=True, on_delete=models.SET_NULL)


    def save(self, *args, **kwargs):
        super(ActivityValue, self).save(*args, **kwargs)


    def __unicode__(self):
        return '%s - %s' % (self.value, self.desc)   

    class Meta:
        ordering = ('value',)
        verbose_name = '5 - Activity'
        verbose_name_plural = verbose_name
        db_table = 'ec_defn_activityvalue'



class SubActivityValue(CommonCOAInfo):
    value = models.CharField(max_length=4, db_index=True, help_text='4 digits')
    parent_value = models.CharField(max_length=6, db_index=True, help_text='6 digits')
    #owning_tub = models.ForeignKey(TubValue, null=True, blank=True, on_delete=models.SET_NULL)
 
    def save(self, *args, **kwargs):
        super(SubActivityValue, self).save(*args, **kwargs)

    
    def __unicode__(self):
        return '%s - %s' % (self.value, self.desc)   

    class Meta:
        ordering = ('value',)
        unique_together = ('value', 'parent_value', )
        verbose_name = '6 - SubActivity'
        verbose_name_plural = verbose_name
        db_table = 'ec_defn_subactivityvalue'



class RootValue(CommonCOAInfo):
    value = models.CharField(max_length=5, unique=True, db_index=True, help_text='5 digits')
    #owning_tub = models.ForeignKey(TubValue, null=True, blank=True, on_delete=models.SET_NULL)


    def save(self, *args, **kwargs):
         super(RootValue, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s - %s' % (self.value, self.desc)   

    class Meta:
        ordering = ('value',)
        verbose_name = '7 - Root'
        verbose_name_plural = verbose_name
        db_table = 'ec_defn_rootvalue'       
      
   
'''
def get_class_def(model, digits):
    return """
class %sValue(CommonCOAInfo):
    value = models.CharField(max_length=%s, unique=True, help_text='%s digits')

    def __unicode__(self):
        return 'zzs - zzs' zz (self.value, self.desc)   

    class Meta:
        ordering = ('value',)

    """ % (model, digits, digits)

lst = 'Tub Org Object Fund Activity SubActivity Root'.split()
lst2 = '3 5 4 6 6 4 5'.split()
for idx in range(0, len(lst)):
    print get_class_def(lst[idx], lst2[idx])


'''
