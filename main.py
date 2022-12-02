# import keep_alive
import datetime
import os
import random
from threading import Thread
from time import sleep

import mysql.connector
import pytz
import requests
import schedule
import tabula
import telebot
from PIL import Image
from emoji import UNICODE_EMOJI
from pexels_api import API
from requests_html import HTMLSession
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from telebot import types





HOST = ''
USER = ''
PASS = ''
DATABASE = ''


TOKEN = ''

CHROMEDRIVER_PATH = '/usr/bin/chromedriver'
GOOGLE_CHROME_BIN = '/usr/bin/chromium'

chrome_options = Options()
WINDOW_SIZE = "1920,2000"
chrome_options.add_argument("--hide-scrollbars")
chrome_options.binary_location = GOOGLE_CHROME_BIN
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
# executable_path=CHROMEDRIVER_PATH
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options, keep_alive=True)
#driver = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options, keep_alive=True)
IST = pytz.timezone('Asia/Kolkata')

mydb = mysql.connector.connect(
    host=HOST,
    database=DATABASE,
    user=USER,
    password=PASS
)
mycursor = mydb.cursor(buffered = True)

mycursor.execute("SELECT * from visitors")
allData = mycursor.fetchall()
dic ={}
t = ['id', 'name', 'visits', 'batch', 'schedule', 'theme', 'time' ]
for i in allData:
    dic[i[0]] = dict()
    for j in range(1,7):
        dic[i[0]][t[j]] = i[j]
        

def addUser(id, name):
    global dic
    dic[id] = dict()
    dic[id]['name'] = name
    dic[id]['visits'] = 100
    dic[id]['batch'] = None
    dic[id]['schedule'] = 0
    dic[id]['theme'] = None
    dic[id]['time'] = None

def editUser(id, key, value):
    global dic
    dic[id][key] = value

im_name = ''

PEXEL_API_KEY = '563492ad6f917000010000019469eb2879c94dda8ec51f01b1340ee0'
api = API(PEXEL_API_KEY)
api.search(open('image_data.txt', 'r').read(), page=1, results_per_page=100)
photos = api.get_entries()


    
markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
markup.add('Help', 'Batch List', 'Set Default Batch', 'Theme', 'Seating Plan', 'Send', 'Today', 'Tomorrow')


def func():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
    markup.add('Help', 'Batch List', 'Set Default Batch', 'Theme', 'Seating Plan', 'Send', 'Today', 'Tomorrow')

    print(datetime.datetime.now())
    global im_name
    im_name = 'gradient'
    print('restarting program')
    global mydb
    mydb = mysql.connector.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASS
    )

    global mycursor
    mycursor = mydb.cursor()

    def ping():
        if not mydb.is_connected():
            mydb.reconnect(attempts=10, delay=10)

    

    try:
        driver.get("http://fiitjeenorthwest.com/time_table.php")
        myElem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'select')))
        print("Page is ready!")
    except TimeoutException:
        driver.get('http://example.com/')
        print("Loading took too much time!")

    x = str(datetime.datetime.now(IST))[:19]


    bot = telebot.TeleBot(TOKEN)

    def emojiToUnicode(s):
        em = [c for c in s if c in UNICODE_EMOJI.keys()]
        if len(em) > 0:
            for k in em:
                uCode = UNICODE_EMOJI[k]
                if k in s:
                    s = s.replace(k, uCode)
        return s

    def imageMaker(lst, batch, theme='Night'):
        #print('reached')
        photo = photos[random.randrange(79)]
        photo_link = photo.large2x
        # photo_link=f'image ({random.randrange(29)}).jpg'
        # print(photo_link)
        data = lst
        data1 = data[0]
        data2 = data[1:]

        lst1 = ['<th>' + i + '</th>' for i in data1]
        lst2 = [['<td>' + data2[j][i] + '</td>' for i in range(7)] for j in range(4)]
        lst3 = ['x2', 'x3', 'x4', 'x5']
        # print(lst1)
        # print(lst2, len(lst2))
        time = "Updated : " + str(str(datetime.datetime.now(IST))[:19])
        batchcode = batch
        with open(f'{theme}.html', 'r+') as file:
            x = file.read()
            x = x.replace('batch', batchcode)
            x = x.replace('bksource', photo_link)
            x = x.replace('x1', ''.join(lst1))
            x = x.replace('update', time)
            for i in range(4):
                x = x.replace(lst3[i], ''.join(lst2[i]))
            # print(x)
        with open('table2.html', 'w') as file2:
            file2.write(x)

        #print('html created')
        # chrome_option = Options()
        # WINDOW_SIZE = "1920,1080"
        # chrome_option.add_argument("--window-size=%s" % WINDOW_SIZE)
        # chrome_option.add_argument("--headless")
        # chrome_option.add_argument('--no-sandbox')
        # chrome_option.add_argument('--disable-dev-shm-usage')

        driver2 = webdriver.Chrome(options=chrome_options)
        path = os.path.abspath('table2.html')
        #print(path)

        driver2.get(r"file:///" + path)

        elem = driver2.find_element_by_class_name('container')
        try:
            elem.screenshot(f'{batch}_{theme}.png')
        except:
            elem.screenshot('Schedule.png')
        driver2.quit()

    def imageUpdater(bot=bot):
        downloader(im_name)


    def scheduler(bot=bot):
        for users in dic.keys():
            defaultBatch = dic[users]['batch']
            if not defaultBatch == '' and not defaultBatch == 'BATCHCODE' and not defaultBatch == None and dic[users]['schedule'] == 0:
                
                    try:
                        print(users, '-------------------------------------------------------')
                        start2(users, defaultBatch)
                        keyboard = types.InlineKeyboardMarkup(row_width=2)
                        a = types.InlineKeyboardButton(text='❌ Turn off Scheduled Msg', callback_data='sched_1')
                        keyboard.add(a)
                        bot.send_message(users, 'This is a Scheduled message:', parse_mode='HTML',reply_markup=keyboard)
                        print('\n')
                    except Exception as e:
                        print(e)
                        print('couldnt send scheduled routine')
                    # print(ids)

    def addEntry(msg, bot):
        name = str('' if msg.from_user.first_name is None else msg.from_user.first_name) + \
               str('' if msg.from_user.last_name is None else ' ' + msg.from_user.last_name)
        sql = "INSERT INTO visitors2 (Name, Chat_Id, Message, DateTime) VALUES (%s, %s, %s, %s)"
        val = (name, msg.chat.id, emojiToUnicode(msg.text), x)
        mycursor.execute(sql, val)
        #mydb.commit()
        

    def addVisitTimes(chat_id):
        # print("SELECT visits FROM visitors WHERE Chat_Id='" +str(chat_id) +"' ")
        mycursor.execute("SELECT visits FROM visitors WHERE Chat_Id='" + str(chat_id) + "' ")
        data = mycursor.fetchall()
        # print(data, data[0][0])
        visits = int(data[0][0])
        # print(visits)
        sql = "UPDATE visitors SET visits = " + str(visits + 1) + " WHERE Chat_Id =" + str(chat_id)
        mycursor.execute(sql)
        mydb.commit()

    def addVisitor(chat_id, name, bot):
        sql = "INSERT INTO visitors (Name, Chat_Id, Date) VALUES (%s, %s, %s)"
        val = (name, chat_id, x)
        mycursor.execute(sql, val)
        mydb.commit()
        #addVisitTimes(chat_id)
        addUser(chat_id, name)

    def checkVisitor(msg, bot):
        #mycursor.execute("SELECT Chat_Id from visitors")
        #data = mycursor.fetchall()
        #allVisitors = [i[0] for i in data]
        # print(allVisitors)
        # print(type(msg))
        if msg.chat.id in dic.keys():
            #addVisitTimes(msg.chat.id)
            print(2)
        else:
            name = str('' if msg.from_user.first_name is None else msg.from_user.first_name) + \
                   str('' if msg.from_user.last_name is None else ' ' + msg.from_user.last_name)
            addVisitor(msg.chat.id, name, bot)

    def setDefault(msg):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        a = types.InlineKeyboardButton(text='Send Routine', callback_data='send')
        keyboard.add(a)
        batch = msg.text
        sql = "UPDATE visitors SET DefaultBatch = '" + batch + "' WHERE Chat_Id =" + str(msg.chat.id)
        mycursor.execute(sql)
        editUser(msg.chat.id, 'batch', batch)
        mydb.commit()
        bot.send_message(msg.chat.id, 'Default Batch set to ' + batch, reply_markup=keyboard)
        bot.send_message(msg.chat.id, 'Now every time you tap send, you will receive your routine', reply_markup=markup)

    def scheduleSetter(msg, rep):
        sql = f"UPDATE visitors SET Scheduler = '{rep}' WHERE Chat_Id =" + str(msg.chat.id)
        mycursor.execute(sql)
        mydb.commit()
        editUser(msg.chat.id, 'scheduler', rep)

    def startMsg(bot, msg):
        intro = open('help.txt', 'r', encoding='utf-8').read()
        bot.send_message(msg.chat.id, intro, parse_mode='HTML')
        bot.send_photo(msg.chat.id, photo=open('ss.jpg', 'rb'), caption='Tap that icon to use custom keyboard',
                       reply_markup=markup, )

    def start(msg):
        batch = msg.text
        id = msg.chat.id
        start2(id, batch)

    def create_image():
        ping()
        mycursor.execute("SELECT DefaultBatch from visitors")
        data = mycursor.fetchall()
        allDefautlBatch = list(set([i[0] for i in data]))
        kkk=0
        for batch in allDefautlBatch:
            kkk = kkk+1
            try:
                element = Select(driver.find_element_by_tag_name('select'))
            except:
                try:
                    driver.get("http://fiitjeenorthwest.com/time_table.php")
                    print('driver refreshed')
                except:
                    continue
            try:
                element = Select(driver.find_element_by_tag_name('select'))
                element.select_by_value(batch)
            except:
                continue
            try:
                driver.find_element_by_name('submit').click()
            except:
                continue
            table = driver.find_element_by_xpath('//*[@id="banner_flash1"]/div[3]/table[4]')
            rows = table.find_elements_by_tag_name('tr')

            lst = []
            for row in rows:
                columns = row.find_elements_by_tag_name('td')
                lst.append([i.text for i in columns])
            for theme in ['Vintage', 'Dark', 'Light', 'Night']:
                print(batch, theme, f'{kkk}/{len(allDefautlBatch)}')
                imageMaker(lst, batch, theme)

        print('Image Making Done')

    #create_image()
    def start2(chat_id, batch):
        driver.refresh()
        #driver2 = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options, keep_alive=True)
        #driver2.get("http://fiitjeenorthwest.com/time_table.php")
        bot.send_chat_action(chat_id, 'typing')
        #ping()
        #mycursor.execute("SELECT Theme FROM visitors WHERE Chat_Id='" + str(chat_id) + "' ")
        #data = mycursor.fetchall()
        # print(data, data[0][0])
        theme = dic[chat_id]['theme']
        if theme == None:
            theme = 'Night'
        elif theme == 'Random':
            theme = random.choice(['Vintage', 'Dark', 'Light', 'Night', 'Classic'])
        id = chat_id
        try:
            element = Select(driver.find_element_by_tag_name('select'))
        except:
            try:
                driver.refresh()
                driver.get("http://fiitjeenorthwest.com/time_table.php")
            except:
                pass
        try:
            element = Select(driver.find_element_by_tag_name('select'))
        except:
            driver.get_screenshot_as_file('ss_error.png')
            try:
                bot.send_photo(id, photo=open(f'{batch}.png', 'rb'), reply_markup=markup)
                bot.send_message(id, "The site can't be reached, this is backed up routine.😀")
                return None
            except:
                bot.send_message(id, "The site can't be reached right now😀", reply_markup=markup)
                return None
        try:
            element.select_by_value(batch)
            bot.send_message(id, "Sending Routine, Please wait!", reply_markup=markup)
            bot.send_chat_action(chat_id, 'upload_photo')
        except:
            bot.send_message(id, "No Batch Found😀", reply_markup=markup)
            return 'no'
        driver.find_element_by_name('submit').click()
        if theme in ['Vintage', 'Dark', 'Light', 'Night']:

            sleep(1)
            table = driver.find_element_by_xpath('//*[@id="banner_flash1"]/div[3]/table[4]')
            rows = table.find_elements_by_tag_name('tr')

            lst = []
            for row in rows:
                columns = row.find_elements_by_tag_name('td')
                lst.append([i.text for i in columns])

            imageMaker(lst, batch, theme)

            try:
                bot.send_photo(id, photo=open(f'{batch}_{theme}.png', 'rb'), reply_markup=markup)
            except:
                bot.send_photo(id, photo=open(f'Schedule.png', 'rb'), reply_markup=markup)
            print('image sent')
            #driver.quit()
            return None

        elif theme == 'Classic':
            node = driver.find_element_by_xpath("//*[@id='banner_flash1']/div[3]/table[3]/tbody/tr[1]")
            script = "arguments[0].insertAdjacentHTML('afterEnd', arguments[1])"
            driver.execute_script(script, node,
                                  f'<tr><td width="2">&nbsp;</td><td><div class="breadcrumb2" style="text-align:justify; margin-top:-5px; padding:0px 5px 0px 5px; font-size:14px;">Telegram :- <b style="color:#000066">@FiitjeePunjabiBagh_Bot</b></div></td></tr>'
                                  f'<tr><td width="2">&nbsp;</td><td><div class="breadcrumb2" style="text-align:justify; margin-top:-5px; padding:0px 5px 0px 5px; font-size:14px;">Updated :- <b style="color:#000066">{str(str(datetime.datetime.now(IST))[:19])}</b></div></td></tr>')

            driver.find_element_by_class_name('banner_flash1_mid_DATADATA').screenshot('Schedule.png')
            im = Image.open(os.path.abspath('Schedule.png'))
            im = im.crop((0, 102, *im.size))
            im.save('Schedule.png')
            bot.send_photo(id, photo=open(f'Schedule.png', 'rb'), reply_markup=markup)
            print('image sent')
            # driver.refresh()
            #driver2.quit()
            return None

    def sendFile(chat_id, filename):
        try:
            bot.send_document(chat_id, data=open(filename, 'rb').read(), visible_file_name=filename)
        except:
            bot.send_message(chat_id, "File doesn't exist")

    def venue(batch):
        # import tabula

        # def ravi():
        url = 'http://fiitjeenorthwest.com/time_table.php'
        try:
            session = HTMLSession()
            response = session.get(url)

        except requests.exceptions.RequestException as e:
            return None
            print(e)

        meta_desc = response.html.xpath('//*[@id="banner_flash1"]/div[1]/div/div[7]/a')
        #print(meta_desc)
        link = 'http://fiitjeenorthwest.com/' + meta_desc[0].attrs['href']
        df = tabula.read_pdf(link, pages='all')

        rohtak13 = []
        rohtak15 = []
        central = []
        date = df[0].values.tolist()[1][0]
        if ':' in date:
            date = date.split(':')[1]
        else : date.split(' ')[1]
        # batch = 'NWCM123A1R'
        for table in df:
            lst = table.values.tolist()
            # print(lst)
            #date = lst[1][0]
            for i in lst:
                if '13/35ROHTAK' in str(i[0]).replace(' ', ''):
                    try:
                        rohtak13 += lst[lst.index(i):]
                        print('Hi', rohtak13)
                        central += lst[:lst.index(i)]
                    except Exception as e:
                        print(e,56)
                elif '15/35ROHTAK' in str(i[0]).replace(' ', ''):
                    rohtak15 += lst[lst.index(i):]
                    central += lst[:lst.index(i)]
            else:
                central += lst

        venues = [rohtak13, rohtak15, central]
        for venue in venues:
            #print(venue)
            for i in range(len(venue)):
                if batch in str(venue[i][0]):
                    return [venue[0][0], f'Room no. {venue[i][1]}', date]

        return ['Venue : Not available', 'Room no. : Not Available', date]
        # #print(link)
        # file1 = 'http://fiitjeenorthwest.com/seatingplan/SP18D.pdf'
        # table = tabula.read_pdf(link, pages=1)
        # # type(table)
        # lst = (table[0].values.tolist())
        # date = lst[1][0]
        # for i in lst:
        #     if 'ROHTAK' in str(i[0]):
        #         rohtak1 = lst[lst.index(i):]
        #         central = lst[:lst.index(i)]
        #     else:
        #         central = lst
        #         rohtak = []
        # try:
        #     table = tabula.read_pdf(link, pages=2)
        #
        #     lst = (table[0].values.tolist())
        #     for i in lst:
        #         if 'ROHTAK' in str(i[0]):
        #             rohtak2 = lst[lst.index(i):]
        #             central += lst[:lst.index(i)]
        #         else:
        #             central += lst
        #             rohtak2 = []
        #
        # except:
        #     rohtak2=[]
        #
        # try:
        #     table = tabula.read_pdf(link, pages=3)
        #
        #     lst = (table[0].values.tolist())
        #     for i in lst:
        #         if 'ROHTAK' in str(i[0]):
        #             rohtak3 = lst[lst.index(i):]
        #             central += lst[:lst.index(i)]
        #         else:
        #             central += lst
        #             rohtak3 = []
        # except:
        #     rohtak3=[]
        #
        #
        # #print(rohtak1)
        # #print(central)
        # # print(type(table[0]))
        #
        # batch = batch
        # for i in rohtak1:
        #     if batch in str(i[0]):
        #         return [rohtak1[0][0], f'Room no. {i[1]}', date.split(':')[1]]
        # for i in rohtak2:
        #     if batch in str(i[0]):
        #         return [rohtak2[0][0], f'Room no. {i[1]}', date.split(':')[1]]
        # for i in rohtak3:
        #     if batch in str(i[0]):
        #         return [rohtak3[0][0], f'Room no. {i[1]}', date.split(':')[1]]
        # for i in central:
        #     if batch in str(i[0]):
        #         return ['Venue : CENTRAL MARKET, PUNJABI BAGH', f'Room no. {i[1]}', date.split(':')[1]]
        # return ['Venue : Not available', 'Room no. : Not Available', date.split(':')[1]]

    def today(uid, batc=None, delta=0, dnd=False):
        if batc == None:
            bot.send_chat_action(uid, 'typing')
            batch = dic[uid]['batch']
        else: batch = batc
        element = Select(driver.find_element_by_tag_name('select'))
        try:
            element.select_by_value(batch)
        except:
            bot.send_message(uid, 'Please Select a Default Batch', reply_markup= markup)
            return None
        driver.find_element_by_name('submit').click()
        table = driver.find_element_by_xpath('//*[@id="banner_flash1"]/div[3]/table[4]')
        rows = table.find_elements_by_tag_name('tr')

        lst = []
        for row in rows:
            columns = row.find_elements_by_tag_name('td')
            lst.append([i.text for i in columns])
        try:
            venu = venue(batch)
            # if venu == None: raise
        except Exception as e:
            print(e, 2)
            if not dnd:
                venu = ['Venue : Not Available', 'Room No. : Not Available', '']
                # bot.send_message(uid, 'Site cant be reached right now', reply_markup=markup)
            # return None
        NextDay_Date = datetime.datetime.now(IST) + datetime.timedelta(days=delta)
        nday = NextDay_Date.strftime('%d-%m-%Y')
        print(nday)
        print(venu[2])
        if not str(nday) in venu[2]:
            venu = ['Venue : Not Available', 'Room No. : Not Available']

        day = (datetime.datetime.now(IST).weekday() + delta)%7
        print(day)
        #print(lst)
        #bot.send_message(uid, str(day))
        if lst[1][day]+lst[2][day]+lst[3][day]+lst[4][day] == '':
            if dnd: return None
            msg2 = 'No Class, Chill!😂'
        else: 
            msg2 = '👉 '+lst[1][day]+'\n👉 '+lst[2][day]+'\n👉 '+lst[3][day]+'\n'+lst[4][day]
        msg = f'{lst[0][day]}\n' \
              f'Batch : {batch}\n' \
              f'⸻⸻⸻⸻⸻⸻⸻\n'\
              f'{venu[0]}\n' \
              f'{venu[1]}\n' \
              f'⸻⸻⸻⸻⸻⸻⸻\n'\
              f'{msg2}\n' 

        bot.send_message(uid, msg, reply_markup=markup)
        if batc == None: return None
        url = 'http://fiitjeenorthwest.com/time_table.php'

        session = HTMLSession()
        response = session.get(url)

        meta_desc = response.html.xpath('//*[@id="banner_flash1"]/div[1]/div/div[7]/a')
        print(meta_desc)
        link = 'http://fiitjeenorthwest.com/' + meta_desc[0].attrs['href']
            #   for i in meta_desc:
            #   print(i.absolute_links)
            # link = list(i.absolute_links)[0]

        bot.send_document(uid, link)
        
    def everyday():
        ping()
        mycursor.execute("SELECT Chat_Id, DefaultBatch from visitors")
        data = mycursor.fetchall()
        print(data)
        allId = list(set([i[0] for i in data]))
        print(allId)
        
        for uid, batch in data:
            print(uid)
            if not batch == None:
                try:
                    today(uid, batch, dnd =True)
                    
                except Exception as e:
                    pass
                    print(e)
                    print('    Passed')

    def restart():
        PROCESS = 'worker.1'
        HEADERS = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": ''
        }
        url = "https://api.heroku.com/apps/" + app + "/dynos/" + PROCESS

        print(url)
        result = requests.delete(url, headers=HEADERS)
        print(result)
        print(result.content)

    def stopDyno():
        # size = 1

        HEADERS = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": ''
        }
        payload = {'quantity': 1}
        url = "https://api.heroku.com/apps/" + app_info2['app'] + "/formation/worker"

        print(url)
        result = requests.patch(url, headers=HEADERS, data=payload)
        print(result)

        payload = {'quantity': 0}
        url = "https://api.heroku.com/apps/" + app + "/formation/worker"
        print(url)
        result = requests.patch(url, headers=HEADERS, data=payload)
        print(result.content)

    # schedule.every().day.at("00:00").do(imageUpdater)
    def sheduler():
        schedule.every().sunday.at("14:37").do(scheduler)
        schedule.every(15).days.at("20:30").do(stopDyno)
        #schedule.every(15).minutes.do(create_image)
        schedule.every().day.at("23:00").do(everyday)
        # schedule.every().day.at("13:50").do(play)
        # schedule.every().day.at("13:52").do(daily_notify)
        while True:
            day = datetime.datetime.now().strftime('%d')
            hour = datetime.datetime.now().strftime('%H')
            min = datetime.datetime.now().strftime('%M')
            if day == app_info['day'] and hour == app_info['hour']:
                stopDyno()
            schedule.run_pending()
            sleep(1)


    def everyday2():
        ping()
        mycursor.execute("SELECT Chat_Id FROM visitors")
        data2 = mycursor.fetchall()
        ids = [i[0] for i in data2]
        print(ids)
        try:
            for i in ids:
                try:
                    #bot.send_message(i, msg.capitalize())
                    today(ids)
                    
                    print(str(i) + '   sent')
                except Exception as e:
                    print(e)
                    print(str(i) + '   couldnt send ur msg')
                    pass
        except Exception as e:
            print(e)
            print('couldnt send ur msg')


    Thread(target=sheduler, args=()).start()

    @bot.message_handler(content_types="text")
    def sender(message):
        global xid
        print(message.chat.id)

        ping()
        if message.text.startswith('Sendfile'):
            sendFile(message.chat.id, message.text.split(maxsplit=1)[1])
        
        upperMsg = message.text.upper()

        if upperMsg in ['/START', 'START', 'HELP🧐', 'HELP']:
            startMsg(bot, message)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
            markup.add('Help', 'Batch List', 'Set Default Batch', 'Theme', 'Seating Plan', 'Send', 'Today', 'Tomorrow')
            # msg = bot.send_message(message.chat.id, 'Tap a Command', reply_markup=markup)

        checkVisitor(message, bot)
        if not message.chat.id == 16822843995:
            bot.send_chat_action(message.chat.id, 'typing')

        # upperMsg = message.text.upper()
        print(upperMsg + ' - ' + str('' if message.from_user.first_name is None else message.from_user.first_name))

        if upperMsg in ['/START', 'START', 'HELP🧐', 'HELP'] or message.chat.id == 16822843995:
            pass

        elif upperMsg in ['SEND', '/SEND', 'Send', 'SEND📮']:
                try:
                    msg = message
                    #mycursor.execute("SELECT DefaultBatch FROM visitors WHERE Chat_Id='" + str(message.chat.id) + "' ")
                    #data = mycursor.fetchall()
                    # print(data, data[0][0])
                    batch = dic[msg.chat.id]['batch']
                    print(batch)
                    out = start2(message.chat.id, batch)
                    if out == 'no':
                        # if batch == None or batch == 'BATCHCODE' or batch == '':
                        #print(batch, data)
                        # markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
                        # markup.add('Help', 'Batch List', 'Set Default Batch', 'Theme', 'Seating Plan', 'Send', 'Today), 'Tomorrow
                        bot.send_message(message.chat.id,
                                         'Your default batch is set to "' + str(batch) + '"\nThis is not a valid batch')
                        options = driver.find_elements_by_tag_name('option')
                        x = [i.get_attribute('value') for i in options]
                        markup2 = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
                        markup2.add(*sorted(x))
                        msg = bot.send_message(message.chat.id, 'Please Select Your Default Batch', reply_markup=markup2)
                        bot.register_next_step_handler(msg, setDefault)

                except Exception as e:
                    markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
                    markup.add('Help', 'Batch List', 'Set Default Batch', 'Theme', 'Seating Plan', 'Send', 'Today', 'Tomorrow')
                    bot.send_message(message.chat.id, 'Some error occured, please try again after some time😀',
                                     reply_markup=markup)

        elif upperMsg in [ 'SET DEFAULT BATCH📝',  'SET DEFAULT BATCH']:
            options = driver.find_elements_by_tag_name('option')
            x = [i.get_attribute('value') for i in options]
            markup2 = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
            markup2.add(*sorted(x))
            msg = bot.send_message(message.chat.id, 'Select Your Default Batch', reply_markup=markup2)
            bot.register_next_step_handler(msg, setDefault)

        elif upperMsg in ['TODAY', 'TODAY🎃']:
            bot.send_message(message.chat.id, 'Wait a sec.')
            today(message.chat.id)
        
        elif upperMsg in ['TOMORROW🍥', 'TOMORROW']:
            bot.send_message(message.chat.id, 'Wait a sec.')
            today(message.chat.id, delta=1)

        elif upperMsg in ['SEATING PLAN💢', 'SEATING PLAN']:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
            markup.add('Help', 'Batch List', 'Set Default Batch', 'Theme', 'Seating Plan', 'Send', 'Today', 'Tomorrow')
            url = 'http://fiitjeenorthwest.com/time_table.php'

            try:
                session = HTMLSession()
                response = session.get(url)

            except requests.exceptions.RequestException as e:
                print(e)

            meta_desc = response.html.xpath('//*[@id="banner_flash1"]/div[1]/div/div[7]/a')
            print(meta_desc)
            link = 'http://fiitjeenorthwest.com/' + meta_desc[0].attrs['href']
            #   for i in meta_desc:
            #   print(i.absolute_links)
            print(meta_desc[0].attrs['href'])
            # link = list(i.absolute_links)[0]
            try:
                bot.send_document(message.chat.id, link, reply_markup=markup)
            except:
                fn=meta_desc[0].attrs['href'].split('/')[-1]
                r = requests.get(link, allow_redirects=True)
                open(fn, 'wb').write(r.content)
                bot.send_document(message.chat.id, data=open(fn, 'rb').read(), visible_file_name=fn, reply_markup=markup)
              
                
            
            # file = str(datetime.datetime.now(IST).strftime('%d'))
        #     urfile'http://fiitjeenorthwest.com/seatingplan/SP{file}}D.pdf'
        # url =f'http://fiitjeenorthwest.com/seatingplan/SP{file}D.pdf'
        # r = requests.get(url, allow_redirects=True)
        # open('plan.pdf', 'wb').write(r.content)
        # sendFile(message.chat.id, 'plan.pdf')

        # driver2
        # driver3=webdriver.Chrome(options=chrome_options)
        # path = os.path.abspath('plan.pdf')
        # driver3.get(r"file:///" + path)
        # sleep(1)
        # driver3.save_screenshot('tara.png')
        # driver3.quit()
        # bot.send_photo(message.chat.id, open('tara.png', 'rb'))

        # elif upperMsg == 'SEATING PLAN💢':
        # url = 'http://fiitjeenorthwest.com/seatingplan/SP07D.pdf'
        #  r = requests.get(url, allow_redirects=True)
        # open('plan.pdf', 'wb').write(r.content)
        #   sendFile(message.chat.id, 'plan.pdf')

        elif upperMsg in ['THEME', 'THEME🍁']:
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            a = types.InlineKeyboardButton(text='Light', callback_data='theme_Light')
            b = types.InlineKeyboardButton(text='Dark', callback_data='theme_Dark')
            c = types.InlineKeyboardButton(text='Vintage', callback_data='theme_Vintage')
            d = types.InlineKeyboardButton(text='Night', callback_data='theme_Night')
            e = types.InlineKeyboardButton(text='Classic', callback_data='theme_Classic')
            f = types.InlineKeyboardButton(text='Random', callback_data='theme_Random')
            keyboard.add(a, b, c, d, e, f)
            bot.send_photo(message.chat.id, open('theme.png', 'rb'), reply_markup=keyboard)


        elif upperMsg == 'RESTART':
            restart()
            
        elif upperMsg in ['FEEDBACK', 'FEEDBACK❤️']:
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            a= types.InlineKeyboardButton(text='Good', callback_data='feed_Good')
            b = types.InlineKeyboardButton(text='Best', callback_data='feed_Best')
            c = types.InlineKeyboardButton(text='Superb', callback_data='feed_Excellent')
            d = types.InlineKeyboardButton(text='Mind Blowing', callback_data='feed_Mind Blowing')
            e = types.InlineKeyboardButton(text='All of these', callback_data='feed_all')
            keyboard.add(a,b,c,d,e)
            bot.send_message(message.chat.id, 'Feedback', reply_markup=keyboard)
            
            

        # elif upperMsg == 'SCHEDULE' or upperMsg == '/SCHEDULE':
        #     scheduleSetter(message)

        elif upperMsg in ['BATCHLIST', '/BATCHLIST', 'BATCH LIST📋', 'BATCH LIST']:
            keyboard = types.InlineKeyboardMarkup(row_width=2)

            options = driver.find_elements_by_tag_name('option')
            x = [i.get_attribute('value') for i in options]
            batches = ''
            for y in sorted(x):
                if not y == '':
                    a = types.InlineKeyboardButton(text=y, callback_data=y)
                    keyboard.add(a)

            bot.send_message(message.chat.id, 'Here are the batches.', reply_markup=keyboard)





        elif 'HI' in upperMsg or 'HELLO' in upperMsg or 'HEY' in upperMsg or 'HLO' in upperMsg or \
            'THANKS' in upperMsg or 'THANK' in upperMsg or 'TNX' in upperMsg or 'THNX' in upperMsg or 'BRO' in upperMsg or 'HELO' in upperMsg or upperMsg.startswith(
            'OK'):
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
            markup.add('Help', 'Batch List', 'Set Default Batch', 'Theme', 'Seating Plan', 'Send', 'Today', 'Tomorrow')
            bot.send_message(message.chat.id, 'This is a bot.\nTo contact me -> @raviarya131', reply_markup=markup)


        else:
            if upperMsg.startswith('/'): upperMsg = upperMsg[1:]
            start2(message.chat.id, upperMsg)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        # print(call.data)
        print(call.message.chat.id, call.data)
        if call.message:
            ping()
            if call.data == 'send':
                #mycursor.execute("SELECT DefaultBatch FROM visitors WHERE Chat_Id='" + str(call.message.chat.id) + "' ")
                #data = mycursor.fetchall()
                # print(data, data[0][0])
                batch = dic[call.message.chat.id]['batch']
                start2(call.message.chat.id, batch)
            elif call.data.startswith('theme'):
                sql = "UPDATE visitors SET Theme = '" + call.data[6:] + "' WHERE Chat_Id =" + str(call.message.chat.id)
                mycursor.execute(sql)
                mydb.commit()
                editUser(call.message.chat.id, 'theme', call.data[6:])
                # bot.edit_message_text('Your theme has been set to '+call.data[6:],call.message.chat.id, call.message.message_id)
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=False)
                markup.add('Help', 'Batch List', 'Set Default Batch', 'Theme', 'Seating Plan', 'Send', 'Today', 'Tomorrow')
                bot.send_message(call.message.chat.id, 'Your theme has been set to ' + call.data[6:], reply_markup=markup)
            elif call.data.startswith('sched'):
                scheduleSetter(call.message, call.data[6:])
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                if call.data[6:] == '1':
                    a = types.InlineKeyboardButton(text='✔ Turn on Scheduled Message', callback_data='sched_0')
                    keyboard.add(a)
                    bot.edit_message_text("Now you won't receive scheduled routine. You can always turn it on:",
                                          call.message.chat.id, call.message.message_id, reply_markup=keyboard)
                elif call.data[6:] == '0':
                    bot.edit_message_text("Now you will receive scheduled routine every Sunday. Chill!😅",
                                          call.message.chat.id, call.message.message_id)
                                          
                else:
                    pass
                # sql = "UPDATE visitors SET Schedule = '" + call.data[6:] + "' WHERE Chat_Id =" + str(call.message.chat.id)

            else:
                #pass
                bot.edit_message_text('👍', call.message.chat.id,
                                      call.message.message_id)
                start2(call.message.chat.id, call.data)
                sleep(1)

        schedule.run_pending()


    bot.infinity_polling()
    print('ravi')


while True:
    try:
        func()
    except Exception as e:
        # import sys
        # sys.modules[__name__].__dict__.clear()
        print(e)
        # keep_alive.shutdown()

        x = str(datetime.datetime.now(IST))[:19]
        if not mydb.is_connected():
            print('Database not connected to server')
            mydb.reconnect(attempts=10, delay=10)
        else:
            print('Database connected')
        sql = "INSERT INTO Errors (Error, Time) VALUES (%s, %s)"
        val = (str(e), x)
        mycursor.execute(sql, val)
        mydb.commit()

        sleep(2)

        print('Restarting Program')
        pass
