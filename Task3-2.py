import csv
import datetime


def csv_reader(file_name):
    years_chunks = {}
    with open(file_name, "r", encoding='utf_8_sig') as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader)
        for index, row in enumerate(reader):
            year = int(datetime.datetime.strptime(row[-1], "%Y-%m-%dT%H:%M:%S%z").strftime("%Y"))
            if year in years_chunks:
                years_chunks[year].append(row)
            else:
                years_chunks[year] = [row]
    return headers, years_chunks

def csv_writer(headers, years_chunks):
    for year in years_chunks.keys():
        with open(f"CSV_files/{year}.csv", 'w', encoding='utf_8_sig', newline='') as csv_file:
            writer = csv.writer(csv_file, dialect="excel", delimiter=',')
            writer.writerow(headers)
            writer.writerows(years_chunks[year])

file_name = input("Введите имя файла: ")
headers, years_chunks = csv_reader(file_name)
csv_writer(headers, years_chunks)


