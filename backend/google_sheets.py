import gspread
import json
import datetime
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st


SYSTEM_HEADERS = ["Timestamp", "Role"]


def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = json.loads(st.secrets["google_sheets"]["service_account"])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
    client = gspread.authorize(credentials)

    return client.open_by_key(st.secrets["google_sheets"]["sheet_id"])


def _is_real_header_row(row, required_headers):
    if not row:
        return False
    return all(h in row for h in SYSTEM_HEADERS) and any(
        h in row for h in required_headers if h not in SYSTEM_HEADERS
    )


def _find_header_row_index(values, required_headers):
    for index, row in enumerate(values, start=1):
        if _is_real_header_row(row, required_headers):
            return index
    return None


def save_data(role, data_dict, sheet_tab=None):
    sheet = get_sheet()
    sheet_tab = sheet_tab or role

    try:
        worksheet = sheet.worksheet(sheet_tab)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=sheet_tab, rows="1000", cols="100")

    required_headers = SYSTEM_HEADERS + list(data_dict.keys())
    values = worksheet.get_all_values()

    header_row_index = _find_header_row_index(values, required_headers)

    if not values:
        worksheet.append_row(required_headers)
        headers = required_headers

    elif header_row_index is None:
        worksheet.insert_row(required_headers, index=1)
        headers = required_headers
        header_row_index = 1

    else:
        headers = values[header_row_index - 1]
        missing_headers = [h for h in required_headers if h not in headers]
        if missing_headers:
            headers = headers + missing_headers
            worksheet.update(f"{header_row_index}:{header_row_index}", [headers])

    row_data = {
        "Timestamp": str(datetime.datetime.now()),
        "Role": role,
        **{k: str(v) for k, v in data_dict.items()},
    }

    row = [row_data.get(header, "") for header in headers]
    worksheet.append_row(row)

    return True