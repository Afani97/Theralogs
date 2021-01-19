from io import BytesIO
from django.template.loader import get_template, render_to_string
from weasyprint import HTML

from xhtml2pdf import pisa


def render_to_pdf(context_dict={}):
    html_string = render_to_string("pdf/transcript.html", context_dict)
    html = HTML(string=html_string)
    result = html.write_pdf()
    return result


def format_transcript(json):
    segments = json["results"]["speaker_labels"]["segments"]
    items = json["results"]["items"]
    output = []
    for seg in segments:
        speaker = seg["speaker_label"]
        start_time = float(seg["start_time"])
        end_time = float(seg["end_time"])
        word = ""
        for item in items:
            if item["type"] == "punctuation" and word != "":
                word += item["alternatives"][0]["content"]
            if "start_time" in item:
                if float(item["start_time"]) >= end_time:
                    break
                if (
                    float(item["start_time"]) >= start_time
                    and float(item["end_time"]) <= end_time
                ):
                    word += f" {item['alternatives'][0]['content']}"
        output.append({"speaker": speaker, "transcript": word.lstrip()})

    current_speaker = output[0]["speaker"]
    format_output = [output[0]]
    for index, item in enumerate(output, start=1):
        if item["speaker"] == current_speaker:
            format_output[len(format_output) - 1][
                "transcript"
            ] += f" {item['transcript']}"
        else:
            format_output.append(item)
        current_speaker = item["speaker"]
    return format_output
