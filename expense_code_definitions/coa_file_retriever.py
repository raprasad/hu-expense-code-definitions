import os, sys
from datetime import date, timedelta
import pexpect
import getpass
import stat
import shutil
from server_names import TEST_SERVER, LIVE_SERVER

"""
tub.20130522.txt
scp username@ye-old-server-36.cadm.harvard.edu:/u03/ftp/public/tub.20130522.txt coa_2013-0522 

"""
class CredFileReader:
    def __init__(self, fname):
        self.username = None
        self.pw = None
        self.load_creds(fname)
        
    def load_creds(self, fname):
        if not os.path.isfile(fname):
            return
        flines = open(fname, 'r').readlines()
        if len(flines) < 2:
            return
        self.username = flines[0].strip()
        self.pw = flines[1].strip()
        

class COAFileRetriever:
    """
    Retrieve COA files from servers ..34/..36 via SCP
    """

    COA_SRC_DIR = '/u03/ftp/public'
    COA_FILE_PREFIX_NAMES = """act fund obj org root sub tub""".split()
    COA_DIRECTORY_PREFIX = 'coa_'
    
    def __init__(self, scp_username, scp_password, is_live_server=False, dest_dir='/var/webapps/coa_files'):
        global TEST_SERVER, LIVE_SERVER
        self.log_msgs = []
        self.yesterday = date.today() + timedelta(days=-1)
        if is_live_server:
            self.server_name = LIVE_SERVER
        else:
            self.server_name = TEST_SERVER
        
        self.file_extension_to_copy = '.txt'
        self.dest_dir = dest_dir
        self.scp_username = scp_username
        self.scp_password = scp_password
        
        self.load_success = False
    
    def get_log_messages(self):
        return '\n'.join(self.log_msgs)
        
    def add_msg(self, msg):
        print msg
        self.log_msgs.append(msg)
        
    def get_destination_dir(self):
        coa_dirname = '%s%s' % (self.COA_DIRECTORY_PREFIX\
                            , self.yesterday.strftime('%Y-%m%d'))
        destination_dirname = os.path.join(self.dest_dir, coa_dirname)
        
        self.add_msg('(1) check for destination directory: %s' % destination_dirname)
        if not os.path.isdir(destination_dirname):
            self.add_msg('attempt to create directory: %s' % destination_dirname)
            os.makedirs(destination_dirname)
            self.add_msg('directory created: %s' % destination_dirname)
        else:
            self.add_msg('directory exists')
        return destination_dirname    
    
    
    def clear_old_coa_files(self):
        """
        Leave the last 3 coa directories
        """
        self.add_msg('-- Remove old COA files (leaving the last 3) --')
        items = os.listdir(self.dest_dir)
        #print items
        coa_dirnames = filter(lambda x: x.startswith(self.COA_DIRECTORY_PREFIX), items)
        print 'found directories: %s' %  coa_dirnames
        coa_dirnames.sort()
        coa_dirnames.reverse()
        
        if len(coa_dirnames) <= 3:
            self.add_msg('Only %s set(s) of files.  Leave them.' % len(coa_dirnames))
            return
        
        for dirname in coa_dirnames[3:]:
            coa_dirname_to_delete = os.path.join(self.dest_dir, dirname)
            shutil.rmtree(coa_dirname_to_delete)
            self.add_msg('directory deleted: %s' % coa_dirname_to_delete)

    
    def copy_yesterdays_backup(self):
        self.add_msg('-- Copy COA files from %s --' % self.yesterday.strftime('%m/%d/%Y'))

        destination_dirname = self.get_destination_dir()
        yesterday_str = self.yesterday.strftime('%Y%m%d')
        
        self.add_msg('(2) scp COA files')
        cnt = 0
        for fname_prefix in self.COA_FILE_PREFIX_NAMES:
            cnt+=1
            coa_filename = '%s.%s.txt' % (fname_prefix, yesterday_str)
            src_file_fullname = os.path.join(self.COA_SRC_DIR, coa_filename)
            #dest_file_fullname = os.path.join(destination_dirname, coa_filename)
            self.add_msg('\t(a) get file: %s' % src_file_fullname)
            #scp username@ye-ole-server-36.cadm.harvard.edu:/u03/ftp/public/tub.20130522.txt coa_2013-0522 
            
            scp_stmt = 'scp %s@%s:%s %s' % (self.scp_username, self.server_name, src_file_fullname, destination_dirname)
            self.add_msg('\tscp stmt: %s' % scp_stmt)
            
            
            handle = pexpect.spawn(scp_stmt)
            tried = False
            index = handle.expect([".*[pP]assword:\s*", ".*[Pp]assphrase.*:\s*", pexpect.EOF, pexpect.TIMEOUT])
            while (index < 2):
                if index == 0:
                    self.add_msg('starting copy...')
                    handle.sendline(self.scp_password)
                elif index == 1:
                    if _passphrase == "" or tried:
                        _passphrase = getpass.getpass("Enter passphrase: ")
                        tried = True
                    handle.sendline(_passphrase)
                else:
                    print handle.before
                index = handle.expect([".*[pP]assword:\s*", ".*[Pp]assphrase.*:\s*", pexpect.EOF, pexpect.TIMEOUT])
            handle.close()
            print 'file moved'
        self.add_msg('files moved (so far):')

        cnt = 0        
        fsizes = []
        for f in os.listdir(destination_dirname):
            if f.endswith(self.file_extension_to_copy):
                cnt += 1
                fsize = os.stat(os.path.join(destination_dirname, f))[stat.ST_SIZE]
                fsizes.append(fsize)
                self.add_msg('     - (%s) %s [%s]' % (cnt, f, fsize))
        if cnt == 7 and not 0 in fsizes:
            self.load_success = True
        self.add_msg('done')

"""
cfr = COAFileRetriever(is_live_server=True)
cfr.copy_yesterdays_backup()

"""
if __name__=='__main__':
    cfr = COAFileRetriever(scp_username='', scp_password=getpass.getpass(), is_live_server=True)
    cfr.copy_yesterdays_backup()
