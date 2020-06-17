import logging

import schedule
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

from getgoogledata import get_japa_data
from time import sleep
import datetime
import os
import argparse

parser = argparse.ArgumentParser(description='Whatsapp BOT')
parser.add_argument('--chrome_driver_path', action='store', type=str, default='./chromedriver',
                    help='chromedriver executable')
parser.add_argument('--remove_cache', action='store', type=str, default='False',
                    help='Remove Cache | Scan QR again or Not')
args = parser.parse_args()

if args.remove_cache == 'True':
    os.system('rm -rf User_Data/*')
fail_over_phone = '917065557707'

link = "https://web.whatsapp.com/"
chrome_options = Options()
chrome_options.add_argument('--user-data-dir=./User_Data')
browser = webdriver.Chrome(executable_path="/Users/bthiruv/PycharmProjects/ARJNotification/chromedriver",
                           options=chrome_options)
browser.implicitly_wait(100)
browser.get(link)
browser.maximize_window()
print("QR scanned")


def invoke_whatsapp_unsaved_contact_url(phone):
    global browser

    try:
        print("invoke_whatsapp_unsaved_contact_url ")
        logging.debug("invoke_whatsapp_unsaved_contact_url ")
        if browser:
            unsaved_link = "https://web.whatsapp.com/send?phone={}&text&source&data&app_absent".format(phone)
            browser.get(unsaved_link)
        print("Sending message to ", phone)
    except Exception as e:
        print("Error invoke_whatsapp_unsaved_contact_url: {0}".format(e))
        sleep(10)
        print("retrying after sleep")
        unsaved_link = "https://web.whatsapp.com/send?phone={}&text&source&data&app_absent".format(phone)
        browser.get(unsaved_link)
        # Wait for the browser to load
        sleep(5)
        print("Sending message to ", phone)


def send_message(message):
    global browser

    try:
        sleep(12)
        input_box = browser.find_elements_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')[0]

        for ch in message:
            if ch == "\n":
                ActionChains(browser).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(
                    Keys.SHIFT).key_up(Keys.BACKSPACE).perform()
            else:
                input_box.send_keys(ch)
        input_box.send_keys(Keys.ENTER)
        print("Message sent successfully")
    except NoSuchElementException:
        print("Failed to send message")
    return


def sender():
    global browser
    now = datetime.datetime.now()
    now_plus = now + datetime.timedelta(minutes=17)
    reminder_slot = now_plus.strftime("%H.%M")
    print("Preparing Message for reminder slot " + reminder_slot)

    # to be moved to conf file
    title: str = "*Akhanda Rama Nama Japam - Reminder* \n \n"
    host_msg = "Jai Shriram! Gentle reminder for your Akhanda Rama Nama Japa hosting slot at IST "
    chant_msg = "Jai Shriram! Gentle reminder for your Akhanda Rama Nama Japa, Lord Rama is waiting to hear you at IST "
    notification: str = "   \n \n -- this is an automated reminder --  "
    channel_1 = "Channel 1: https://meetingsemea3.webex.com/meet/itadmin89  | 148910181"
    channel_2 = "Channel 2: https://personal-mkm.my.webex.com/meet/thiruvengadam.balaji | 1653111610"

    try:
        current_slot_data = get_japa_data(reminder_slot)
        for index, row in current_slot_data.iterrows():
            host_number = fail_over_phone  # Defaulting
            chanter_number = fail_over_phone  # Defaulting
            webex_link = None

            if row['Group'] == 'Japa1':
                webex_link = channel_1
            elif row['Group'] == 'Japa2':
                webex_link = channel_2

            print(row["Participants"], row["Chanters Number"], row["Group"])

            if not (row["Chanters Number"] and row["Chanters Number"].strip()):
                print("Mobile number is not available for " + row["Participants"])
            else:
                chanter_number = row["Chanters Number"]

            if row["Participants"] is not None and row["Participants"]:
                chanter_message = title + "Dear " + row[
                    "Participants"] + "," + "\n\n" + chant_msg + reminder_slot + " hours" + "\n\n" + \
                                  webex_link + notification
            else:
                chanter_message = title + chant_msg + reminder_slot + " hours" + "\n\n" + webex_link + \
                                  notification

            print(chanter_message)
            sleep(5)

            try:
                invoke_whatsapp_unsaved_contact_url(chanter_number)
                send_message(chanter_message)
                sleep(5)
            except Exception as e:
                print("Exception in loading chanter number " + chanter_number)
                print("Error : {0}".format(e))

            if not (row["Hosts Number"] and row["Hosts Number"].strip()):
                print("Mobile Number not available for " + row["Hosts"])
            else:
                host_number = row["Hosts Number"]

            print(row["Hosts"], row["Hosts Number"], row["Group"])

            if row["Hosts"] is not None and row["Hosts"]:
                host_message = title + "Dear " + row[
                    "Hosts"] + "," + "\n\n" + host_msg + reminder_slot + " hours" + "\n\n" + webex_link + \
                               notification
            else:
                host_message = title + host_msg + reminder_slot + "hours" + "\n\n" + webex_link + notification

            sleep(5)
            print(host_message)

            try:
                invoke_whatsapp_unsaved_contact_url(host_number)
                send_message(host_message)
                sleep(5)
            except Exception as e:
                print("Exception in loading host number " + host_number)
                print("Error : {0}".format(e))
                sleep(5)

    except Exception as e:
        print("Error : {0}".format(e))
        browser.close()


schedule.every().day.at("00:13").do(sender)
schedule.every().day.at("00:43").do(sender)
schedule.every().day.at("01:13").do(sender)
schedule.every().day.at("01:43").do(sender)
schedule.every().day.at("02:13").do(sender)
schedule.every().day.at("02:43").do(sender)
schedule.every().day.at("03:13").do(sender)
schedule.every().day.at("03:43").do(sender)
schedule.every().day.at("04:13").do(sender)
schedule.every().day.at("04:43").do(sender)
schedule.every().day.at("05:13").do(sender)
schedule.every().day.at("05:43").do(sender)
schedule.every().day.at("06:13").do(sender)
schedule.every().day.at("06:43").do(sender)
schedule.every().day.at("07:13").do(sender)
schedule.every().day.at("07:43").do(sender)
schedule.every().day.at("08:13").do(sender)
schedule.every().day.at("08:43").do(sender)
schedule.every().day.at("09:13").do(sender)
schedule.every().day.at("09:43").do(sender)
schedule.every().day.at("10:13").do(sender)
schedule.every().day.at("10:43").do(sender)
schedule.every().day.at("11:13").do(sender)
schedule.every().day.at("11:43").do(sender)
schedule.every().day.at("12:13").do(sender)
schedule.every().day.at("12:43").do(sender)
schedule.every().day.at("13:13").do(sender)
schedule.every().day.at("13:43").do(sender)
schedule.every().day.at("14:13").do(sender)
schedule.every().day.at("14:43").do(sender)
schedule.every().day.at("15:13").do(sender)
schedule.every().day.at("15:43").do(sender)
schedule.every().day.at("16:13").do(sender)
schedule.every().day.at("16:43").do(sender)
schedule.every().day.at("17:13").do(sender)
schedule.every().day.at("17:43").do(sender)
schedule.every().day.at("18:13").do(sender)
schedule.every().day.at("18:43").do(sender)
schedule.every().day.at("19:13").do(sender)
schedule.every().day.at("19:43").do(sender)
schedule.every().day.at("20:13").do(sender)
schedule.every().day.at("20:43").do(sender)
schedule.every().day.at("21:13").do(sender)
schedule.every().day.at("21:43").do(sender)
schedule.every().day.at("22:13").do(sender)
schedule.every().day.at("22:43").do(sender)
schedule.every().day.at("23:13").do(sender)
schedule.every().day.at("23:43").do(sender)


# To schedule your msgs
def scheduler():
    while True:
        schedule.run_pending()
        sleep(10)


if __name__ == "__main__":
    logging.basicConfig(filename='whatsappbot.log', format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',
                        level=logging.INFO)
    print("Web Page Open")
    # Let us login and Scan
    print("SCAN YOUR QR CODE FOR WHATSAPP WEB")

    sender()

    # First time message sending Task Complete
    print("Task Completed")

    # Messages are scheduled to send
    # Default schedule to send attachment and greet the personal
    # For GoodMorning, GoodNight and howareyou wishes
    # Comment in case you don't want to send wishes or schedule
    scheduler()
