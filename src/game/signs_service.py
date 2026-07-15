import json

# constants
REQUEST_FILE = "signs_request.json"
RESPONSE_FILE = "signs_response.json"
DB_FILE = "signs_db.json"

MAX_LINE_LENGTH = 19

# variables
old_request = 0

# functions
def get_sign(all_signs,coords):
    print(coords)
    for sign in all_signs:
        if ((sign['x'] == coords['x']) and (sign['y'] == coords['y'])):
            requested_sign = sign
            break
    if (not requested_sign):
        return []
    
    text = requested_sign['text'].split()
    lines = []
    while len(text) > 0:
        new_line = ""
        while (len(text) > 0) and ((len(new_line) + len(text[0])) < MAX_LINE_LENGTH):
            new_line = new_line + text.pop(0) + " "
        lines.append(new_line)
    
    return lines

def send_response(req_id,sign_lines):
    response = {
        'req_id': req_id,
        'lines': sign_lines
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
                    sign_lines = get_sign(db, request)
                    send_response(request['req_id'], sign_lines)
        

if __name__ == "__main__":
    main()