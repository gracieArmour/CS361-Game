import json
import random
from datetime import datetime
import math

# constants
REQUEST_FILE = "death_message_request.json"
RESPONSE_FILE = "death_message_response.json"
DB_FILE = "death_message_db.json"

# variables
old_request = 0

# functions
def get_message(all_messages):
    message_index = math.floor(random.random() * len(all_messages))
    return all_messages[message_index]

def send_response(req_id,message):
    response = {
        'req_id': req_id,
        'message': message
    }

    with open(RESPONSE_FILE, "w", encoding="utf-8") as f:
        json.dump(response, f)
    
    print("Response sent: ",response)


def init():
    global old_request
    with open(REQUEST_FILE, "w", encoding="utf-8"):
        pass
    
    with open(RESPONSE_FILE, "w", encoding="utf-8"):
        pass
    
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# MAIN LOOP
def main():
    random.seed(datetime.now().timestamp())

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
                    print("Request received: ",request)
                    old_request = request['req_id']
                    selected_message = get_message(db)
                    send_response(request['req_id'], selected_message)
        

if __name__ == "__main__":
    main()