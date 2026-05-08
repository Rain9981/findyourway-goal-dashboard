import gspread
import json
import datetime
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st


def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = json.loads(st.secrets["google_sheets"]["service_account"])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
    client = gspread.authorize(credentials)

    return client.open_by_key(st.secrets["google_sheets"]["sheet_id"])


def _row_has_real_headers(row):
    if not row:
        return False

    clean_row = [str(cell).strip() for cell in row]

    return "Timestamp" in clean_row and "Role" in clean_row


def save_data(role, data_dict, sheet_tab=None):
    sheet = get_sheet()
    sheet_tab = sheet_tab or role

    try:
        worksheet = sheet.worksheet(sheet_tab)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(
            title=sheet_tab,
            rows="1000",
            cols="100"
        )

    required_headers = ["Timestamp", "Role"] + list(data_dict.keys())
    values = worksheet.get_all_values()

    header_row_index = None

    for idx, row in enumerate(values, start=1):
        if _row_has_real_headers(row):
            header_row_index = idx
            break

    if not values:
        worksheet.append_row(required_headers)
        headers = required_headers

    elif header_row_index is None:
        worksheet.insert_row(required_headers, index=1)
        headers = required_headers

    else:
        headers = values[header_row_index - 1]

        missing_headers = [
            header for header in required_headers
            if header not in headers
        ]

        if missing_headers:
            headers = headers + missing_headers
            worksheet.update(
                f"{header_row_index}:{header_row_index}",
                [headers]
            )

    row_data = {
        "Timestamp": str(datetime.datetime.now()),
        "Role": role,
        **{key: str(value) for key, value in data_dict.items()}
    }

    row = [row_data.get(header, "") for header in headers]
    worksheet.append_row(row)

    return True