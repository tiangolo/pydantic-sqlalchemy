from dataclasses import dataclass
from typing import List, Union


def trim_margin_inner(line_str: str):
    splitted = line_str.split('|')
    if len(splitted) == 1:
        return splitted[0]
    return '|'.join(splitted[1:])


def trim_margin(
        text: str,
        indent_level: int,
        indent_chars: str,
):
    lines = text.split('\n')
    splitted_by_sep = [
        f'{indent_chars * indent_level}{trim_margin_inner(line)}'
        for line in lines
    ]
    return '\n'.join(splitted_by_sep)

@dataclass
class TrimIndent:
    value: List[Union['TrimIndent', str]]

    def render(self,
               indent_level: int = 0,
               indent_chars: str = '    '):
        render_result = [
            item.render(
                indent_level=indent_level+1,
                indent_chars=indent_chars,
            ) if isinstance(item, TrimIndent)
            else trim_margin(item, indent_level, indent_chars)
            for item in self.value
        ]
        return '\n'.join(render_result)


if __name__ == '__main__':
    test = TrimIndent([
        f"""
        |class HelloWorld(BaseModel):
        |    class Config:
        |        orm_mode = True
        """,

    ])

    print(test.render(0))