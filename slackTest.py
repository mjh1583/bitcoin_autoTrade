import requests
 
def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    print(response)
 
myToken = "xoxb-2045596135299-2030614043751-tysSvkxYFV4wBGgelM3fBJqP"
 
post_message(myToken,"#bitcoinautotrade","허위")
