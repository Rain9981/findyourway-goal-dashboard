import gspread
import json
import datetime
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def save_data(role, data_dict, sheet_tab="General"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = json.loads(st.secrets["google_sheets"]["service_account"])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(st.secrets["google_sheets"]["sheet_id"])

    # ✅ Use role name as sheet tab if none explicitly provided
    sheet_tab = sheet_tab or role

    worksheet = None
    try:
        worksheet = sheet.worksheet(sheet_tab)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=sheet_tab, rows="100", cols="20")

    # ✅ Add headers only if empty
    if not worksheet.get_all_values():
        headers = ["Timestamp", "Role"] + list(data_dict.keys())
        worksheet.append_row(headers)

    row = [str(datetime.datetime.now()), role] + [str(v) for v in data_dict.values()]
    worksheet.append_row(row)
