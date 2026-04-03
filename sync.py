import os
import json
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_DATABASE_ID = "29e0133858d7803e93cade22c5a7a58d"
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_notion_pages():
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    pages = []
    cursor = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        resp = requests.post(url, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        pages.extend(data["results"])
        if not data.get("has_more"):
            break
        cursor = data["next_cursor"]
    return pages


def parse_page(page):
    props = page["properties"]

    # Name
    title_list = props.get("Name", {}).get("title", [])
    name = title_list[0]["plain_text"] if title_list else "(İsimsiz)"

    # Date
    date_prop = props.get("Date", {}).get("date")
    date = date_prop["start"] if date_prop else None

    # Status
    status_prop = props.get("Status", {})
    if status_prop.get("type") == "status":
        status = (status_prop.get("status") or {}).get("name", "")
    elif status_prop.get("type") == "select":
        status = (status_prop.get("select") or {}).get("name", "")
    else:
        status = ""

    return {"id": page["id"], "name": name, "date": date, "status": status}


def get_calendar_service():
    creds_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
    token_json = os.environ["GOOGLE_TOKEN_JSON"]
    creds_info = json.loads(token_json)
    client_info = json.loads(creds_json)

    creds = Credentials(
        token=creds_info["token"],
        refresh_token=creds_info["refresh_token"],
        token_uri=client_info["installed"]["token_uri"],
        client_id=client_info["installed"]["client_id"],
        client_secret=client_info["installed"]["client_secret"],
        scopes=SCOPES,
    )
    return build("calendar", "v3", credentials=creds)


def get_existing_events(service):
    """notion_id içeren tüm eventleri çek."""
    events = {}
    page_token = None
    while True:
        result = service.events().list(
            calendarId="primary",
            privateExtendedProperty="sync_source=notion",
            pageToken=page_token,
            maxResults=250,
        ).execute()
        for e in result.get("items", []):
            desc = e.get("description", "")
            for line in desc.splitlines():
                if line.startswith("notion_id:"):
                    nid = line.split(":", 1)[1].strip()
                    events[nid] = e
                    break
        page_token = result.get("nextPageToken")
        if not page_token:
            break
    return events


def sync():
    service = get_calendar_service()
    existing = get_existing_events(service)
    notion_pages = get_notion_pages()

    notion_ids_with_date = set()

    for page in notion_pages:
        p = parse_page(page)
        nid = p["id"]

        if p["date"]:
            notion_ids_with_date.add(nid)
            body = {
                "summary": f"🗓 {p['name']}",
                "description": f"Durum: {p['status']}\nnotion_id: {nid}",
                "start": {"date": p["date"][:10]},
                "end": {"date": p["date"][:10]},
                "extendedProperties": {"private": {"sync_source": "notion"}},
            }

            if nid in existing:
                ev = existing[nid]
                # Güncelle (başlık veya durum değiştiyse)
                if ev.get("summary") != body["summary"] or ev.get("description") != body["description"]:
                    service.events().update(
                        calendarId="primary", eventId=ev["id"], body=body
                    ).execute()
                    print(f"[GÜNCELLENDI] {p['name']}")
                else:
                    print(f"[AYNI] {p['name']}")
            else:
                service.events().insert(calendarId="primary", body=body).execute()
                print(f"[EKLENDI] {p['name']}")

    # Tarih kalkan veya Notion'dan silinen kayıtları Calendar'dan sil
    for nid, ev in existing.items():
        if nid not in notion_ids_with_date:
            service.events().delete(calendarId="primary", eventId=ev["id"]).execute()
            print(f"[SILINDI] {ev.get('summary', nid)}")

    print("✅ Senkronizasyon tamamlandı.")


if __name__ == "__main__":
    sync()
