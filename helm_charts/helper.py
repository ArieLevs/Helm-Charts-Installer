
import re


def remove_ansi_color_from_string(input_string):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', input_string)


def is_valid_charts_yaml(content):
    """
    Check if 'content' contains mandatory keys

    :param content: parsed YAML file as list of dictionary of key values
    :return: True if dict contains mandatory values, else False
    """

    # Iterate on each list cell
    for chart_details in content:
        # If one of the keys is missing or, is None
        if not all(chart_details.get(x) is not None
                   and x in chart_details
                   for x in ['chart_name', 'helm_repo_name', 'name_space', 'values_file', 'private_image']):
            return False
        # If one of the keys is not a string
        if not all(type(chart_details.get(x)) is str
                   for x in ['chart_name', 'helm_repo_name', 'name_space', 'values_file']):
            return False
        # If one of the keys is not a boolean
        if not all(type(chart_details.get(x)) is bool
                   for x in ['private_image']):
            return False
    return True


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
