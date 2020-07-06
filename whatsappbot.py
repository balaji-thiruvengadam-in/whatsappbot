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
parser.add_argument('--chrome_driver_path', action='store', type=str, default='./chromedriver.exe',
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
browser = webdriver.Chrome(executable_path="F:\development\whatsappbot-master\chromedriver.exe",
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
    now_plus = now + datetime.timedelta(minutes=18)
    reminder_slot = now_plus.strftime("%H.%M")
    print("Preparing Message for reminder slot " + reminder_slot)

    # to be moved to conf file
    title: str = "*Akhanda Rama Nama Japam* \n \n"
    host_msg = "Jai Shriram! Gentle reminder for your hosting slot at IST "
    chant_msg = "Jai Shriram! Gentle reminder for your Rama Nama Japa, Lord Rama is waiting to hear you at IST "
    communication = "\n\nFor any interruption, contact +91 8310286620"
    notification: str = "   \n\n -- this is an automated message --  "
    #channel_1 = "Channel 1: https://meetingsemea3.webex.com/meet/itadmin89  | 148910181"
    channel_1 = "https://adpmeet.webex.com/meet/balaji.thiruvengadam | 711 050 143"
    channel_2 = "Channel 2: https://personal-mkm.my.webex.com/meet/thiruvengadam.balaji | 1653111610"
    channel_3 = "Channel 3: https://individual-vib.my.webex.com/meet/ramanama-channel3 | 1652544392"

    try:
        current_slot_data = get_japa_data(reminder_slot)
        for index, row in current_slot_data.iterrows():
            host_number = fail_over_phone  # Defaulting
            chanter_number = fail_over_phone  # Defaulting
            webex_link = None
            chanter_details = None

            if row['Group'] == 'Japa1':
                webex_link = channel_1
            elif row['Group'] == 'Japa2':
                webex_link = channel_2
            elif row['Group'] == 'Japa3':
                webex_link = channel_3

            print(row["Participants"], row["Chanters Number"], row["Group"])

            if not (row["Chanters Number"] and row["Chanters Number"].strip()):
                print("Mobile number is not available for " + row["Participants"])
            else:
                chanter_number = row["Chanters Number"]

            if row["Participants"] is not None and row["Participants"]:
                chanter_message = title + "Dear " + row[
                    "Participants"] + "," + "\n\n" + chant_msg + reminder_slot + " hours" + "\n\n" + \
                                  webex_link + notification
                chanter_details = "Chanter: " + row["Participants"] + " | " + row["Chanters Number"] + "\n\n"
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
                extn = reminder_slot+"_"+chanter_number
                browser.save_screenshot("./Error_Screenshots/err_screen{0}.png".format(extn))
                print("Exception in loading chanter number " + chanter_number)
                print("Error : {0}".format(e))

                sleep(10)
                try:
                    print("retrying...")
                    invoke_whatsapp_unsaved_contact_url(chanter_number)
                    send_message(chanter_message)
                except Exception as e:
                    extn = reminder_slot + "_" + chanter_number + "_1"
                    browser.save_screenshot("./Error_Screenshots/err_screen{0}.png".format(extn))
                    print("Exception in loading chanter number " + chanter_number)
                    print("Error : {0}".format(e))

            if not (row["Hosts Number"] and row["Hosts Number"].strip()):
                print("Mobile Number not available for " + row["Hosts"])
            else:
                host_number = row["Hosts Number"]

            print(row["Hosts"], row["Hosts Number"], row["Group"])

            if row["Hosts"] is not None and row["Hosts"]:
                host_message = title + "Dear " + row[
                    "Hosts"] + "," + "\n\n" + host_msg + reminder_slot + " hours" + "\n\n" + chanter_details + \
                               webex_link + communication + notification
            else:
                host_message = title + host_msg + reminder_slot + "hours" + "\n\n" + chanter_details + \
                               webex_link + communication + notification

            sleep(5)
            print(host_message)

            try:
                invoke_whatsapp_unsaved_contact_url(host_number)
                send_message(host_message)
                sleep(5)
            except Exception as e:
                extn = reminder_slot + "_" + chanter_number
                browser.save_screenshot("./Error_Screenshots/err_screen{0}.png".format(extn))
                print("Exception in loading host number " + host_number)
                print("Error : {0}".format(e))
                sleep(10)
                try:
                    invoke_whatsapp_unsaved_contact_url(host_number)
                    send_message(host_message)
                except Exception as e:
                    extn = reminder_slot + "_" + chanter_number + "_1"
                    browser.save_screenshot("./Error_Screenshots/err_screen{0}.png".format(extn))
                    print("Retrying Exception in loading host number " + host_number)
                    print("Error : {0}".format(e))

    except Exception as e:
        print("Error : {0}".format(e))
        browser.close()


schedule.every().day.at("00:12").do(sender)
schedule.every().day.at("00:42").do(sender)
schedule.every().day.at("01:12").do(sender)
schedule.every().day.at("01:42").do(sender)
schedule.every().day.at("02:12").do(sender)
schedule.every().day.at("02:42").do(sender)
schedule.every().day.at("03:12").do(sender)
schedule.every().day.at("03:42").do(sender)
schedule.every().day.at("04:12").do(sender)
schedule.every().day.at("04:42").do(sender)
schedule.every().day.at("05:12").do(sender)
schedule.every().day.at("05:42").do(sender)
schedule.every().day.at("06:12").do(sender)
schedule.every().day.at("06:42").do(sender)
schedule.every().day.at("07:12").do(sender)
schedule.every().day.at("07:42").do(sender)
schedule.every().day.at("08:12").do(sender)
schedule.every().day.at("08:42").do(sender)
schedule.every().day.at("09:12").do(sender)
schedule.every().day.at("09:42").do(sender)
schedule.every().day.at("10:12").do(sender)
schedule.every().day.at("10:42").do(sender)
schedule.every().day.at("11:12").do(sender)
schedule.every().day.at("11:42").do(sender)
schedule.every().day.at("12:12").do(sender)
schedule.every().day.at("12:42").do(sender)
schedule.every().day.at("13:12").do(sender)
schedule.every().day.at("13:42").do(sender)
schedule.every().day.at("14:12").do(sender)
schedule.every().day.at("14:42").do(sender)
schedule.every().day.at("15:12").do(sender)
schedule.every().day.at("15:42").do(sender)
schedule.every().day.at("16:12").do(sender)
schedule.every().day.at("16:42").do(sender)
schedule.every().day.at("17:12").do(sender)
schedule.every().day.at("17:42").do(sender)
schedule.every().day.at("18:12").do(sender)
schedule.every().day.at("18:42").do(sender)
schedule.every().day.at("19:12").do(sender)
schedule.every().day.at("19:42").do(sender)
schedule.every().day.at("20:12").do(sender)
schedule.every().day.at("20:42").do(sender)
schedule.every().day.at("21:12").do(sender)
schedule.every().day.at("21:42").do(sender)
schedule.every().day.at("22:12").do(sender)
schedule.every().day.at("22:42").do(sender)
schedule.every().day.at("23:12").do(sender)
schedule.every().day.at("23:42").do(sender)


# To schedule your msgs
def scheduler():
    while True:
        schedule.run_pending()
        sleep(10)


if __name__ == "__main__":
    logging.basicConfig(filename='whatsappbot.log', format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p',
                        level=logging.INFO)
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
