import os, sys, binascii, webbrowser


user = os.getlogin()
home = os.path.expanduser("~")
token_file = os.path.join(home, '.dbtoken/dropbox_shorturl')
token_pathdir = os.path.dirname(token_file)
access_token = ''

if os.path.isfile(token_file):
	try:
		with open(token_file, 'rb') as tkf:
			tk = tkf.read()
		access_token = tk.strip()
		access_token = binascii.a2b_hex(access_token).decode()

		import dropbox
		db = dropbox.Dropbox(access_token)
		db.users_get_current_account()
		print("Already Authenticatied!\nSession End")
		sys.exit()
	except Exception as e:
		# print(e)
		# print("Access token is invalid, need reauthorized.")
		valid = False

else:
	print("Preparing...")

if access_token == '' or not os.path.isfile(token_file) or valid is False:
	from dropbox import DropboxOAuth2FlowNoRedirect

	print("Hi, {0}\nYou will need to authorize 'Urlshorten' to access your dropbox.".format(user))
	print("'Urlshorten' will need permission to access your entire dropbox folder in order to create shorturls.")

	auth_flow = DropboxOAuth2FlowNoRedirect('6w8ks8cgiz1oeqk', 'lzpmi1hpyz2esan')
	authorize_url = auth_flow.start()
	print("1. Go to: " + authorize_url)
	print("2. Click \"Allow\" (you might have to log in first).")
	print("3. Copy the authorization code.")
	# openurl = 'open ' + authorize_url
	# openurl = openurl.replace('&', '\&')
	webbrowser.open(authorize_url)
	auth_code = input("Enter the authorization code here \n>> ").strip()

	try:
		access_token, user_id = auth_flow.finish(auth_code)
	except Exception as e:
		print('\n', 'Error: %s' % (e,))

	mkdir = 'mkdir -p ' + token_pathdir
	os.system(mkdir)
	access_token = binascii.b2a_hex(access_token.encode()).decode()
	file_conn = open(token_file, 'w')
	file_conn.write(access_token)
	file_conn.close()

	print("Authorization Success!")

	status = True

if status is True:
	home = os.path.expanduser("~")
	loc_dir = os.path.dirname(os.path.realpath(__file__))

	pathToPY = os.path.join(loc_dir, 'Resource/dropbox_geturl.py')
	pathToService = os.path.join(loc_dir, 'Resource/Dropbox\ ShortUrl.workflow')

	pathToSetPY = os.path.join(home, '.py-tools')
	pathToSetService = os.path.join(home, 'Library/Services')

	mkdir = 'mkdir -p ' + pathToSet
	os.system(mkdir)

	mvToTools = 'mv ' + pathToPY + ' ' + pathToSetPY
	os.system(mvToTools)

	mvToService = 'open ' + pathToService
	os.system(mvToService)

	print('All dependencies are installed!\nSession end.')
