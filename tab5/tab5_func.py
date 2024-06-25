import gradio as gr
import docx
from docx import Document
import tempfile
import os
import zipfile
import torch
import re

def convert_docx_to_srttxt(docx_files):
    output_files = []
    if docx_files==None:
        return []
    for docx_file in docx_files:
        filename = os.path.basename(docx_file.name)
        base_name, ext = os.path.splitext(filename)
        
        # Check the suffix of the basename to determine output type
        if base_name.endswith('_srt'):
            output_filename = base_name.replace('_srt', '_ja.srt')
        elif base_name.endswith('_txtnr'):
            output_filename = base_name.replace('_txtnr', '_NR_ja.txt')
        elif base_name.endswith('_txtr'):
            output_filename = base_name.replace('_txtr', '_R_ja.txt')
        else:
            continue  # Skip unknown patterns
        
        doc = Document(docx_file)
        content = "\n".join([para.text for para in doc.paragraphs])
        
        output_filepath = os.path.join(tempfile.gettempdir(), output_filename)
        with open(output_filepath, 'w', encoding='utf-8') as output_file:
            output_file.write(content)
        
        output_files.append(output_filepath)

    zip_filename = os.path.join(tempfile.gettempdir(), "converted_files.zip")
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in output_files:
            zipf.write(file, os.path.basename(file))
    
    output_files.append(zip_filename)
    
    return output_files



def clear_inputs():
    return None, None

def process_doc_files(files):
    output_files = []
    if files==None:
        return []
    for file in files:
        filename = os.path.basename(file.name)
        match = re.match(r"(.+?)(_NR\.txt|_R\.txt|\.srt)$", filename)
        if not match:
            continue  # skip files with unknown extensions
        
        basename, ext = match.groups()
        if ext == ".srt":
            doc_filename = f"{basename}_srt.docx"
        elif ext == "_NR.txt":
            doc_filename = f"{basename}_txtnr.docx"
        elif ext == "_R.txt":
            doc_filename = f"{basename}_txtr.docx"

        doc = Document()
        with open(file.name, 'r', encoding='utf-8') as f:
            for line in f:
                doc.add_paragraph(line)
        doc.save(doc_filename)
        output_files.append(doc_filename)
    
    if len(output_files)>1:
        zip_filename = "converted_files.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for file in output_files:
                    zipf.write(file)
        output_files.append(zip_filename)
    return output_files

def clear_both():
    return None, None

