import os, sys
from datetime import datetime, date, timedelta
from expense_code_definitions.models import *
from django.conf import settings
import csv, MySQLdb
import subprocess
from datetime import date

def msg(m): print m
def dashes(): msg('-' * 40)
def msgt(m): dashes(); msg(m); dashes()


class MySqlDefinitionFileLoader(object):
    """
    Load COA definition files into sqlite database tables*.  
    Uses direct sqlite connection and 'executemany'
    * database tables defined by django models in app expense_code_definitions
    """
    ec_file_prefixes_ordered = 'tub org obj fund act sub root'.split()
    ec_obj_prefixes = 'TubValue OrgValue ObjectValue FundValue ActivityValue SubActivityValue RootValue'.split()
    
    EC_OBJ_DB_TABLE_MAP = dict(zip(ec_obj_prefixes ,map(lambda x: 'ec_defn_%s' % x.lower(), ec_obj_prefixes)))  # { 'TubValue':'ec_defn_tubvalue', 'OrgValue':'ec_defn_orgvalue', ...}
    
    EC_OBJ_MAP = dict(zip(ec_file_prefixes_ordered, ec_obj_prefixes))  # { 'tub':'TubValue', 'org':'OrgValue', ...}
    MONTH_MAP = dict(zip('JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC'.split() , range(1, 13)))
    
    LOAD_FILE_DELIMITER = '|'
    MAX_ROWS_IN_STMT = 75000
    
    def __init__(self, segment_file_directory, commit_in_bulk=True):
        if not os.path.isdir(segment_file_directory):
            raise Exception("not a directory: %s" % segment_file_directory )
        
        self.segment_file_directory = segment_file_directory
        self.commit_in_bulk = commit_in_bulk
        self.rows_to_bulk_commit = 5000
        
        
        self.inactive_segment_cutoff_date = date.today() + timedelta(days=-1*365*6)
        
    def fmt_date(self, fdate):
        """
        Format for sqlite insert
        in: 25-NOV-2008
        out: 2008-11-25
        """
        if fdate is None or len(fdate.strip()) ==0:
            return None
        dd, month, yyyy = fdate.split('-')
        mm = self.MONTH_MAP.get(month, None)
        if mm is None:
            return None

        return date(int(yyyy), int(mm), int(dd))
        #return '%s-%s-%s' % (yyyy, mm, dd)

    
    def fmt_flag(self, enabled):
        if enabled == 'Y':
            return True
        return False
        

    def load_definitions(self, fullname, EC_CLASS, clear_table=False):
        msg('Attempt to load definitions for %s\nsource: %s ' % (EC_CLASS.__name__, fullname, ))
        """
        example of input file line: 
            "TUB|100|ARB^Arnold Arboretum|ARB^|100|Y|07-JAN-1999|29-MAY-2002|||"
        
        input file line attrs:
            coa_seg_type|val|desc|prefix|owning_tub_object|enabled|create_date|update_date|start_date|end_date|parent_val 
        
        "INSERT INTO expense_code_definitions_tubvalue (value, desc, prefix, owning_tub_or_object, enabled_flag, coa_create_date, last_update, effective_start_date, effective_end_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ? );", to_db
        
        """
        if fullname is None or EC_CLASS is None:
            return
        
        # The input file doesn't have a header line
        input_file_header_fieldnames = "coa_seg_type  value  desc  prefix  owning_tub_object  enabled_flag  coa_create_date  last_update  effective_start_date  effective_end_date  parent_value".split()
        
        # Which table should this data be loaded to?
        DEFN_DB_TABLE_NAME = self.EC_OBJ_DB_TABLE_MAP.get(EC_CLASS.__name__, None)
        if DEFN_DB_TABLE_NAME is None:
            return
        
        # open the database connection
        db_conn = MySQLdb.connect(host=settings.DATABASES['default']['HOST']\
                            , user=settings.DATABASES['default']['USER']\
                            , passwd=settings.DATABASES['default']['PASSWORD']\
                            , db=settings.DATABASES['default']['NAME']\
                            )
        
        #---------------------------------
        # clear table of data of existing data
        #---------------------------------
        db_cursor = db_conn.cursor()
        if clear_table:
            db_cursor.execute('DELETE FROM %s;' % DEFN_DB_TABLE_NAME)   # clear the table! 
            db_conn.commit()
            print '\n(a) table cleared: %s' % DEFN_DB_TABLE_NAME
        #---------------------------------
        # format/load data from file
        #---------------------------------        
        cnt =0 

        with open(fullname, 'rb') as file_input: 
            dr = csv.DictReader(file_input\
                                , fieldnames=input_file_header_fieldnames\
                                , delimiter='|') # comma is default delimiter
            cnt +=1
            
            if EC_CLASS.__name__ == 'SubActivityValue':
                stmt_str = """INSERT INTO %s VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s);""" % DEFN_DB_TABLE_NAME
                db_insert_values = [ self.format_sub_activity_row_info(i) for i in dr]
            else:
                stmt_str = """INSERT INTO %s VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s);""" % DEFN_DB_TABLE_NAME
                db_insert_values = [ self.format_basic_row_info(i, DEFN_DB_TABLE_NAME) for i in dr]
    
            print '(b) attempt to load --%s-- rows' % len(db_insert_values)
            print 'insert_stmt:', stmt_str
    
            if len(db_insert_values) > self.MAX_ROWS_IN_STMT:
                num_execute_runs = len(db_insert_values) / self.MAX_ROWS_IN_STMT
                num_last_load_rows = len(db_insert_values) % self.MAX_ROWS_IN_STMT
                if num_last_load_rows > 0:
                    num_execute_runs +=1
                
                start_idx = 0
                end_idx = self.MAX_ROWS_IN_STMT
                for run_num in range(0, num_execute_runs):
                    if run_num == num_execute_runs -1:
                        print 'Attempt to insert last %s rows, starting at row %s' % (num_last_load_rows, start_idx+1)
                    else:
                        print 'Attempt to insert %s rows, starting at row %s' % (self.MAX_ROWS_IN_STMT, start_idx+1) 
                    # Insert a slice of values, up to MAX_ROWS_IN_STMT rows
                    db_cursor.executemany(stmt_str, db_insert_values[start_idx:end_idx])
                    db_conn.commit()        
                    print '> Done!'

                    # update indexes
                    start_idx = end_idx
                    end_idx += self.MAX_ROWS_IN_STMT 

            else:
                db_cursor.executemany(stmt_str, db_insert_values)
                
                db_conn.commit()        
            db_cursor.close()
            print '(c) table loaded: %s' % DEFN_DB_TABLE_NAME

        db_conn.close()
       
    def get_table_insert_stmt(self, db_table_name, is_subactivity_value=False):
        if is_subactivity_value:
            return """INSERT INTO %s (value, desc, prefix, owning_tub_or_object, enabled_flag, coa_create_date, last_update, effective_start_date, effective_end_date, parent_value) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""" % db_table_name
    
        return """INSERT INTO %s (value, desc, prefix, owning_tub_or_object, enabled_flag, coa_create_date, last_update, effective_start_date, effective_end_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ? );""" % db_table_name
        
        
    def format_sub_activity_row_info(self, csv_dict):
        # For SubActivity, add the 'parent_value' field
        return (None\
                , str(csv_dict['desc'].decode('ascii', 'ignore'))\
                , csv_dict['prefix']\
                , csv_dict['owning_tub_object']\
                , self.fmt_flag(csv_dict['enabled_flag'])\
                , self.fmt_date(csv_dict['coa_create_date'])\
                , self.fmt_date(csv_dict['last_update'])\
                , self.fmt_date(csv_dict['effective_start_date'])\
                , self.fmt_date(csv_dict['effective_end_date'])\
                , csv_dict['value']\
                , csv_dict['parent_value']\
                )

    def format_basic_row_info(self, csv_dict, table_name):
        """
        | id                   | int(11)      | NO   | PRI | NULL    | auto_increment |
        | desc                 | varchar(240) | NO   |     | NULL    |                |
        | prefix               | varchar(240) | NO   |     | NULL    |                |
        | owning_tub_or_object | varchar(4)   | NO   |     | NULL    |                |
        | enabled_flag         | tinyint(1)   | NO   |     | NULL    |                |
        | coa_create_date      | date         | NO   |     | NULL    |                |
        | last_update          | date         | NO   |     | NULL    |                |
        | effective_start_date | date         | YES  |     | NULL    |                |
        | effective_end_date   | date         | YES  |     | NULL    |                |
        | value                | varchar(3)   | NO   | UNI | NULL

        e.g. INSERT INTO `ec_defn_tubvalue` VALUES (NULL, "Unspecified", "", '000', 1, '1998-08-27', '2002-05-29', NULL, NULL, '977');
        """
        
        return (None\
                , str(csv_dict['desc'].decode('ascii', 'ignore'))\
                , csv_dict['prefix']\
                , csv_dict['owning_tub_object']\
                , self.fmt_flag(csv_dict['enabled_flag'])\
                , self.fmt_date(csv_dict['coa_create_date'])\
                , self.fmt_date(csv_dict['last_update'])\
                , self.fmt_date(csv_dict['effective_start_date'])\
                , self.fmt_date(csv_dict['effective_end_date'])\
                , csv_dict['value']\
                )
    
    def process_expense_code_files(self, clear_tables=True):
        """Process expense code files.  
        Load files in this order: tub org obj fund act sub root
        
        Sample file names:
            act.20110713.txt    org.20110713.txt    tub.20110713.txt
            fund.20110713.txt   root.20110713.txt
            obj.20110713.txt    sub.20110713.txt
        
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
        for file_prefix in self.ec_file_prefixes_ordered:#[5:6]:#[5:6]:#[:1]:#[5:]:    
            file_cnt +=1
            fname = ec_fname_dict.get(file_prefix, None)
            if fname is not None:
                fullname = os.path.join(self.segment_file_directory, fname)
                if os.path.isfile(fullname):
                    msgt('processing file: %s' % fname)
                    EC_CLASS = self.EC_OBJ_MAP.get(file_prefix, None)
                    if EC_CLASS is not None:    
                        self.load_definitions(fullname, eval(EC_CLASS), clear_table=clear_tables)
                    
    
if __name__=='__main__':
    EC_DIR = '/var/webapps/coa_files/coa_2013-0529'
    coa_loader = MySqlDefinitionFileLoader(EC_DIR)
    coa_loader.process_expense_code_files(clear_tables=True)
    
