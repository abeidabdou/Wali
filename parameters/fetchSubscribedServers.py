from firebase_admin import db
from firebase_admin import credentials
import firebase_admin
import os
import json
from dotenv import load_dotenv

load_dotenv()

cred = credentials.Certificate(json.loads(
    os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')))
firebase_admin.initialize_app(cred, {
    'databaseURL': os.getenv('FIREBASE_REALTIME_DB_URL')
})


def fetch_servers():
    ref = db.reference('members')
    members = ref.get()
    if members:
        all_servers = set()
        for servers in members.values():
            for server_id in servers.keys():
                all_servers.add(int(server_id))
        return all_servers
    return None
