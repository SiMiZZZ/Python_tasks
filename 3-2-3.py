import csv
import datetime
import os
import pathlib
import re
import multiprocessing
from statistics import mean
import concurrent.futures

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

class Vacancy():
    def __init__(self):
        self.name = str()
        self.salary_from = str()
        self.salary_to = str()
        self.salary_currency = str()
        self.area_name = str()
        self.published_at = str()

    def get_ru_salary(self):
        self.currency_to_rub = {
        "AZN": 35.68,
        "BYR": 23.91,
        "EUR": 59.90,
        "GEL": 21.74,
        "KGS": 0.76,
        "KZT": 0.13,
        "RUR": 1,
        "UAH": 1.64,
        "USD": 60.66,
        "UZS": 0.0055,
        }
        return (int(float(self.salary_from)) + int(float(self.salary_to))) / 2 * self.currency_to_rub[
                    self.salary_currency]



class DataSet():
    def __init__(self, file_name):
        self.file_name = file_name
        self.vacancies_objects = []

    @staticmethod
    def csv_reader(file_name):
        empty = False
        vacancies = []
        first_line = []
        with open(file_name, "r", encoding='utf_8_sig') as csv_file:
            reader = csv.reader(csv_file)
            for index, row in enumerate(reader):
                if index == 0:
                    first_line = row
                    quanity = len(first_line)
                else:
                    if DataSet.check_list(row, quanity):
                        vacancie_dict = {}
                        for i, skill in enumerate(first_line):
                            vacancie_dict[skill] = row[i]
                        vacancies.append(vacancie_dict)

        return vacancies

    @staticmethod
    def check_list(non_checked_list, quanity):
        if len(non_checked_list) == quanity and ('' not in non_checked_list):
            return True
        return False

    def clear_list(self, value):
        value = re.sub(r'\<[^>]*\>', '', value)
        return value

    def csv_filer(self, reader, list_naming):
        vacancies = []
        for vacancie in list_naming:
            clear_naming = {}
            for index, skill in enumerate(reader):
                clear_naming[skill] = " ".join(self.clear_list(vacancie[index]).split())
            vacancies.append(clear_naming)
        return vacancies

    @staticmethod
    def set_class_values(data):
        vacancies = []
        for dic in data:
            vacancy = Vacancy()
            for value in dic.items():
                setattr(vacancy, value[0], value[1])
            vacancies.append(vacancy)
        return vacancies


class Statistics():
    def __init__(self, data):

        self.vacancies = data[0]
        self.profession_name = data[1]
        self.suitable_cities = []
        self.share_of_cities = self.make_share_of_cities()
        self.salary_by_years = self.make_salary_by_years()
        self.quantity_by_years = self.make_quantity_by_years()
        self.salary_by_profession = self.make_salary_by_profession()
        self.quantity_by_profession = self.make_quantity_by_profession()
        self.salary_by_cities = self.make_salary_by_sities()

    def make_salary_by_years(self):
        salary_by_years = {}
        for vacancie in self.vacancies:
            vacancie_year = int(datetime.datetime.strptime(vacancie.published_at, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y"))
            if vacancie_year not in salary_by_years.keys():
                salary_by_years[vacancie_year] = []
            salary_by_years[vacancie_year].append(vacancie.get_ru_salary())
        for year in salary_by_years.keys():
            salary_by_years[year] = int(mean(salary_by_years[year]))
        salary_by_years = dict(sorted(salary_by_years.items(), key=lambda x: x[0]))
        return salary_by_years

    def make_quantity_by_years(self):
        quantity_by_years = {}
        for vacancie in self.vacancies:
            vacancie_year = int(datetime.datetime.strptime(vacancie.published_at, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y"))
            if vacancie_year not in quantity_by_years.keys():
                quantity_by_years[vacancie_year] = 0
            quantity_by_years[vacancie_year] += 1
        quantity_by_years = dict(sorted(quantity_by_years.items(), key=lambda x: x[0]))
        return quantity_by_years

    def make_salary_by_profession(self):
        salary_by_years = {}
        for vacancie in self.vacancies:
            if self.profession_name not in vacancie.name:
                continue
            vacancie_year = int(datetime.datetime.strptime(vacancie.published_at, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y"))
            if vacancie_year not in salary_by_years.keys():
                salary_by_years[vacancie_year] = []
            salary_by_years[vacancie_year].append(vacancie.get_ru_salary())
        for year in salary_by_years.keys():
            salary_by_years[year] = int(mean(salary_by_years[year]))
        salary_by_years = dict(sorted(salary_by_years.items(), key=lambda x: x[0]))
        if len(salary_by_years.keys()) == 0:
            salary_by_years[2022] = 0
        return salary_by_years

    def make_quantity_by_profession(self):
        quantity_by_years = {}
        for vacancie in self.vacancies:
            if self.profession_name not in vacancie.name:
                continue
            vacancie_year = int(datetime.datetime.strptime(vacancie.published_at, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y"))
            if vacancie_year not in quantity_by_years.keys():
                quantity_by_years[vacancie_year] = 0
            quantity_by_years[vacancie_year] += 1
        quantity_by_years = dict(sorted(quantity_by_years.items(), key=lambda x: x[0]))
        if len(quantity_by_years.keys()) == 0:
            quantity_by_years[2022] = 0
        return quantity_by_years

    def make_salary_by_sities(self):
        salary_by_cities = {}
        for vacancie in self.vacancies:
            if vacancie.area_name not in self.suitable_cities:
                continue
            vacancie_city = vacancie.area_name
            if vacancie_city not in salary_by_cities.keys():
                salary_by_cities[vacancie_city] = []
            salary_by_cities[vacancie_city].append(vacancie.get_ru_salary())
        for area_name in salary_by_cities.keys():
            salary_by_cities[area_name] = int(mean(salary_by_cities[area_name]))
        salary_by_cities = sorted(salary_by_cities.items(), key=lambda x: x[1], reverse=True)
        salary_by_cities = dict(salary_by_cities[:min(10,len(salary_by_cities))])
        return salary_by_cities

    def make_share_of_cities(self):
        vacancies_quantity = len(self.vacancies)
        share_of_cities = {}
        pop_names= []
        for vacancie in self.vacancies:
            vacancie_city = vacancie.area_name
            if vacancie_city not in share_of_cities.keys():
                share_of_cities[vacancie_city] = 0
            share_of_cities[vacancie_city] += 1
        for area_name in share_of_cities.keys():
            share_of_cities[area_name] = round(share_of_cities[area_name]/vacancies_quantity,4)
            if share_of_cities[area_name]<0.01:
                pop_names.append(area_name)
            else:
                self.suitable_cities.append(area_name)
               # print(area_name, share_of_cities[area_name])
        for a in pop_names:
            share_of_cities.pop(a)
        share_of_cities = sorted(share_of_cities.items(), key=lambda x: x[1], reverse=True)
        share_of_cities = dict(share_of_cities[:min(10,len(share_of_cities))])
        return share_of_cities


class MultipleReader:
    def __init__(self):
        self.file_names = self.get_file_names(r"C:\Users\79823\Desktop\SiMiZZZ\Python_tasks_2.3\CSV_files")
        self.datasets = [(lambda x: DataSet(x))(i) for i in self.file_names]

    def get_file_names(self, folder_name):
        file_names_list = [i[2] for i in os.walk(rf'{folder_name}')][0]
        file_names_list = list(map(lambda x: f"CSV_files/{x}", file_names_list))
        return file_names_list

    def reader(self):
        with concurrent.futures.ProcessPoolExecutor() as pool:
            vacancies = pool.map(DataSet.csv_reader, self.file_names)

        return vacancies


class MultipleStatistics:

    def __init__(self, vacancie_name):
        self.vacancie_name = vacancie_name
        self.share_of_cities = {}
        self.salary_by_years = {}
        self.quantity_by_years = {}
        self.salary_by_profession = {}
        self.quantity_by_profession = {}
        self.salary_by_cities = {}

    def get_statistic(self, vacancies):
        vacancies = list(map(DataSet.set_class_values, vacancies))
        with concurrent.futures.ProcessPoolExecutor() as pool:
            statistics = pool.map(Statistics, tuple(map(lambda x: (x, self.vacancie_name), vacancies)))

        return list(statistics)

    def merge_statistics(self, statistics):
        for instance in statistics:
            year = list(instance.salary_by_years.keys())[0]
            self.salary_by_years[year] = instance.salary_by_years[year]
            self.quantity_by_years[year] = instance.quantity_by_years[year]
            self.salary_by_profession[year] = instance.salary_by_profession[year]
            self.quantity_by_profession[year] = instance.quantity_by_profession[year]
            for city in instance.salary_by_cities.keys():
                if city not in self.salary_by_cities:
                    self.salary_by_cities[city] = instance.salary_by_cities[city]
                else:
                    self.salary_by_cities[city] += instance.salary_by_cities[city]

            for city in instance.share_of_cities.keys():
                if city not in self.share_of_cities:
                    self.share_of_cities[city] = instance.share_of_cities[city]
                else:
                    self.share_of_cities[city] += instance.share_of_cities[city]

        for city in self.salary_by_cities.keys():
            self.salary_by_cities[city] = int(self.salary_by_cities[city]/len(statistics))
        for city in self.share_of_cities.keys():
            self.share_of_cities[city] = '{:.3f}'.format(self.share_of_cities[city] / len(statistics))

if __name__ == "__main__":
    vacancie_name = input("Введите название вакансии: ")
    multiple_reader = MultipleReader()
    vacancies = multiple_reader.reader()
    multiple_statistics = MultipleStatistics(vacancie_name)
    statistics = multiple_statistics.get_statistic(vacancies)
    multiple_statistics.merge_statistics(statistics)

    print(f"Динамика уровня зарплат по годам: {multiple_statistics.salary_by_years}")
    print(f"Динамика количества вакансий по годам: {multiple_statistics.quantity_by_years}")
    print(f"Динамика уровня зарплат по годам для выбранной профессии: {multiple_statistics.salary_by_profession}")
    print(f"Динамика количества вакансий по годам для выбранной профессии: {multiple_statistics.quantity_by_profession}")
    print(f"Уровень зарплат по городам (в порядке убывания): {multiple_statistics.salary_by_cities}")
    print(f"Доля вакансий по городам (в порядке убывания: {multiple_statistics.share_of_cities}")
    # folder_name = input("Введите название папки: ")
    # profesion_name = input("Введите название профессии: ")



