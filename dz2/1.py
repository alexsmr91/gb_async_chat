import csv
import re


def get_data():
    headers = ["Изготовитель системы", "Название ОС", "Код продукта", "Тип системы"]
    main_data = [headers]
    for i in range(1, 4):
        main_data.append([])
        with open(f"info_{i}.txt") as f:
            file_data = f.read()
            for k, item in enumerate(headers):
                reg_exp = r"{}:\s*(.*)".format(re.escape(item))
                search = re.search(reg_exp, file_data)
                if search:
                    data = search.group(1).strip()
                else:
                    data = None
                main_data[i].append(data)
    return main_data


def write_to_csv(csv_file):
    data = get_data()
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)


if __name__ == "__main__":
    write_to_csv("report.csv")
