from datetime import datetime
import random
import re
import string


def random_str(length):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))


def is_safe_filename(filename):
    dangerous_patterns = [
        '../', './', '~/', '\\', ':', '|', '*', '?', '"', '<', '>'
    ]
    for pattern in dangerous_patterns:
        if pattern in filename:
            return False
    return True


def handle_name(name, file, dt: datetime):
    name = name.replace('{filepath}', '/'.join(file.parent.path).strip('/'))
    name = name.replace('{filename}', file.name)

    name = name.replace('{timestamp}', str(int(dt.timestamp())))

    def replace_random(match):
        length = int(match.group(1))
        return random_str(length)

    name = re.sub(r'\{random\((\d+)\)\}', replace_random, name)

    return name.strip('/')


def update_source_name(file):
    dir_name = file.storage.dir_name_rule
    file_name = file.storage.file_name_rule

    dt = datetime.now()

    dir_name = handle_name(dir_name, file, dt)
    file_name = handle_name(file_name, file, dt)

    source = f'{dir_name}/{file_name}'.split('/')

    for i in range(len(source)):
        source[i] = source[i].strip().strip('.').strip()

    while '' in source:
        source.remove('')

    file.source = '/'.join(source)
