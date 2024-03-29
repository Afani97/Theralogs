from datetime import datetime

from django.template.loader import render_to_string
from weasyprint import HTML


def render_to_pdf(context_dict={}):
    html_string = render_to_string("pdf/transcript.html", context_dict)
    html = HTML(string=html_string)
    result = html.write_pdf()
    return result


def format_transcript_utterances(utterances):
    output = []
    if len(utterances) > 1:
        for turn in utterances:
            output.append(
                {"speaker": f"speaker_{turn['speaker']}", "transcript": turn["text"]}
            )
    return output


def read_file(filename, chunk_size=5242880):
    with open(filename, "rb") as _file:
        while True:
            data = _file.read(chunk_size)
            if not data:
                break
            yield data


def format_date(month, year):
    date_str = f"01/{month}/{year}"
    format_str = "%d/%m/%Y"
    date = datetime.strptime(date_str, format_str).date()
    return date
