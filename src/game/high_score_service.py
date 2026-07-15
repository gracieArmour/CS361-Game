import json

# constants
REQUEST_FILE = "high_score_request.json"
RESPONSE_FILE = "high_score_response.json"
DB_FILE = "high_score_db.json"

# variables
old_request = 0
db = []

# functions
def sorting_key(entry):
    return entry['points']

def save_db():
    global db

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db,f)


def process_request(request):
    global db

    print("Request received: ",request)

    if ('post' == request['type']):
        response = update_score(request)
    else:
        response = get_list()
    response['req_id'] = request['req_id']
    response['type'] = request['type']
    return response

def update_score(request):
    global db

    selected_score = -1
    response = {
        "highscore": "n"
    }

    if (len(db) > 0):
        for i, entry in enumerate(db):
            if entry['name'] == request['name']:
                selected_score = i
    
    updated_scores = False
    if selected_score < 0:
        db.append({
            "name": request['name'],
            "points": request['points']
        })
        updated_scores = True
    else:
        if db[selected_score]['points'] < request['points']:
            db[selected_score]['points'] = request['points']
            updated_scores = True
    
    if (updated_scores):
        db.sort(reverse=True,key=sorting_key)
        save_db()
        response['highscore'] = 'y'
    
    return response

def get_list():
    global db

    response = {
        "entries": []
    }
    if len(db) < 1:
        return response
    
    for i in range(0,min(len(db),10)):
        response["entries"].append(db[i])
    
    return response


def send_response(response):
    with open(RESPONSE_FILE, "w", encoding="utf-8") as f:
        json.dump(response, f)
    print("Response sent: ",response)


def init():
    with open(REQUEST_FILE, "w", encoding="utf-8"):
        pass
    
    with open(RESPONSE_FILE, "w", encoding="utf-8"):
        pass

    with open(DB_FILE, "a", encoding="utf-8") as f:
        pass
    
    with open(DB_FILE, "r", encoding="utf-8") as f:
        contents = f.read()
        if contents != "":
            data = json.loads(contents)
            return data
        else:
            return []

# MAIN LOOP
def main():
    global db
    global old_request

    db = init()

    while True:
        # check for new request
        request={
            "req_id": old_request
        }
        with open(REQUEST_FILE, "r", encoding="utf-8") as f:
            try:
                contents = f.read()
                if (contents != ""):
                    request = json.loads(contents)
            except Exception as e:
                print(e)
            else:
                if (request['req_id'] != old_request):
                    old_request = request['req_id']
                    send_response(process_request(request))
        

if __name__ == "__main__":
    main()