#!/Library/Frameworks/Python.framework/Versions/3.8/bin/python3

import json
import operator
import requests
import os
import sys
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def download_data():
    # download .json from city of Toronto
    url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/download_resource/e5bf35bc-e681-43da-b2ce-0242d00922ad?format=json"
    r = requests.get(url)
    return r.json()


def save_data(data):
    # Saves copy of website data locally.
    path = os.getcwd()
    with open(path + '/currentdata.json', 'w') as outfile:
        json.dump(data, outfile)


def load_data(filename):
    # Loads the contents of local file as a JSON file.
    path = os.getcwd()
    with open(path + filename) as json_file:
        data = json.load(json_file)
    return data


def process_data(data):
    active_cases = {}
    total_cases = {}
    for item in data:
        # postal_code returns all active cases by postal code
        if item["FSA"] not in active_cases.keys():
            active_cases[item["FSA"]] = 0
            if item["Outcome"] == "ACTIVE":
                active_cases[item["FSA"]] += 1
        else:
            if item["Outcome"] == "ACTIVE":
                active_cases[item["FSA"]] += 1
        # totals returns total cases by postal code
        if item["FSA"] not in total_cases.keys():
            total_cases[item["FSA"]] = 1
        else:
            total_cases[item["FSA"]] += 1
    try:
        active_cases["Unknown"] = active_cases[None]
        active_cases.pop(None)
    except Exception:
        pass
    try:
        total_cases["Unknown"] = total_cases[None]
        total_cases.pop(None)
    except Exception:
        pass
    return active_cases, total_cases


def changed_data(newdata, olddata):
    changes = {}
    for newkey, newvalue in newdata.items():
        for oldkey, oldvalue in olddata.items():
            if newkey == oldkey:
                changes[newkey] = newvalue - oldvalue
                break
    return changes


def generate_report(filename, title, table_data):
    path = os.getcwd()
    styles = getSampleStyleSheet()
    report = SimpleDocTemplate(path + filename)
    report_title = Paragraph(title, styles["h1"])
    table_style = [('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')]
    report_table = Table(data=table_data, style=table_style, hAlign="LEFT")
    empty_line = Spacer(1, 20)
    report.build([report_title, empty_line, report_table])
    print(filename.strip("/") + " saved.")


def verify_changes(changes):
    check = False
    for value in changes.values():
        if value != 0:
            check = True
    if check is False:
        print("Database not updated.")
        sys.exit(0)


def active(active):
    total_active = 0
    population = 2956024
    for value in active.values():
        total_active += value
    total_per_pop = total_active/population*100000
    print("Active Cases: " + str(total_active))
    print("Total Cases per 100,000: {:.2f}".format(total_per_pop))


def main():
    # downloads data, processes and outputs dictionaries
    new_data = download_data()
    try:
        old_data = load_data('/currentdata.json')
        changed = True
    except Exception:
        print("No old data.")
        changed = False
    active_cases, totals_cases = process_data(new_data)
    if changed is True:
        old_active, old_totals = process_data(old_data)
        changes = changed_data(active_cases, old_active)
        verify_changes(changes)
        generate_report("/changes.pdf", "Changes Since Last Report", sorted(changes.items(), key=operator.itemgetter(1), reverse=True))
    active(active_cases)
    save_data(new_data)
    generate_report("/active.pdf", "Active Cases", sorted(active_cases.items(), key=operator.itemgetter(1), reverse=True))
    generate_report("/total.pdf", "Total Cases", sorted(totals_cases.items(), key=operator.itemgetter(1), reverse=True))
    sys.exit(0)


if __name__ == "__main__":
    main()
