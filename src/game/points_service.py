import json
import os
import time

REQUEST_FILE = "points_request.json"
RESPONSE_FILE = "points_response.json"
DB_FILE = "points_db.json"

# Loads data from a json file, and returns it as a dictionary
def load_db():
    # checks if file exists
    if not os.path.exists(DB_FILE):
        return {}
    # if it does, it loads the data and returns it as a dictionary
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # handles errors
    except Exception:
        return {}

# Safely saves a dictionary to a json file
def save_db(db):
    # creates temp file
    tmp = DB_FILE + ".tmp"
    # writes the data to the temp file
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f)
    # replaces the original
    os.replace(tmp, DB_FILE)

# safely writes a response to a json file
def write_response(obj):
    # writes the response to the temp file
    with open(RESPONSE_FILE, "w", encoding="utf-8") as f:
        json.dump(obj, f)

# processes requests to add or retrieve points for a user
def process_request(req):
    # loads the database
    db = load_db()
    # extracts request info
    req_type = req.get("request_type")
    points_id = str(req.get("points_id"))

    # if post request, adds points to point's account
    if req_type == "POST":
        added = int(req.get("added_points", 0))
        current = int(db.get(points_id, 0))
        new_total = current + added
        if new_total < 0:
            new_total = 0
        db[points_id] = new_total
        save_db(db)
        resp = {"Points": new_total}
        resp["request_id"] = req.get("request_id")
        return resp

    # if get request, returns the user's current points total
    elif req_type == "GET":
        total = int(db.get(points_id, 0))
        resp = {"Points": total}
        resp["request_id"] = req.get("request_id")
        return resp

    # if neither, returns an error
    else:
        resp = {"error": "unknown request_type"}
        resp["request_id"] = req.get("request_id")
        return resp


def main():
    while True:
        try:
            # checks for request file
            if os.path.exists(REQUEST_FILE):
                # reads and parses the request
                with open(REQUEST_FILE, "r", encoding="utf-8") as f:
                    try:
                        req = json.load(f)
                    # handles bad json
                    except Exception:
                        write_response({"error": "bad request json"})
                        time.sleep(1)
                        continue
                # processes the request and writes the response          
                resp = process_request(req)
                write_response(resp)
        # handles graceful shutdown
        except KeyboardInterrupt:
            break
        except Exception:
            # ignore and continue polling
            pass
        # waits before polling again
        time.sleep(1)


if __name__ == "__main__":
    main()
