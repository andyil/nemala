import xlsxwriter
import tempfile

class Excel:

    def __init__(self, column_names, rows):
        self.column_names = column_names
        self.rows = rows
        self.name = "hello.xlsx"

    def do(self):
        workbook = xlsxwriter.Workbook(self.name)
        worksheet = workbook.add_worksheet()

        columns = []
        for c in ['', 'A', 'B']:
            columns += ['%s%s' % (c, chr(i)) for i in range(ord('A'), ord('Z')+1)]

        for i, name in enumerate(self.column_names):
            column = columns[i]
            worksheet.write('%s1' % column, name)

        for rownumber, row in enumerate(self.rows):
            line = rownumber+2
            for i, r in enumerate(row):
                column = columns[i]
                worksheet.write("%s%s" % (column, line), "%s" % r)


        workbook.close()

    def get(self):
        self.do()
        bytes = open(self.name, "rb").read()
        from os import unlink
        unlink(self.name)
        return bytes

if __name__ == "__main__":
    rows = []
    for ii in range(0, 10):
        row = []
        for jj in range(0, 5):
            row.append(jj)
        rows.append(row)
    e = Excel(["בית המשפט", "תוצאה", "a", "b", "c"], rows)
    e.do()
    exit(0)

    output = io.BytesIO()

    # Even though the final file will be in memory the module uses temp
    # files during assembly for efficiency. To avoid this on servers that
    # don't allow temp files, for example the Google APP Engine, set the
    # 'in_memory' constructor option to True:
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Write some test data.
    worksheet.write(0, 0, 'Hello, world!')

    # Close the workbook before streaming the data.
    workbook.close()

    # Rewind the buffer.
    output.seek(0)

    # Construct a server response.
    self.send_response(200)
    self.send_header('Content-Disposition', 'attachment; filename=test.xlsx')
    self.send_header('Content-type',
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    self.end_headers()
    self.wfile.write(output.read())