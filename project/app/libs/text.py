import re

def string_to_path(text: str) -> str:
    """Function to clean string for path creating

    Args:
        path_string (str): string to convert

    Returns:
        string: cleaned from unallowed symbols string
    """

    return re.sub(r'[^a-zA-Z0-9_]', '_', text)


def clean_text(text, subset: str = 'all') -> str:
    """
    Clean the input text using specified regex patterns subset.

    Parameters:
    - text (str): The input text to be cleaned.
    - subset (str, optional): The name of the regex patterns subset to use. Defaults to 'all'.

    Returns:
    - str: The cleaned text.
    """

    regex_patterns = {
        'for_soc':          {'re': re.compile(re.escape('<{ Для сотрудников SOC') + r'.*?' + r'\}\>', re.DOTALL), 'sub': ''},
        'comments':         {'re': re.compile(r'^\>.*?$', re.MULTILINE), 'sub': ''},
        'extra_newlines':   {'re': re.compile(r'\n{3,}'), 'sub': '\n\n'},
        'empty_lines':      {'re': re.compile(r'^\s*\n?', re.MULTILINE), 'sub': ''},
    }

    regex_subsets = {
        'all': regex_patterns,
        'light': {key: value for key, value in regex_patterns.items() if key in ['comments']}
    }

    if subset in regex_subsets.keys():
        subset_dict = regex_subsets[subset]
    elif subset in regex_patterns.keys():
        subset_dict = regex_patterns[subset]
    else:
        raise KeyError(f'There is no subset of regex with name {subset}')

    cleaned_text = text
    for pattern_name, pattern_val in subset_dict.items():
        if callable(pattern_val['sub']):
            cleaned_text = pattern_val['sub'](cleaned_text)
        else:
            cleaned_text = re.sub(pattern_val['re'], pattern_val['sub'], cleaned_text)

    return cleaned_text
