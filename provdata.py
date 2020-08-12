#!/Library/Frameworks/Python.framework/Versions/3.8/bin/python3

import csv
import operator
import requests
import os
import sys


def download_data():
    path = os.getcwd()
    url = "https://data.ontario.ca/dataset/f4112442-bdc8-45d2-be3c-12efae72fb27/resource/455fd63b-603d-4608-8216-7d8647f43350/download/conposcovidloc.csv"
    with open(path + "/currentdata.csv", 'w') as outfile:
        writer = csv.writer(outfile)
        with requests.get(url, stream=True) as r:
            lines = (line.decode('utf-8') for line in r.iter_lines())
            for row in csv.reader(lines):
                writer.writerow(row)


def read_data():
    active_cases = {}
    path = os.getcwd()
    with open (path + "/currentdata.csv") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Reporting_PHU_City"] not in active_cases.keys():
                active_cases[row["Reporting_PHU_City"]] = 0
            if row["Outcome1"].lower().strip() == "not resolved":
                active_cases[row["Reporting_PHU_City"]] += 1
    print(active_cases)
    return active_cases


def active(active_cases):
    casesperpop = {}
    populations = {"Whitby": 135566, "Port Hope": 16753, "Newmarket": 84224,
                   "Mississauga": 828854, "Oakville": 211382, "Owen Sound": 21341,
                   "Point Edward": 2037, "Kingston": 136685, "Thunder Bay": 110172,
                   "Guelph": 135474, "Timmins": 41788, "Toronto": 2930000,
                   "Sudbury": 164926, "Ottawa": 994837, "Hamilton": 579200,
                   "Cornwall": 46589, "Waterloo": 113520, "Barrie": 153356,
                   "London": 404699, "Stratford": 31465, "Kenora": 15096,
                   "Thorold": 18801, "Peterborough": 84230, "Windsor": 233763,
                   "Brantford": 102159, "Belleville": 50720, "Chatham": 105529,
                   "St. Thomas": 38909, "Sault St. Marie": 73368,
                   "New Liskeard": 9920, "North Bay": 51553, "Simcoe": 13992,
                   "Brockville": 21854, "Pembroke": 13882}
    for active_key, active_value in active_cases.items():
        for pop_key, pop_value in populations.items():
            if active_key == pop_key:
                total_per_pop = active_value/pop_value*100000
                casesperpop[active_key] = total_per_pop
    return casesperpop


def printout(casesperpop):
    sorted_dict = {}
    print(casesperpop)
    #for key, value in casesperpop.items():
        #print("{}, total Cases per 100,000: {:.2f}".format(key, value))


def main():
    download_data()
    active_cases = read_data()
    casesperpop = active(active_cases)
    printout(sorted(casesperpop.items(), key=operator.itemgetter(1), reverse=True))


if __name__ == "__main__":
    main()
