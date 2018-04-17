import os
import time
import datetime
import openpyxl
from openpyxl.cell.cell import get_column_letter

def writeExcel(data):
    filename = r'评选结果%s.xlsx' % time.mktime(datetime.datetime.now().timetuple())
    print(os.getcwd())
    workbook = openpyxl.Workbook()

    sheet = workbook.active

    for r in data:
        sheet.append(r)
    workbook.save(os.getcwd() + '/files/' + filename)
    path = os.path.abspath(filename)


    return filename


