

def is_valid_name(text):
    """ Checks if name is valid (only ASCII printable characters, no slashes) """
    return all(32 <= ord(ch) <= 126 and ch != '/' for ch in text)


def nl2br(text):
    return text.replace('\n', '<br>')

