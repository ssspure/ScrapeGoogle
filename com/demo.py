import xlsxwriter
import os

# # Create an new Excel file and add a worksheet.
# workbook = xlsxwriter.Workbook('/Users/ssspure/demo.xlsx')
# worksheet = workbook.add_worksheet()
#
# worksheet.write(0, 0, "abc")
# worksheet.write(1, 0, "def")
#
#
# workbook.close()

path = "/Users/ssspure/test/deawd/asdje/dea"

if not os.path.exists(path):
    os.makedirs(path)