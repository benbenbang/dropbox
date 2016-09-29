import sys, os, argparse, contextlib, datetime, six, clipboard, re, binascii

import dropbox
from dropbox.files import FileMetadata, FolderMetadata

#####################################################################################################################
# Authentication
#####################################################################################################################

try:
	home = os.path.expanduser("~")
	token_file = os.path.join(home, '.dbtoken/dropbox_shorturl')
	token_pathdir = os.path.dirname(token_file)

	with open(token_file, 'rb') as tkf:
		tk = tkf.read()
	access_token = tk.strip()
	access_token = binascii.a2b_hex(access_token).decode()

except:
	clipboard.copy('Failed, you need to authenticate first.')
	print('Failed, you have to authenticate this app first on Dropbox Website')

db = dropbox.Dropbox(access_token)

#####################################################################################################################
# Get Short Url
#####################################################################################################################

home = os.path.expanduser("~")
root = os.path.join(home, 'Dropbox')

# loc_dir = os.path.dirname(os.path.realpath(__file__))

loc_path = ""
for f in sys.argv[1:2]:
	loc_path += f

# dbFileName = os.path.basename(loc_path)
# dbDirName = os.path.dirname(loc_path)

if bool(re.search(root, loc_path)) is True:
	try:
		db_Dir = loc_path.replace(root, '')
		if db_Dir.endswith('/'):
			cursor = len(db_Dir) - 1
			db_Dir = db_Dir[0:cursor]
		dbShare = db.sharing_create_shared_link(db_Dir, short_url=True)
		dbShareLink = dbShare.url
		clipboard.copy(dbShareLink)
		print('Short Url: %s already save to clipboard :)' % dbShareLink)
	except Exception as e:
		error = 'Wait for Uploading, do it later'
		clipboard.copy(error)
		print(e)

else:
	clipboard.copy('Failed, file/folder is not in dropbox')
	print('Failed, you have to enter a file is already in your Dropbox folder!')
