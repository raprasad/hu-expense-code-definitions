from django import forms

from expense_code_definitions.models import *
import re

def digit_match(num_digits, val):
    if re.match('^\d{%s}$' % num_digits, val):
        return val    
    raise forms.ValidationError('Please enter a %s-digit code.' % num_digits)

class TubValueForm(forms.ModelForm):
    class Meta:
        model = TubValue

    def clean_value(self):
        return digit_match(3, self.cleaned_data["value"])


class OrgValueForm(forms.ModelForm):
    class Meta:
        model = OrgValue

    def clean_value(self):
        return digit_match(5, self.cleaned_data["value"])


class ObjectValueForm(forms.ModelForm):
    class Meta:
        model = ObjectValue

    def clean_value(self):
        return digit_match(4, self.cleaned_data["value"])


class FundValueForm(forms.ModelForm):
    class Meta:
        model = FundValue

    def clean_value(self):
        return digit_match(6, self.cleaned_data["value"])


class ActivityValueForm(forms.ModelForm):
    class Meta:
        model = ActivityValue

    def clean_value(self):
        return digit_match(6, self.cleaned_data["value"])


class SubActivityValueForm(forms.ModelForm):
    class Meta:
        model = SubActivityValue

    def clean_value(self):
        return digit_match(4, self.cleaned_data["value"])


class RootValueForm(forms.ModelForm):
    class Meta:
        model = RootValue

    def clean_value(self):
        return digit_match(5, self.cleaned_data["value"])

'''
def get_class_def(model, digits):
    return """
class %sValueForm(forms.ModelForm):
    class Meta:
        model = %sValue

    def clean_root(self):
        return digit_match(%s, self.cleaned_data["value"])
    """ % (model, model, digits)

lst = 'Tub Org Object Fund Activity SubActivity Root'.split()
lst2 = '3 5 4 6 6 4 5'.split()
for idx in range(0, len(lst)):
    print get_class_def(lst[idx], lst2[idx])


'''

