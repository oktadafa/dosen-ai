import random
import string

def random_string():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=10))

