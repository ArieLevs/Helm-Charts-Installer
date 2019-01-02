
import re


def remove_ansi_color_from_string(input_string):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', input_string)


main_palette = [
    ('body', 'black', 'light gray', 'standout'),
    ('reverse', 'light gray', 'black'),
    ('header', 'white', 'dark red', 'bold'),
    ('footer', 'white', 'dark green', 'bold'),
    ('important', 'dark blue', 'light gray', ('standout', 'underline')),
    ('editfc', 'white', 'dark blue', 'bold'),
    ('editbx', 'light gray', 'dark blue'),
    ('editcp', 'black', 'light gray', 'standout'),
    ('bright', 'dark gray', 'light gray', ('bold', 'standout')),
    ('buttn', 'black', 'light blue'),
    ('buttnf', 'white', 'dark blue', 'bold'),
    ('errors', 'black', 'dark red'),
]
