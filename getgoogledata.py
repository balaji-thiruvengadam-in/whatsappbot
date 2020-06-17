from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import pandas as pd


def get_google_data(sheet_range):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    # here enter the id of your google sheet
    SAMPLE_SPREADSHEET_ID_input = '19WH5cae3RqgbTTotJuPT5RS8xkRYaloDJPq-_7aBSrM'
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)  # here enter the name of your downloaded JSON file
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                range=sheet_range).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')

    return values


def get_japa_data(reminder_time):
    file_name = '/Users/bthiruv/PycharmProjects/ARJNotification/japa_data.csv'
    print("Getting Data from Google Sheet")
    try:
        japa_data_1 = get_google_data('japa1!A1:E100')
        japa_data_2 = get_google_data('japa2!A1:E100')
        df_japa1 = pd.DataFrame(japa_data_1[1:], columns=japa_data_1[1])
        df_japa2 = pd.DataFrame(japa_data_2[1:], columns=japa_data_2[1])

        df_japa1['Group'] = 'Japa1'
        df_japa2['Group'] = 'Japa2'

        df_japa = df_japa1.append(df_japa2)

        if os.path.exists(file_name):
            print("Old file is removed")
            os.remove(file_name)
        else:
            print("Can not delete the file as it doesn't exists")

        df_japa.to_csv(file_name)

    except Exception as e:
        print("Error in reading google Sheet, Use local sheet")
        print("Exception get_japa_data: {0}".format(e))
        # In case of failure reading google sheet, use local file
        df_japa = pd.read_csv(file_name)

    # new data frame with split value columns
    slot_split = df_japa["Slot"].str.split("-", n=1, expand=True)

    # making separate from new data frame
    df_japa["StartTime"] = slot_split[0]
    df_japa["EndTime"] = slot_split[1]

    current_slot_data = df_japa.loc[df_japa['StartTime'] == reminder_time]

    return current_slot_data
