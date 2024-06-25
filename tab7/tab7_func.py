import re
import os
import gradio as gr
import codecs
from docx import Document

def replace_special_periods(text):
    text = re.sub(r'\bDr\.', 'Dr<PERIOD>', text)
    text = re.sub(r'\.com\b', '<DOTCOM>', text)
    text = re.sub(r'\.org\b', '<DOTORG>', text)
    return text

def restore_special_periods(text):
    text = text.replace('Dr<PERIOD>', 'Dr.')
    text = text.replace('<DOTCOM>', '.com')
    text.replace('<DOTORG>', '.org')
    return text

def split_segment(segment, start_time, end_time):
    if start_time is None or end_time is None:
        return [(segment, start_time, end_time)]
    sentences = re.split(r'(?<!\.\.\.)\. ', segment)  # 三点リーダーはそのまま残す
    num_sentences = len(sentences)
    times = [(start_time + i * (end_time - start_time) / num_sentences) for i in range(num_sentences + 1)]
    return [(sentences[i], times[i], times[i+1]) for i in range(num_sentences)]

def merge_segments(segments):
    merged_segments = []
    buffer_segment = ""
    buffer_start = None
    buffer_end = None

    for segment, start, end in segments:
        if buffer_segment:
            buffer_segment += " " + segment
            buffer_end = end
            if segment.endswith('.'):
                merged_segments.append((buffer_segment, buffer_start, buffer_end))
                buffer_segment = ""
                buffer_start = None
                buffer_end = None
        else:
            if segment.endswith('.'):
                merged_segments.append((segment, start, end))
            else:
                buffer_segment = segment
                buffer_start = start
                buffer_end = end

    if buffer_segment:
        merged_segments.append((buffer_segment, buffer_start, buffer_end))

    return merged_segments

def process_vtt(lines):
    segments = []
    start_time = None
    end_time = None
    text = ""
    header = lines[0]

    for line in lines[1:]:
        if re.match(r'^\d+$', line.strip()):
            if text:
                text = replace_special_periods(text)
                if start_time is not None and end_time is not None:
                    segments.extend(split_segment(text.strip(), start_time, end_time))
            text = ""
        elif '-->' in line:
            times = line.strip().split(' --> ')
            start_time = convert_time_to_seconds(times[0])
            end_time = convert_time_to_seconds(times[1])
        else:
            text += line.strip() + " "

    if text:
        text = replace_special_periods(text)
        if start_time is not None and end_time is not None:
            segments.extend(split_segment(text.strip(), start_time, end_time))

    merged_segments = merge_segments(segments)

    output = [header]
    segment_number = 0
    for text, start, end in merged_segments:
        text = restore_special_periods(text)
        output.append(f"{segment_number}")
        output.append(convert_seconds_to_time(start, 'vtt') + ' --> ' + convert_seconds_to_time(end, 'vtt'))
        output.append(text)
        segment_number += 1
        output.append("")  # セグメント間の改行を保持

    return '\n'.join(output)

def process_srt(lines):
    segments = []
    start_time = None
    end_time = None
    text = ""
    segment_index = 0

    for line in lines:
        if re.match(r'^\d+$', line.strip()):
            if text:
                text = replace_special_periods(text)
                segments.extend(split_segment(text.strip(), start_time, end_time))
            segment_index = int(line.strip())
            text = ""
        elif '-->' in line:
            times = line.strip().split(' --> ')
            start_time = convert_time_to_seconds(times[0].replace(',', '.'))
            end_time = convert_time_to_seconds(times[1].replace(',', '.'))
        else:
            text += line.strip() + " "

    if text:
        text = replace_special_periods(text)
        segments.extend(split_segment(text.strip(), start_time, end_time))

    merged_segments = merge_segments(segments)

    output = []
    segment_number = 0
    for text, start, end in merged_segments:
        text = restore_special_periods(text)
        output.append(f"{segment_number + 1}\n{convert_seconds_to_time(start).replace('.', ',')} --> {convert_seconds_to_time(end).replace('.', ',')}\n{text}\n")
        segment_number += 1

    return '\n'.join(output)

def convert_time_to_seconds(time_str):
    h, m, s = map(float, time_str.replace(',', '.').split(':'))
    return h * 3600 + m * 60 + s

def convert_seconds_to_time(seconds, format_type='vtt'):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    if format_type == 'vtt':
        return f"{h:02}:{m:02}:{s:06.3f}".replace(',', '.')
    else:
        return f"{h:02}:{m:02}:{s:06.3f}".replace('.', ',')



def process_file(input_file):
    if input_file is None:
        return None, None

    with open(input_file, 'r') as file:
        lines = file.readlines()

    _, file_extension = os.path.splitext(input_file)

    if file_extension.lower() == '.vtt':
        output = process_vtt(lines)
        output_file = os.path.splitext(input_file)[0] + '_edited.vtt'
    elif file_extension.lower() == '.srt':
        output = process_srt(lines)
        output_file = os.path.splitext(input_file)[0] + '_edited.srt'
    else:
        raise ValueError('Unsupported file format')

    with open(output_file, 'w') as file:
        file.write(output)

    # Add the output to a .docx file
    doc = Document()
    doc.add_paragraph(output)
    basename = os.path.splitext(input_file)[0]
    docx_file = basename + '_en_edited.docx'
    doc.save(docx_file)

    output_html = f"""<pre style="white-space: pre-wrap; overflow-y: auto; height: 500px; word-wrap: break-word; padding: 10px; font-family: inherit; font-size: inherit;">{output}</pre>"""

    return output_html, [output_file, docx_file]



def vtt_translate(input_file, translated_content):
    ja_file_name, file_extension = os.path.splitext(input_file)
    output_ja_file_path = ja_file_name + "_edited_ja" + file_extension

    with codecs.open(output_ja_file_path, 'w', 'utf-8') as f:
        f.write(translated_content)

    return output_ja_file_path




