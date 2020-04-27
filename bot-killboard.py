from datetime import datetime
from random import randrange
import requests
import threading
import time
import sqlite3

GUILD_ID = "0rk05r3DRkOSqAV5m_IUWQ"
GUILD_NAME = "KNIGHTS OF TOMO"
KILLBOARD_URL = "https://gameinfo.albiononline.com/api/gameinfo/guilds/" +GUILD_ID +"/top?limit=100&range=week"
DISCORD_WEBHOOKS = "https://discordapp.com/api/webhooks/704237220038705162/XtsJndaxurQyC1YPuJQY8jMlOKkcFEMJ6qv2MQ1jYrEmFMwS1KrxgaoiaaiYjbzLzvNS"
KILLBOARD_LINK = "https://albiononline.com/en/killboard/kill/"
exitFlag = 0
date_filter = datetime.now().strftime("%Y-%m-%d")

class myThread (threading.Thread):

   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter

   def run(self):
      print ("Starting " + self.name)
      get_killboard_data(self.name, self.counter, 1)
      print ("Exiting " + self.name)

def send_to_discord(data):
    # payload = {
    #     "content": data["Killer"]["Name"] +" killed " +data["Victim"]["Name"] +" [" +data["Victim"]["GuildName"] + "]"
    # }
    colors = ["16711680", "6724044", "16773120"]
    if data["Victim"]["AllianceName"] == "":
        data["Victim"]["AllianceName"] = "None"
    embeds = [{
            "title": data["Killer"]["Name"] +" Killed " +data["Victim"]["Name"],
            "color": colors[randrange(len(colors)-1)]
            },
            {
            "fields": [
                {
                    "name": "Guild",
                    "value": data["Victim"]["GuildName"],
                    "inline": True
                },
                {
                    "name": "Alliance",
                    "value": data["Victim"]["AllianceName"],
                    "inline": True
                },
                {
                    "name": "Kill Fame",
                    "value": str(data["Killer"]["KillFame"])
                }
                ]
                },{
                    "title": "Killboard Link",
                    "url": KILLBOARD_LINK +str(data["EventId"])
                },
                {
                "timestamp": data["TimeStamp"]
            }
        ]
    time.sleep(5)
    payload = {
        "content": "Another one bites the dust",
        "embeds": embeds
    }
    print(payload)
    r = requests.post(DISCORD_WEBHOOKS, json=payload)
    print(r.status_code)
    print(r.text)

def get_killboard_data(threadName, delay, counter):

    while counter:
        if exitFlag:
            threadName.exit()

        print("Checking....")
        try:
            r = requests.get(KILLBOARD_URL)
            print(r.status_code)
            killboard_data = r.json()
        except:
            print("Error!")
            killboard_data = {}

        for data in killboard_data:
            if data["Type"] == "KILL":
                conn = sqlite3.connect('kills_db')
                cur = conn.cursor()
                # Check if exists
                cur.execute("SELECT id FROM events WHERE id='" +str(data["EventId"]) +"'")
                rows = cur.fetchall()
                if len(rows) >= 1:
                    continue
                else:
                    print("-----------------------------")
                    print(data["EventId"])
                    print(data["Killer"]["Name"])
                    print(data["Victim"]["Name"])
                    print(data["Victim"]["GuildName"])
                    print("-----------------------------")
                    print("Sending to DISCORD_WEBHOOKS")
                    send_to_discord(data)
                    # Insert a row of data
                    cur.execute("INSERT INTO events(id) VALUES ('"+str(data["EventId"]) +"') ")
                    # Save (commit) the changes
                    conn.commit()
                # We can also close the connection if we are done with it.
                # Just be sure any changes have been committed or they will be lost.
                conn.close()

        print("Checks Done!")
        time.sleep(delay)
        print("Run count: " +str(counter))
        counter += 1

# Create new threads
thread1 = myThread(1, "Thread-1", 60)


# Start new Threads
thread1.start()
thread1.join()

print ("Exiting Main Thread")