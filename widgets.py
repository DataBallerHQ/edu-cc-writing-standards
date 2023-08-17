import ipywidgets as w
import textwrap
from genai import STANDARDS

input_theme = w.Text(
    value='',
    placeholder='Enter theme here',
    description='Context theme:',
    disabled=False   
)

input_standard = w.Dropdown(
    options=[(k, v) for k, v in STANDARDS.items()],
    # value=2,
    description='Select standard:',
)

input_answer = w.Textarea(
    value='',
    placeholder='Enter answer here',
    description='Answer:',
    disabled=False
)

def print_section(header, content):
    print(f"\n{header}:")
    print(textwrap.fill(content, width=60))
