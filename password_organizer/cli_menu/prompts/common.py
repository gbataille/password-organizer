from prompt_toolkit.styles import Style


default_style = Style.from_dict({
    'set-cursor-position':  '#FF9D00 bold',
    'separator': '#6C6C6C',
    'question-mark': 'noinherit #5F819D bold',
    'selected': 'noinherit #5F819D bold',
    'pointer': '#FF9D00 bold',
    'instruction': '',
    'answer': '#FF9D00 bold',
    'question': 'bold',
    'disabled': '#555555',
})
