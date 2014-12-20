from expense_code_definitions.models import *
"""
Given an expense code, or part of an expense code, 
look up as much of the code as possible.
"""
NOT_FOUND = '-- Not Found --'
class NotFoundEC:
    def __init__(self, value, desc):
        self.value = value
        self.desc = desc
        self.NOT_FOUND = True
        
class ExpenseCodeDefined:
    """
    tub, org, obj, fund, act, sub, root 
    lst = 'Tub Org Object Fund Activity SubActivity Root'.split()
    """
    def __init__(self, tub=None, org=None, obj=None, fund=None, act=None, sub=None, root=None):
        self.ec_attrs = """tub org obj fund activity subactivity root""".split()

        self.tub = self.define_ec_part('Tub', tub)
        self.org = self.define_ec_part('Org', org)
        self.obj = self.define_ec_part('Object', obj)
        self.fund = self.define_ec_part('Fund', fund)
        self.activity = self.define_ec_part('Activity', act)
        self.subactivity = self.define_ec_part('SubActivity', sub, parent_val=act)
        self.root = self.define_ec_part('Root', root)
        
    def get_ec_str(self):
        ec_parts = []
        for attr in self.ec_attrs:
            val = self.__dict__.get(attr, None)
            if val is None:
                return None
            ec_parts.append(val.value)
        return '-'.join(ec_parts)
        
    def get_ec_description_dict(self):
        d = {}
        for attr in self.ec_attrs:
            val = self.__dict__.get(attr, None)
            #print '%s -> [%s]' % (attr, val)
            if val is None:
                d.update({ attr : None })
            else:
                d.update({ attr : val.desc })
        return d

    
    @staticmethod
    def load_ec_str(ec_str):
        if ec_str is None or not len(ec_str) == 33:
            return
        
        return ExpenseCodeDefined(tub=ec_str[0:3], \
                            org=ec_str[3:8],                     \
                            obj=ec_str[8:12], \
                            fund=ec_str[12:18], \
                            act=ec_str[18:24], \
                            sub=ec_str[24:28], \
                            root=ec_str[28:33], \
        )
            
            
        
    def define_ec_part(self, class_prefix, val, parent_val=None):
        if val is None or str(val).strip() == '':
            return None
            
        CLASS_NAME = eval('%sValue' % class_prefix)
        
        
        try:
            if class_prefix == 'SubActivity':
                if parent_val is None or parent_val == '':
                    sub_activity_cnt = CLASS_NAME.objects.filter(value=val).count()
                    if sub_activity_cnt == 0:
                        return NotFoundEC(val, NOT_FOUND)
                    elif sub_activity_cnt == 1:
                        obj = CLASS_NAME.objects.get(value=val)
                    else:
                        return NotFoundEC(val, '%s Subactivities have this value [%s]. Please enter an Activity to narrow it down.  ' % (  CLASS_NAME.objects.filter(value=val).count(), val))
                else:
                    obj = CLASS_NAME.objects.get(value=val, parent_value=parent_val)
            else:
                obj = CLASS_NAME.objects.get(value=val)
            return obj
        except CLASS_NAME.DoesNotExist:
            return NotFoundEC(val, NOT_FOUND)
            #return '%s not found for %s' % (val, CLASS_NAME)
            
