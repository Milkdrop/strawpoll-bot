import requests, argparse, time
import threading

parser =  argparse.ArgumentParser (description = "Example: python3 script.py 13371337 1")
parser.add_argument ("id", help = "strawpoll.me poll ID")
parser.add_argument ("option", help = "Poll checkbox number (1 for 1st option, 2 for 2nd, ...)")

parser.add_argument ("-f", help = "Voting frequency (in ms) (Default: 200ms)")
parser.add_argument ("-m", help = "Max threads (Default: 16)")
parser.add_argument ("-p", action='store_true', help = "Use proxies (if the poll is doing an IP Check) - WARNING: Slow!")

args = parser.parse_args ()

motd = """
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$'               `$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$  
$$$$$$$$$$$$$$$$$$$$$$$$$$$$'                   `$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$$'`$$$$$$$$$$$$$'`$$$$$$!                       !$$$$$$'`$$$$$$$$$$$$$'`$$$
$$$$  $$$$$$$$$$$  $$$$$$$                         $$$$$$$  $$$$$$$$$$$  $$$$
$$$$. `$' \\' \\$`  $$$$$$$!                         !$$$$$$$  '$/ `/ `$' .$$$$
$$$$$. !\\  i  i .$$$$$$$$                           $$$$$$$$. i  i  /! .$$$$$
$$$$$$   `--`--.$$$$$$$$$                           $$$$$$$$$.--'--'   $$$$$$
$$$$$$L        `$$$$$^^$$                           $$^^$$$$$'        J$$$$$$
$$$$$$$.   .'   ""~   $$$    $.                 .$  $$$   ~""   `.   .$$$$$$$
$$$$$$$$.  ;      .e$$$$$!    $$.             .$$  !$$$$$e,      ;  .$$$$$$$$
$$$$$$$$$   `.$$$$$$$$$$$$     $$$.         .$$$   $$$$$$$$$$$$.'   $$$$$$$$$
$$$$$$$$    .$$$$$$$$$$$$$!     $$`$$$$$$$$'$$    !$$$$$$$$$$$$$.    $$$$$$$$
$JT&yd$     $$$$$$$$$$$$$$$$.    $    $$    $   .$$$$$$$$$$$$$$$$     $by&TL$
                                 $    $$    $
                                 $.   $$   .$
                                 `$        $'
                                  `$$$$$$$$'

                         strawpoll.me voting bot v1.2
                                        - by Milkdrop

	If you don't have enough proxies you can fill the file proxies.txt
	with valid SSL proxies from https://www.proxy-list.download/HTTPS
	for example.
"""

def prepare (args, motd):
	print (motd)

	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'}
	url = "https://www.strawpoll.me/" + args.id
	try:
		opt = int (args.option)
	except:
		print ("Invalid option: '{}'. Must be a number: 1 for 1st option, 2 for 2nd, ...".format (args.option))
		exit (1)

	if (args.f == None):
		freq = 0.2
	else:
		freq = int (args.f) / 1000.0

	if (args.m == None):
		maxthreads = 16
	else:
		maxthreads = int (args.m)

	if (args.p == True):
		try:
			proxies = open ("proxies.txt", "r").read ().split ("\n")
			print ("Found proxies.txt file, using that.")
		except:
			print ("Getting proxies from an on-line source...")
			page = requests.get ("https://proxy-daily.com", headers = headers).text
			page = page [page.find ("centeredProxyList freeProxyStyle"):]
			page = page [page.find (">") + 1:]
			page = page [:page.find ("</div>")]
			proxies = page.split ("\n")
			print ("Loaded {} proxies.".format (len (proxies)))

	print ("Connecting to: " + url)
	page = requests.get (url, headers = headers).text

	# Get Checkbox ID
	ind = page.find ("\"field-options-")

	checkboxID = page [ind:]
	checkboxID = checkboxID [checkboxID.find ("value=\"") + len ("value=\""):]
	checkboxID = checkboxID [:checkboxID.find ("\"")]
	checkboxID = str (int (checkboxID) + opt - 1)

	if (page.find (checkboxID) == -1):
		print ("Couldn't find option {}".format (opt))
		exit (1)

	print ("Checkbox ID: " + checkboxID)
	print ("Max threads: " + str (maxthreads))

	proxyindex = 0

	while True:
		if (args.p == True):
			proxy = proxies [proxyindex]
			proxyindex += 1
			if (proxyindex >= len (proxies)):
				print ("All proxies have been used.")
				break
		else:
			proxy = None

		thr = threading.Thread (target = vote, args = (url, checkboxID, headers, proxy))
		thr.daemon = True
		thr.start ()

		while (threading.active_count () >= maxthreads):
			time.sleep (0.1)

		time.sleep (freq)

def vote (url, checkboxID, headers, proxy = None):
	if (proxy == None):
		proxies = {}
	else:
		proxies = {"https": proxy}

	try:
		# Connect
		page = requests.get (url, headers = headers, proxies = proxies, timeout = 10).text

		# Get Security Tokens
		secToken1 = page [page.find ("security-token"):]
		secToken1 = secToken1 [secToken1.find ("value=\"") + len ("value=\""):]
		secToken1 = secToken1 [:secToken1.find ("\"")]

		secToken2 = page [page.find ("field-authenticity-token"):]
		secToken2 = secToken2 [secToken2.find ("name=\"") + len ("name=\""):]
		secToken2 = secToken2 [:secToken2.find ("\"")]

		fieldName = page [page.find ("\"field-options-"):]
		fieldName = fieldName [fieldName.find ("name=\"") + len ("name=\""):]
		fieldName = fieldName [:fieldName.find ("\"")]

		page = requests.post (url, data = {"security-token": secToken1, secToken2: "", fieldName: checkboxID}, headers = headers, proxies = proxies, timeout = 10).text

		successString = "\"success\":\"success\""
		if (page.find (successString) != -1):
			print ("Vote Successful ({})".format (secToken1))
		else:
			if (proxy == None):
				print ("Vote Unsuccessful (The poll may be doing an IP Check. Use option -p)")
			else:
				print ("Vote Unsuccessful ({})".format (secToken1))

	except requests.exceptions.ProxyError:
		print ("Vote Unsuccessful (Invalid Proxy)")
	except requests.exceptions.ConnectionError:
		print ("Vote Unsuccessful (Invalid Proxy - Connection Error)")

prepare (args, motd)