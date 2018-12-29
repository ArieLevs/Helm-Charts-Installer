
import re


def remove_ansi_color_from_string(input_string):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', input_string)
