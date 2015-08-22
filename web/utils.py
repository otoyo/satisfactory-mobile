class CSVDumper:

    @classmethod
    def dump(self, matrix, encoding='sjis'):
        rows = []
        for row in matrix:
            fields = []
            for field in row:
                if field is None:
                    fields.append('')
                elif str(field).isdigit():
                    fields.append(str(field))
                else:
                    fields.append('"{0}"'.format(str(field).replace('"', '""')))
            rows.append(','.join(fields))
        return '\n'.join(rows).encode(encoding, 'ignore')
