#!/Library/Frameworks/Python.framework/Versions/3.8/bin/python3

import json
import operator
import requests
import os
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def download_data():
    # download .json from city of Toronto
    url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/download_resource/e5bf35bc-e681-43da-b2ce-0242d00922ad?format=json"
    r = requests.get(url)
    return r.json()


def load_data(filename):
    # Loads the contents of local file as a JSON file - not needed w/ download.
    path = os.getcwd()
    with open(path + filename) as json_file:
        data = json.load(json_file)
    return data


def process_data(data):
    postal_code = {}
    totals = {}
    for item in data:
        # postal_code returns all active cases by postal code
        if item["FSA"] is None:
            break
        if item["FSA"] not in postal_code.keys():
            postal_code[item["FSA"]] = 0
            if item["Outcome"] == "ACTIVE":
                postal_code[item["FSA"]] += 1
        else:
            if item["Outcome"] == "ACTIVE":
                postal_code[item["FSA"]] += 1
        # totals returns total cases by postal code
        if item["FSA"] not in totals.keys():
            totals[item["FSA"]] = 1
        else:
            totals[item["FSA"]] += 1
    return postal_code, totals


def dict_to_table(data):
    # turns the dictionary data into a list of lists.
    table_data = []
    for key, value in data.items():
        temp_list = []
        temp_list.append(key)
        temp_list.append(value)
        table_data.append(temp_list)
    return table_data


def generate_report(filename, title, table_data):
    path = os.getcwd()
    print(path)
    styles = getSampleStyleSheet()
    report = SimpleDocTemplate(path + "/" + filename)
    report_title = Paragraph(title, styles["h1"])
    table_style = [('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')]
    report_table = Table(data=table_data, style=table_style, hAlign="LEFT")
    empty_line = Spacer(1, 20)
    report.build([report_title, empty_line, report_table])


if __name__ == "__main__":
    # downloads data, processes and outputs dictionaries
    data = download_data()
    # data = load_data("/COVID19_cases.json")
    postal_code, totals = process_data(data)
    postal_code_table_data = dict_to_table(postal_code)
    totals_table_data = dict_to_table(totals)
    generate_report("active.pdf", "Active Cases", sorted(postal_code.items(), key=operator.itemgetter(1), reverse=True))
    generate_report("total.pdf", "Total Cases", sorted(totals.items(), key=operator.itemgetter(1), reverse=True))
    # print("Active Cases\n" + str(sorted(postal_code.items(), key=operator.itemgetter(1), reverse=True)))
    # print("Total Cases\n" + str(sorted(totals.items(), key=operator.itemgetter(1), reverse=True)))
