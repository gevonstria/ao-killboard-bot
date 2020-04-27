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
      get_killboard_data(self.name, self.counter, 1)
      print ("Exiting " + self.name)

def send_to_discord(data):
    payload = {
        "content": data["Killer"]["Name"] +" killed " +data["Victim"]["Name"] +" [" +data["Victim"]["GuildName"] + "]"
    }
    time.sleep(5)
    r = requests.post(DISCORD_WEBHOOKS, json=payload)
    print(r.status_code)

def get_killboard_data(threadName, delay, counter):

    while counter:
        if exitFlag:
            threadName.exit()
        time.sleep(delay)

        print("Checking....")
        try:
            killboard_data = requests.get(KILLBOARD_URL).json()
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