import argparse
import os
import csv
from collections import defaultdict
from tabulate import tabulate
#______________________________________________________________________

def main():
    parser = argparse.ArgumentParser(description='Обработка CSV файлов и генерация отчета указанного типа')

    # Обязательные аргументы
    parser.add_argument(
        '--files',
        nargs='+',
        required=True,
        help='Список CSV файлов для обработки (через пробел)'
    )

    parser.add_argument(
        '--report',
        required=True,
        choices=['performance'],
        help='Тип отчета: performance - производительность'
    )

    args = parser.parse_args()

    # Проверка существования файлов
    for file_path in args.files:
        if not os.path.exists(file_path):
            parser.error(f"Файл {file_path} не найден!")

    # Обработка файлов
    process_files(args.files, args.report)
#______________________________________________________________________

def process_files(file_list, report_type):
    all_data = []

    # Чтение всех файлов
    for file_path in file_list:
        try:
            all_data = all_data + read_csv_file(file_path)
        except Exception as e:
            print(f"  Ошибка чтения {file_path}: {e}")

    # Генерация отчета в зависимости от типа
    generate_report_by_type(all_data, report_type)
#______________________________________________________________________

def generate_report_by_type(data, report_type):
    if report_type == 'performance':
        generate_performance_report(data)
#______________________________________________________________________

def read_csv_file(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        items = csv.DictReader(file)
        for row in items:
            if row:
                data.append(row)
    return data
#______________________________________________________________________

def generate_performance_report(data):
    position = 'position'
    performance = 'performance'

    groupped = group_by(
        data,
        key_func=lambda item: item[position],
        value_func=lambda item: float(item[performance])
    )

    output = []
    for key, value in groupped.items():
        output.append({
            position: key,
            performance: (sum(value) / len(value)),
        })

    row_numbers = range(1, len(output) + 1)
    output_sorted = sorted(output, key=lambda x: x[performance], reverse=True)
    print(tabulate(
        output_sorted,
        headers='keys',
        tablefmt='simple',
        showindex=row_numbers,
        floatfmt='.2f'
    ))

    return output_sorted
#______________________________________________________________________

def group_by(iterable, key_func, value_func):
   result = defaultdict(list)
   for item in iterable:
       result[key_func(item)].append(value_func(item))
   return result

if __name__ == "__main__":
    main()