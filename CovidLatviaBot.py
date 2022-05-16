import requests
import os
import praw
import datetime
import sys

# ID_log tiek glabāts pēdējais id json ierakstam, kas tika publicēts subredditā komentāra veidā. 
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
ID_log = os.path.join(THIS_FOLDER, 'ID_log.txt')

# Gets which day of week given date it
def getDay(date_and_time):
    size = len(date_and_time)
    date = date_and_time[:size - 9]
    size = len(date)
    year = date[:size - 6]
    month = date[5:7]
    day = date[8:10]
    daynr = datetime.date(day=int(day), month=int(month), year=int(year)).weekday()
    if(daynr == 0):
        return "svētdienu"
    elif(daynr == 1):
        return "pirmdienu"
    elif(daynr == 2):
        return "otrdienu"
    elif(daynr == 3):
        return "trešdienu"
    elif(daynr == 4):
        return "ceturtdienu"
    elif(daynr == 5):
        return "piektdienu"
    elif(daynr == 6):
        return "sestdienu"

# Replies to post with covid stats
def makeComment(day, date, tests_count, cases_count, proportion, dead_count, cases_count_unvaccinated, cases_count_vaccinated):
    TestSubmissionID = "q6jdhh" # Post for test purposes in r/test_for_bots
    SubmissionID = "q4haf9" # Real post in r/latvia

    submission = reddit.submission(SubmissionID)
    submission.reply(
    "# Covid statistika Latvijā par "+str(day)+"!"+'\n\n'+'\n\n'+
    "|Datums|"+str(date)+"|"+'\n'+
    ":--|:--:|"+'\n'+
    "|Testu skaits|"+str(tests_count)+"|"+'\n'+
    "|Covid-19 inficēto skaits|"+str(cases_count)+"|"+'\n'+
    "|Īpatsvars|"+str(proportion)+"%|"+'\n'+
    "|Inficēto skaits, kuri nav vakcinējušies|"+str(cases_count_unvaccinated)+"|"+'\n'+
    "|Inficēto skaits, kuri ir vakcinējušies|"+str(cases_count_vaccinated)+"|"+'\n'+
    "|Mirušo personu skaits|"+str(dead_count)+"|"+'\n'+"---"+'\n'+
    "[Source](https://data.gov.lv/dati/lv/dataset/covid-19)|[Feedback](https://www.reddit.com/message/compose?to=Ginters17&subject=About%20CovidLatviaBot&message=)"
    )

# https://old.reddit.com/prefs/apps/
reddit = praw.Reddit(
    client_id="",
    client_secret="",
    username="",
    password="",
    user_agent="Covid statistics in Latvia - made by /u/Ginters17"
)

# Iegūst JSON no data.gov.lv mājaslapas API
# Need to change offset value in URL after 100 records have been posted in JSON. Can write a script for this but i am too lazy, so just manually change it every 100 days lul.
response = requests.get('https://data.gov.lv/dati/lv/api/3/action/datastore_search?offset=600&resource_id=d499d2f0-b1ea-4ba2-9600-2c701b03bd4a') 
data = response.json()

# Izskaita cik ir kopā ierakstu par covid statistiku katru dienu, lai varētu izvēlēties pēdējo (visjaunāko)
count = 0
for item in data["result"]["records"]:
    count+=1

# count - 1 is the last record in json. count -2 is previous to last record in json. 
count = count - 1

# Gets the stats from json. Also formats it.
tests_count = data["result"]["records"][count]["TestuSkaits"]
cases_count = data["result"]["records"][count]["ApstiprinataCOVID19InfekcijaSkaits"]
dead_count = data["result"]["records"][count]["MirusoPersonuSkaits"]
proportion = data["result"]["records"][count]["Ipatsvars"] 
cases_count_unvaccinated = data["result"]["records"][count]["ApstCOVID19InfSk_Nevakc"] 
cases_count_vaccinated = data["result"]["records"][count]["ApstCOVID19InfSk_Vakc"] 
cumulitive_count = data["result"]["records"][count]["14DienuKumulativaSaslimstibaUz100000Iedzivotaju"] 
date_and_time = data["result"]["records"][count]["Datums"]
size = len(date_and_time)
date = date_and_time[:size - 9] # Subtracts hour:minute:second part of string
day = getDay(date_and_time) # day = "pirmdienu", "otrdienu"...



datetime_object = datetime.datetime.strptime(date, '%Y-%m-%d') # Turns date into datetime object
Previous_Date_and_time = datetime_object - datetime.timedelta(days=1) # Subtracts 1 day from datetime object because date in json is 1 day further
size = len(str(Previous_Date_and_time))
Previous_Date = str(Previous_Date_and_time)[:size - 9] # Subtracts hour:minute:second part of string
date = Previous_Date # Assign just calculated previous date to variable date for easier understanding


new_id = data["result"]["records"][count]["_id"] # Pēdējā json 'record' ieraksta id
with open(ID_log) as f:
    for line in f:
        pass
    prev_id = line # Pēdējais izmantotais id


# Ja jaunais id no json ir lielāks par veco id, tad var publicēt jaunu komentāru ar jauno statistiku
if (int(new_id) > int(prev_id)):
    makeComment(day, date, tests_count, cases_count, proportion, dead_count, cases_count_unvaccinated, cases_count_vaccinated)
    with open(ID_log, 'a') as f:
        f.write("\n"+str(new_id))
    print("New comment was posted. Record id - "+str(new_id))

# Ja abi id ir vienādi, tad json'ā nav jauns 'record'
elif (int(new_id) == int(prev_id)):
    print("New record not found!")


sys.exit(0)