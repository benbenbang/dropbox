# -*- coding: utf-8 -*-
import sys, os

home = os.path.expanduser("~")
loc_dir = os.path.dirname(os.path.realpath(__file__))

packages_path = os.path.join(loc_dir,'envset/lib/python3.5/site-packages')
sys.path.append(packages_path)

import argparse, contextlib, datetime, six, time, unicodedata, hashlib, getpass

import dropbox
from dropbox.files import FileMetadata, FolderMetadata

import clipboard, re, zipfile

print("\nUpload You Attachments to Dropbox!")
print("------------------------------")

#####################################################################################################################
#	Authentication
#####################################################################################################################
 
token_file = os.path.join(home,'.dbtoken')
 
if os.path.isfile(token_file):
    tkf = open(token_file,'r')
    tk = tkf.read()
    tkf.close()
    access_token = tk.strip()
else:
    from dropbox import DropboxOAuth2FlowNoRedirect
 
    print("Somehow this is your first time here, you need to authorize 'cargo' to access your dropbox.")
 
    auth_flow = DropboxOAuth2FlowNoRedirect('fjv7mxum0q9xbpg', '5ums61uc9nhzz8m')
    authorize_url = auth_flow.start()
    print("1. Go to: " + authorize_url)
    print("2. Click \"Allow\" (you might have to log in first).")
    print("3. Copy the authorization code.")
    auth_code = input("Enter the authorization code here: ").strip()
 
    try:
        access_token, user_id = auth_flow.finish(auth_code)
    except Exception:
        print('Error: %s' % (e,))
 
    file_conn = open(token_file,'w')
    file_conn.write(access_token)
    file_conn.close()
 
#####################################################################################################################
#   Clock Ticking! 
#####################################################################################################################
 
statName = [ "Percent: ","Packing: ", "Uploading: "]
 
def update_progress(progress, stat=statName[0]):
    barLength = 10 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\r" + stat + "[{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), format(progress*100,'.2f'), status)
    sys.stdout.write(text)
    sys.stdout.flush()
 
def clock(i,Total,stat):
    Total = Total - 1
    time.sleep(0.1)
    update_progress(i/Total,stat)
 
def exist(path):
    try:
        db.files_list_folder_get_latest_cursor(path)
        return True
    except:
        return False
 
#####################################################################################################################
#   File/Folder Check
#####################################################################################################################
 
checkPoint1 = 1
while checkPoint1 > 0:
    loc_path = ""
    for f in sys.argv[1:2]:
        loc_path += f
 
    if os.path.exists(loc_path) == True :
        if os.path.isfile(loc_path) == True:
            dbFileName = os.path.basename(loc_path)
            dbZipName = dbFileName.split('.')[0]+'.zip'
            print("Packing your cargo..." , end=' ')
            with zipfile.ZipFile(dbZipName,'w') as dbzip:
                dbzip.write(loc_path, dbFileName)
            print("Done#")
            print("Package in this cargo:")
            print(dbzip.namelist())
            #print(os.getcwd())
            time.sleep(1)
 
        elif os.path.isdir(loc_path) == True:
            dbFileName = os.path.dirname(loc_path)
            dbDirName = os.path.dirname(dbFileName)
            dbFileName = dbFileName.replace(dbDirName+'/','')
            dbZipName = dbFileName + '.zip'
            dbZipPath = os.path.dirname(loc_path)
            print("Packing your cargo...")
            numInCargo = len([name for name in os.listdir(loc_path) if not name.startswith('.')])
 
            print("%s packages are in this cargo:" %(numInCargo))
 
            os.system('cd "%s";zip -r "%s" "%s"' %(dbDirName,dbZipName,dbFileName))
            os.system('cd %s;mv "%s" "%s"' %(dbDirName,dbZipName,os.path.join(home+'/'+dbZipName)))
            print('Packing your cargo... #Done')
            time.sleep(1)
 
        else:
            print("Cannot deal with explosive things, please check your package again.")
            exit(0)
 
        checkPoint1 = 0
    else:
        print("Please check the dir you paste is valid or the file is exist or not")
        checkPoint1 = 1
 
#####################################################################################################################
#   Ready to upload
#####################################################################################################################

loc_path = os.path.join(home+'/',dbZipName)
file_size = os.path.getsize(loc_path)
threshold = 5 * 1024 * 1024 # 5 MB
chunk_size = 1024 * 1024 # 1 MB
 
db = dropbox.Dropbox(access_token)
 
db_Dir = os.path.join('/',dbZipName)
 
if file_size < threshold :
    print("Prepare to Upload...")
    f = open(loc_path,'rb')
 
    # Ticking
    clock(f.tell(), file_size,statName[2])
    data = f.read()
 
    dbUpload = db.files_upload(data, db_Dir, autorename=True)
    dbShare = db.sharing_create_shared_link(db_Dir,short_url=True)
    dbShareLink = dbShare.url
    # Ticking
    clock(f.tell(), file_size,statName[2])
    f.close()
 
    os.remove(loc_path)
    print("Piece of cake ;) ")
 
else:
    print("Prepare to Upload...")
    f = open(loc_path,'rb')
 
    # Ticking
    clock(f.tell(), file_size,statName[2])
 
    data = f.read(chunk_size)
    upload_session_result = db.files_upload_session_start(data)
 
    # Ticking
    clock(f.tell(), file_size,statName[2])
 
    session_id = upload_session_result.session_id
    cursor = dropbox.files.UploadSessionCursor(session_id, offset=f.tell())
    commit = dropbox.files.CommitInfo(path=db_Dir,autorename=True)
 
    while f.tell() < file_size:
        if ((file_size - f.tell()) <= chunk_size):
            data = f.read(chunk_size)
            db.files_upload_session_finish(data, cursor, commit)
        else:
            db.files_upload_session_append(data, cursor.session_id, cursor.offset)
            data = f.read(chunk_size)
            cursor.offset = f.tell()
        # Ticking
        clock(f.tell(), file_size,statName[2])
 
    dbShare = db.sharing_create_shared_link(db_Dir,short_url=True)
    dbShareLink = dbShare.url
    f.close()
 
    os.remove(loc_path)
 
 
#####################################################################################################################
#   HTML Make and Copy
#####################################################################################################################
 
html = '''
<table border="0" cellpadding="0" cellspacing="0" class="">
    <tbody class="">
    <tr class="">
        <td align="left" style="border: 1px solid #007ee5; border-left: 16px solid #007ee5; -webkit-border-radius: 10px; -moz-border-radius: 10px; border-radius: 10px; padding: 10px 15px; font-family: \'Helvetica Neue\', \'Arial\'; font-size: 12px; color: #000000; line-height: 14px;" class="">
            <img src=\'https://github.com/benbenbang/dropbox/blob/master/asset/dropbox.jpg?raw=true\' width="64" height="64" border="0" align="right" class="">
            <h1 style="font-family: \'Helvetica Neue\', \'Arial\'; font-size: 20px; font-weight: normal; line-height: 24px; padding: 2px 0; margin: 0 0 6px 0; color: #000000;border-bottom:1px dashed #007ee5;" class="">Attachments</h1>
            <h2 style="font-family: \'Helvetica Neue\', \'Arial\'; font-size: 14px; font-weight: normal; line-height: 20px; margin: 0 0 6px 0; color: #000000;" class="">The file attachment of this email has been uploaded to the cloud.<br class="">Please download it from the following link:</h2>
            <ul style="padding-left:0px;" class="">
                <li style="background:url(\'https://github.com/benbenbang/dropbox/blob/master/asset/zip.png?raw=true\') no-repeat;background-size:32px 32px;padding:1px 36px 2px;min-height:36px;list-style-type:none;" class="">
                    <a href='%s' class="">%s</a>
                    <br>
                    <a>Click to Dropbox: %s</a>
                </li>
            </ul>
        </td>
    </tr>
    <tr class="">
    </tr>
    </tbody>
</table>
'''  % (dbShareLink, dbFileName, dbShareLink)
 
clipboard.copy(html)
 
#####################################################################################################################
#   Session End
#####################################################################################################################
print('Everything Done!')