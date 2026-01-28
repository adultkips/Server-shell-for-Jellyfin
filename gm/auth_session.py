import requests
from .config import JELLYFIN_URL, USERNAME, PASSWORD
def auth_session():
    s = requests.Session()
    s.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Emby-Authorization":
            'MediaBrowser Client="ModelList", '
            'Device="Windows", '
            'DeviceId="jellyfin-model-list", '
            'Version="1.0.0"'
    })
    r = s.post(
        f"{JELLYFIN_URL}/Users/AuthenticateByName",
        json={"Username": USERNAME, "Pw": PASSWORD},
        timeout=20
    )
    r.raise_for_status()
    auth = r.json()
    s.headers["X-Emby-Token"] = auth["AccessToken"]
    user_id = auth["User"]["Id"]
    return s, user_id
