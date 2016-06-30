# -*- coding: utf-8 -*-

import argparse, contextlib, datetime, os, six, sys, time, unicodedata

import dropbox
from dropbox.files import FileMetadata, FolderMetadata

import clipboard, re, zipfile

print("\nUpload You Attachments to Dropbox!")
print("------------------------------")

statName = [ "Percent: ","Packing: ", "Uploading: ", "TP: " ]

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

home = os.path.expanduser("~")

checkPoint1 = 1
while checkPoint1 > 0:

	loc_path = ""
	for f in sys.argv[1:]:
		loc_path += f
		print(loc_path)

	if os.path.exists(loc_path) == True :
		if os.path.isfile(loc_path) == True:
			print("Packing your cargo..."),
			dbFileName = os.path.basename(loc_path)
			dbZipName = dbFileName.split('.')[0]+'.zip'
			with zipfile.ZipFile(dbZipName,'w') as dbzip:
				dbzip.write(loc_path, dbFileName)
			print("Done#")
			print("Package in this cargo:")
			print(dbzip.namelist())
			time.sleep(1)

		elif os.path.isdir(loc_path) == True:
			print("Packing your cargo..."),
			dbFileName = os.path.basename(loc_path)
			dbZipName = dbFileName.split('.')[0]+'.zip'
			numInCargo = len([name for name in os.listdir(loc_path) if os.path.isfile(os.path.join(loc_path, name))])
			with zipfile.ZipFile(dbZipName,'w') as dbzip:
				i = 0
				for root, dirs, files in os.walk(loc_path):
					for file in files:
						dbzip.write(os.path.join(loc_path,file), file)
						clock(i,numInCargo,statName[1])
						i += 1
			print("%s packages are in this cargo:" %(numInCargo))
			for i in dbzip.namelist():
				if not i.startswith('.'):
					print('[',i,']')
			time.sleep(1)

		else:
			print("Cannot deal with explosive things, please check your package again.")
			exit(0)

		checkPoint1 = 0
	else:
		print("Please check the dir you paste is valid or the file is exist or not")
		checkPoint1 = 1

loc_path = os.path.join(home,dbZipName)

file_size = os.path.getsize(loc_path)
threshold = 5 * 1024 * 1024 # 5 MB
chunk_size = 1024 * 1024 # 1 MB

db_Dir = os.path.join('App Path',dbZipName)
db = dropbox.Dropbox('APP Token')

if file_size < threshold :
	print("Prepare to Upload...")
	f = open(loc_path,'rb')

	# Ticking
	clock(f.tell(), file_size,statName[2])
	data = f.read()

	dbUpload = db.files_upload(data, db_Dir)
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
	commit = dropbox.files.CommitInfo(path=db_Dir)

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

print('Everything Done!')