import gspread
import json
import datetime
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st


def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = json.loads(st.secrets["google_sheets"]["service_account"])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
    client = gspread.authorize(credentials)

    return client.open_by_key(st.secrets["google_sheets"]["sheet_id"])


def save_data(role, data_dict, sheet_tab="General"):
    sheet = get_sheet()
    sheet_tab = sheet_tab or role

    try:
        worksheet = sheet.worksheet(sheet_tab)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=sheet_tab, rows="1000", cols="100")

    values = worksheet.get_all_values()

    required_headers = ["Timestamp", "Role"] + list(data_dict.keys())

    # If sheet is empty, add headers.
    if not values:
        headers = required_headers
        worksheet.append_row(headers)

    else:
        headers = values[0]

        # Detect bad old header row.
        # A valid header row should include Timestamp and Role.
        bad_headers = (
            "Timestamp" not in headers
            or "Role" not in headers
        )

        if bad_headers:
            # Insert correct headers at top, preserving old row below.
            worksheet.insert_row(required_headers, index=1)
            headers = required_headers
        else:
            missing_headers = [h for h in required_headers if h not in headers]

            if missing_headers:
                headers = headers + missing_headers
                worksheet.update("1:1", [headers])

    row_data = {
        "Timestamp": str(datetime.datetime.now()),
        "Role": role,
        **{k: str(v) for k, v in data_dict.items()}
    }

    row = [row_data.get(header, "") for header in headers]
    worksheet.append_row(row)