current_language_code = 'en-US'  

def set_language_code(new_code):
    global current_language_code
    current_language_code = new_code

def get_language_code():
    return current_language_code
