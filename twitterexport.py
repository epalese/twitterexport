# usage:
# python tweetexport.py username password startimeinmillis endtimeinmillis outputfile
import sys, re, requests, codecs, time, json

if len(sys.argv) != 6:
        print('Usage:')
        print('python tweetexport.py username password startimeinmillis endtimeinmillis outputfile')
        print
        exit(127)


loginPageReq = requests.get("https://twitter.com")
loginPage = loginPageReq.text

reg = re.compile('.+?<input type="hidden" value="([^"]*)" name="authenticity_token"/>.+?', re.DOTALL)
authToken = authToken = reg.match(loginPage).group(1)

username = sys.argv[1]
password = sys.argv[2]
params = {
        'session[username_or_email]' : username,
        'session[password]' : password,
        'return_to_ssl' : True,
        'scribe_log' : '',
        'redirect_after_login': '/',
        'authenticity_token': authToken
}
headers = {
        'User-Agent': ''
        }
session = requests.Session()
sessionResponse = session.post(
        "https://twitter.com/sessions",
        data=params,
        cookies=loginPageReq.cookies,
        verify=True,
        headers=headers )

loginPageFile = codecs.open("output.html", "w", "utf-8")
loginPageFile.write(sessionResponse.text)
loginPageFile.close()

starttime = sys.argv[3]
endtime = sys.argv[4]
requestJSONUrl = "https://analytics.twitter.com/user/" + str(username) + "/tweets/export.json?start_time=" + str(starttime) + "&end_time=" + str(endtime) + "&lang=en"

status = 'Pending'
counter = 0
while status != 'Available' and  counter < 5:
        requestJSONTrigger = session.post(requestJSONUrl,cookies=sessionResponse.cookies,verify=True,headers=headers)
        print(requestJSONTrigger.text)
        jsonresp = json.loads(requestJSONTrigger.text)
        status = jsonresp['status']
        counter = counter + 1
        time.sleep(5)

		
if status != 'Available':
        exit(127)

requestExportUrl = "https://analytics.twitter.com/user/" + str(username) + "/tweets/bundle?start_time=" + str(starttime) + "&end_time=" + str(endtime) + "&lang=en"
requestExport = session.get(requestExportUrl,cookies=sessionResponse.cookies,verify=True,headers=headers, stream=True)

exportFileName = sys.argv[5]                                    # "tweet_activity_metrics_" + str(starttime) + "_" + str(endtime) + ".csv"
exportFile = codecs.open(exportFileName, "w", "utf-8")
exportFile.write(unicode(requestExport.content, 'utf-8'))
exportFile.close()
exit(0)
