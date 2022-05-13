from typing import List

def trim_margin_inner(line_str: str):
    splitted = line_str.split('|')
    if len(splitted) == 1:
        return splitted[0]
    return '|'.join(splitted[1:])


def trim_margin(text: str):
    lines = text.split('\n')
    splitted_by_sep = [
        trim_margin_inner(line)
        for line in lines
    ]
    return '\n'.join(splitted_by_sep)

def get_template_string(
    imports: List[str]
):
    imports_text = '\n|    '.join([''] + imports)
    return trim_margin(
    f"""

    {imports_text}
    """)

output = get_template_string(
    ['1', '2', '3']
)

if __name__ == '__main__':
    print(output)