import os
import re
import requests
import magic
import pdfplumber
import docx
from app import app
from fpdf import FPDF

def dictionary_request(term):
    definition = None
    partofspeech = None

    baseurl = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"

    json = requests.get(baseurl + term).json()

    if "title" in json:
        definition = ""
    else:
        partofspeech = json[0]['meanings'][0]['partOfSpeech']
        definition = "(" + partofspeech + ") " + json[0]['meanings'][0]['definitions'][0]['definition']

    return definition

def wikipedia_request(term):
    definition = None

    baseurl = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exsentences=2&explaintext&redirects=1&titles="

    json = requests.get(baseurl + term).json()
    json = json['query']['pages']

    if "-1" in json:
        definition = ""
    else:
        id = str(list(json)[0])
        json = json[id]
        definition = json['extract']

    return definition

def filetype(filename):

    if ".pdf" in filename[-5:]:
        return "pdf"
    elif ".docx" in filename[-5:]:
        return "docx"
    elif ".txt" in filename[-5:]:
        return "txt"
    else:
        fileidentity = ','.split(magic.from_buffer(os.path.join(app.config['UPLOAD_FOLDER'], filename)).lower())[0]

        if ("pdf document" in fileidentity):
            return "pdf"
        elif ("microsoft word" in fileidentity):
            return "docx"
        elif ("ascii text" in fileidentity):
            return "txt"

    return None

def filecontent(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    file_type = filetype(filename)

    content = ''

    if (file_type == "pdf"):
        pdf = pdfplumber.open(filepath)
        for page in pdf.pages:
            content += page.extract_text()
    elif (file_type == "txt"):
        content = open(filepath, "r", encoding='utf-8-sig').read()
    elif (file_type == "docx"):
        doc = docx.Document(filepath)
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"

    return content

def format_dictionary(dictionary):
    formatted = []

    for term in dictionary:
        section = term + "\n" + dictionary[term]
        formatted.append(section)
    return "\n-\n".join(formatted)

def save_file(formatted):
    pdf = FPDF(unit = "in", format = "letter")
    pdf.set_margins(left= 1, top= 1, right= 1)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 0.25, txt = formatted, align = "L")
    pdf.output(os.path.join(app.config['DOWNLOAD_FOLDER'], "definitions.pdf"))

def generate_definitions(def_source, omit_term, separator, filename):

    file_text = filecontent(filename)

    separator = separator[-2]

    terms = []

    if separator == 'n':
        terms = file_text.split("\n")
    else:
        terms = file_text.split(separator)

    for term in terms:
        term = term.strip()
        if term == "":
            terms.remove(term)

    dictionary = dict.fromkeys(terms)

    for term in terms:
        definition = ""
        if def_source == "Dictionary":
            definition = dictionary_request(term).strip()
            if definition == "":
                definition = re.sub(r'\([^)]*\)', '', wikipedia_request(term).strip())

        elif def_source == "Wikipedia":
            definition = re.sub(r'\([^)]*\)', '', wikipedia_request(term).strip())
            if definition == "":
                definition = dictionary_request(term).strip()

        if omit_term:
            ignore_case = re.compile(re.escape(term), re.IGNORECASE)
            definition = ignore_case.sub("_____", definition)

        dictionary[term] = definition

    formatted = format_dictionary(dictionary)

    save_file(formatted)