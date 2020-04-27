from datetime import datetime
import requests
import threading
import time
import sqlite3

GUILD_ID = "0rk05r3DRkOSqAV5m_IUWQ"
GUILD_NAME = "KNIGHTS OF TOMO"
KILLBOARD_URL = "https://gameinfo.albiononline.com/api/gameinfo/guilds/" +GUILD_ID +"/top?limit=50&range=week"
DISCORD_WEBHOOKS = "https://discordapp.com/api/webhooks/704237220038705162/XtsJndaxurQyC1YPuJQY8jMlOKkcFEMJ6qv2MQ1jYrEmFMwS1KrxgaoiaaiYjbzLzvNS"
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
      print_time(self.name, self.counter, 5)
      print ("Exiting " + self.name)

def send_to_discord(data):
    payload = {
        "content": data["Killer"]["Name"] +" killed " +data["Victim"]["Name"]
    }
    time.sleep(5)
    r = requests.post(DISCORD_WEBHOOKS, json=payload)
    print(r.status_code)

def print_time(threadName, delay, counter):
    while counter:
        if exitFlag:
            threadName.exit()
        time.sleep(delay)

        killboard_data = requests.get(KILLBOARD_URL).json()
        for data in killboard_data:
            if data["Type"] == "KILL" and date_filter in data["TimeStamp"]:
                print(data["EventId"])
                print(data["Killer"]["Name"])
                print(data["Victim"]["Name"])
                conn = sqlite3.connect('kills_db')
                cur = conn.cursor()
                # Check if exists
                cur.execute("SELECT id FROM events WHERE id='" +str(data["EventId"]) +"'")
                rows = cur.fetchall()
                if len(rows) > 1:
                    print("Exist")
                else:
                    send_to_discord(data)
                    # Insert a row of data
                    cur.execute("INSERT INTO events(id) VALUES ('"+str(data["EventId"]) +"') ")
                    # Save (commit) the changes
                conn.commit()
                # We can also close the connection if we are done with it.
                # Just be sure any changes have been committed or they will be lost.
                conn.close()

        print(date_filter)
        time.sleep(delay)

    counter -= 1

# Create new threads
thread1 = myThread(1, "Thread-1", 10)


# Start new Threads
thread1.start()
thread1.join()

print ("Exiting Main Thread")