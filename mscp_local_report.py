#!/usr/bin/env python3
# description: Point to mSCP Plist Log File to make pretty graph, 
# required: input file and output file
# ./mscp_local_report -p /Library/Preferences/org.BASELINE.audit.plist -o ~/prettyoutput.xlsx

import argparse
from openpyxl import Workbook
from pathlib import Path
import plistlib
from collections import OrderedDict
from openpyxl.chart import (
    PieChart,
    ProjectedPieChart,
    Reference
)
from openpyxl.chart.series import DataPoint

def validate_file(arg):
    if (file := Path(arg)).is_file():
        return file
    else:
        raise FileNotFoundError(arg)

parser = argparse.ArgumentParser()
parser.add_argument('--plist', '-p', type=validate_file, help="Input plist scan", required=True)
parser.add_argument('--output','-o',help="Output file path", required=True)
args = parser.parse_args()
failed = 0
passed = 0
with open(args.plist, 'rb') as fp:
    pl = plistlib.load(fp)
    
sortedpl = OrderedDict(sorted(pl.items()))
data = [["Rule ID", "Result"]]
for rule,result in sortedpl.items():
    if rule == "lastComplianceCheck":
        continue
    for k,v in result.items():
        if v == True:
            failed += 1
        if v == False:
            passed += 1
        entry = [rule,v]
        data.append(entry)
    
entries = len(data)
minrow = len(data)+1
maxrow = len(data)+2
data.append(["failed",failed])
data.append(["passed",passed])

wb = Workbook()
ws = wb.active

for row in data:
    ws.append(row)

pie = PieChart()
labels = Reference(ws, min_col=1, min_row=minrow, max_row=maxrow)
data = Reference(ws, min_col=2, min_row=minrow, max_row=maxrow)
pie.add_data(data)
pie.set_categories(labels)
pie.title = "Compliance Scan Results"

ws.add_chart(pie, "D1")

savefile = str()

if ".xlsx" == args.output[-5:]: 
    savefile= args.output
else:
    savefile = args.output + ".xlsx"
wb.save(savefile)
