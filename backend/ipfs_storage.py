import requests
import json

# ---------------- UPLOAD TO IPFS
def upload_to_ipfs(data):

    url = "http://127.0.0.1:5001/api/v0/add"

    files = {
        "file": (
            "prescription.json",
            json.dumps(data)
        )
    }

    res = requests.post(url, files=files)

    return res.json()["Hash"]


# ---------------- FETCH FROM IPFS (FIXED)
def get_prescription_from_ipfs(ipfs_hash):

    url = f"http://127.0.0.1:8850/ipfs/{ipfs_hash}"

    res = requests.get(url)

    if res.status_code != 200:
        return None

    # Try JSON
    try:
        return res.json()
    except:
        pass

    # Try text JSON
    try:
        return json.loads(res.text)
    except:
        pass

    # Fallback raw content
    return res.text