import os, sys

from django.db import transaction
from datetime import datetime, date, timedelta
from expense_code_definitions.models import *
from django.db import transaction

def msg(m): print m
def dashes(): msg('-' * 40)
def msgt(m): dashes(); msg(m); dashes()

class COADefinitionFileLoader(object):
    """
    Load COA definition files into the Django models 
    defined in the app "expense_code_defintions"
    """
    ec_file_prefixes_ordered = 'tub org obj fund act sub root'.split()
    ec_obj_prefixes = 'TubValue OrgValue ObjectValue FundValue ActivityValue SubActivityValue RootValue'.split()
    
    EC_OBJ_MAP = dict(zip(ec_file_prefixes_ordered, ec_obj_prefixes))
    MONTH_MAP = dict(zip('JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC'.split() , range(1, 13)))
    
    
    def __init__(self, segment_file_directory, commit_in_bulk=True):
        if not os.path.isdir(segment_file_directory):
            raise Exception("not a diretory: %s" % segment_file_directory )
        
        self.segment_file_directory = segment_file_directory
        self.commit_in_bulk = commit_in_bulk
        self.rows_to_bulk_commit = 5000
        
        
        self.inactive_segment_cutoff_date = date.today() + timedelta(days=-1*365*6)
        
    def fmt_date(self, fdate):
        #print fdate
        if fdate is None or len(fdate.strip()) ==0:
            #print 'no date'
            return None
        #25-NOV-2008
        dd, month, yyyy = fdate.split('-')
        #print dd, month,yyyy
        mm = self.MONTH_MAP.get(month, None)
        #print 'mm', mm
        if mm is None:
            msgx('month not found for: %s' % fdate)
            return None

        #print 'fmt date', date(int(yyyy), int(mm), int(dd))
        return date(int(yyyy), int(mm), int(dd))


    def get_subactivity_object(self, val, parent_val):
       
        try:
            ec_obj = SubActivityValue.objects.get(value=val, parent_value=parent_val)
        except SubActivityValue.DoesNotExist:
            ec_obj = SubActivityValue(value=val, parent_value=parent_activity)

        return ec_obj

    @transaction.commit_manually
    def load_definitions(self, fullname, EC_CLASS):
        """
        Process a definitions file, Load it up and save it to the correct db model
        """
        if fullname is None or EC_CLASS is None:
            return
        
        if EC_CLASS.__name__ in ['TubValue']:   #, 'ObjectValue']:
            self.commit_in_bulk = False
    
        row_cnt =0
        for line in open(fullname, 'r').readlines():
            row_cnt+=1
            print '(%s) Loading: %s'  % (row_cnt, line.strip())
            params = line.split('|')
            if row_cnt % self.rows_to_bulk_commit == 0:
                print '(%s) Loading: %s'  % (row_cnt, line.strip())
            
            if len(params) == 11:   # and row_cnt > 140000:
                process_record = True
                coa_seg_type, val, desc, prefix, owning_tub_object, enabled, create_date, update_date, start_date, end_date, parent_val = line.split('|') 
            
                # strip the last value
                parent_val = parent_val.strip()
            
            
                # set the enabled_flag
                if enabled == 'Y':
                    enabled = True
                else:
                    enabled = False

                last_update = self.fmt_date(update_date)
                if enabled is False and last_update is not None:
                    if last_update < self.inactive_segment_cutoff_date:
                        print '---- IGNORE OLD RECORD ----'
                        continue # go to next record
                            
                try:
                    desc = desc.decode('utf-8', 'ignore')
                except UnicodeDecodeError:
                    print '(%s) >>UnicodeDecodeError<< Loading: %s'  % (row_cnt, line.strip())
                    #desc = pull_out_not_ascii_chars(desc)
                
                kwargs = { 'desc' :  desc\
                    , 'prefix' : prefix\
                    , 'owning_tub_or_object' : owning_tub_object\
                    , 'enabled_flag' : enabled\
                    , 'coa_create_date' :  self.fmt_date(create_date)\
                    , 'last_update' :  last_update\
                    , 'effective_start_date' :  self.fmt_date(start_date)\
                    , 'effective_end_date' :  self.fmt_date(end_date)\
                    }
                print kwargs

               

                if EC_CLASS.__name__  == 'SubActivityValue':
                    try:
                        ec_obj = SubActivityValue.objects.get(value=val, parent_value=parent_val)
                    except SubActivityValue.DoesNotExist:
                        ec_obj = SubActivityValue(value=val, parent_value=parent_val)        
                    kwargs.update({'parent_val':parent_val})            
                else:
                    # Look for an existing object
                    try:
                        ec_obj = EC_CLASS.objects.get(value=val)
                    except EC_CLASS.DoesNotExist:
                        # start new object
                        ec_obj = EC_CLASS(value=val)
                        
                ec_obj.__dict__.update(kwargs)
                ec_obj.save()
                
                if not self.commit_in_bulk: 
                    transaction.commit()
            
                #save_object(ec_obj)
                if row_cnt >1 and (row_cnt % self.rows_to_bulk_commit == 0) and self.commit_in_bulk:
                    print 'committing transactions!'
                    print datetime.now()
                    transaction.commit()
                    print 'done'
                    print datetime.now()
                    

        print 'row_cnt: %s' % row_cnt
        if ((row_cnt % self.rows_to_bulk_commit) > 0) and self.commit_in_bulk:
            print 'committing transactions!'
            print datetime.now()
            transaction.commit()
            print 'done'
            print datetime.now()
        
        # For tubs, owning tubs not necessarily available on the 1st load, so resave them
        if EC_CLASS.__name__ == 'TubValue':
            print 'resave the tubs'
            for tv in EC_CLASS.objects.all():
                tv.save()
            transaction.commit()
    

    #@transaction.commit_manually
    #def save_object(expense_code_object):
    #    expense_code_object.save()

    
    def process_expense_code_files(self):
        """Process expense code files.  
        Load files in this order: tub org obj fund act sub root
        
        Sample file names:
            act.20110713.txt	org.20110713.txt	tub.20110713.txt
            fund.20110713.txt	root.20110713.txt
            obj.20110713.txt	sub.20110713.txt
        
        """
        msgt('process_expense_code_files')
        cnt =0
    
        # retrieve a list of filenames
        ec_fnames = os.listdir(self.segment_file_directory)
        
        # only keep text files
        ec_fnames = filter(lambda x: x.endswith('.txt'), ec_fnames)

        # pull prefix from file names
        ec_fname_prefixes = map(lambda x: x.split('.')[0], ec_fnames)

        # make a {} of { file prefix : file name }; 
        # e.g. { 'tub':'tub20110713.txt'}
        #
        ec_fname_dict = dict(zip(ec_fname_prefixes, ec_fnames))
        # open the files in the correct order
        file_cnt = 0 
        #for file_prefix in ['root']:# 'root']:    
        for file_prefix in self.ec_file_prefixes_ordered:    
            file_cnt +=1
            fname = ec_fname_dict.get(file_prefix, None)
            if fname is not None:
                print '(%s) process file: %s' % (file_cnt, fname)
                fullname = os.path.join(self.segment_file_directory, fname)
                if os.path.isfile(fullname):
                    msg('processing file: %s' % fname)
                    EC_CLASS = self.EC_OBJ_MAP.get(file_prefix, None)
                    if EC_CLASS is not None:  
                        self.load_definitions(fullname, eval(EC_CLASS))
                    
    
if __name__=='__main__':
    #RootValue.objects.all().delete()
    EC_DIR = '/Users/some-username/Projects/short_tasks/2011_0713_expcode/segment_files'
    coa_loader = COADefinitionFileLoader(EC_DIR)
    coa_loader.process_expense_code_files()
    
