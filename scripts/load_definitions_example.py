import os, sys

potential_paths = """/Users/some-username/mcb-git/mcb-finance-utilities
/Users/some-username/mcb-git/mcb-finance-utilities/finance_utilities'
/Users/raprasad/projects/mcb-git/mcb-finance-utilities
/Users/raprasad/projects/mcb-git/mcb-finance-utilities/finance_utilities
/var/webapps/django/mcb-finance-utilities/finance_utilities
/var/webapps/django/mcb-finance-utilities""".split()

[sys.path.append(pth) for pth in filter(lambda x: os.path.isdir(x), potential_paths)]

import settings
from django.core import management 
management.setup_environ(settings)
from datetime import datetime

from expense_code_definitions.definition_loader import COADefinitionFileLoader

from expense_code_definitions.defn_file_loader_sqlite import SqlLiteDefinitionFileLoader
from expense_code_definitions.defn_file_loader_mysql import MySqlDefinitionFileLoader
from expense_code_definitions.models import *

if __name__ == '__main__':
    #FundValue.objects.all().delete()
    #SubActivityValue.objects.all().delete()
    #segment_file_dir = '/Users/raprasad/HU_GOOGLE_DRIVE/Google Drive/ec_validate/segmentfiles/coa_2011-0713'
    #segment_file_dir = '/Users/some-username/Projects/short_tasks/2011_0713_expcode/segment_files'
    
    segment_file_dir = '/var/webapps/coa_files/coa_2013-0529'
    coa_loader = MySqlDefinitionFileLoader(segment_file_dir)    # prod, fairly quick
    #coa_loader = SqlLiteDefinitionFileLoader(segment_file_dir) # test systems, fairly quick
    #coa_loader = COADefinitionFileLoader(segment_file_dir, commit_in_bulk=True)    # slow load via django

    start_time =  datetime.now()
    coa_loader.process_expense_code_files()
    print ''
    print '=' * 50
    print 'start time:', start_time
    print 'end time:', datetime.now()
   

"""  
drop table expense_code_definitions_subactivityvalue          ;
drop table expense_code_definitions_activityvalue          ;
drop table  expense_code_definitions_fundvalue              ;
drop table  expense_code_definitions_objectvalue            ;
drop table  expense_code_definitions_orgvalue               ;
drop table  expense_code_definitions_rootvalue              ;
drop table expense_code_definitions_tubvalue;
"""
