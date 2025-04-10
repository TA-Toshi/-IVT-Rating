import numpy as np
import yadisk
import pandas as pd
from io import BytesIO

# Настройки
OAUTH_TOKEN = 'y0__xD5u5uzBhiP2jYgqtfH3BJPdoNuBfWhA76z5-DYzuauTa1Ngw'
FILE_PATH_IVT = 'Загрузки/Текущая успеваемость 1 курс/ИВТ журнал оценок.xlsx'  # Например, 'Рабочие/данные.xlsx'
FILE_PATH_IT = 'Загрузки/Текущая успеваемость 1 курс/ИТ журнал оценок.xlsx'
FILE_PATH_PIE = 'Загрузки/Текущая успеваемость 1 курс/ПИЭжурнал оценок.xlsx'

y = yadisk.YaDisk(token=OAUTH_TOKEN)


def read_excel_from_yadisk(file_path):
    # Скачиваем файл в память
    file_bytes = BytesIO()
    y.download(file_path, file_bytes)
    file_bytes.seek(0)

    # Читаем Excel файл
    return pd.ExcelFile(file_bytes)


# Использование

def get_df(file_path):
    try:
        excel_data = read_excel_from_yadisk(file_path)

        all_sheets = excel_data.parse(skiprows=2, sheet_name=None)
        combined_df = pd.concat(all_sheets.values(), ignore_index=True)
        combined_df = combined_df.drop(columns=["№"])
        combined_df = combined_df.dropna(subset=["Студенч. номер"])
        combined_df["Студенч. номер"] = combined_df["Студенч. номер"].apply(lambda x: f"{str(x)[:7]}")

        return combined_df
    except Exception as e:
        return f"Ошибка: {e}"


# print(get_df(FILE_PATH_PIE))


def get_by_stud_id(stud_id, file_path):
    df = get_df(file_path)
    if df["Студенч. номер"].isin([stud_id]).any():
        row = df.loc[df["Студенч. номер"] == stud_id].iloc[0]
        return row
    return "Нет совпадений"


def format_student_data(row):
    # Основная информация
    response = [
        f"📊 <b>Успеваемость студента</b>",
        f"<b>Номер:</b> {row['Студенч. номер']}",
        "",
        "<b>Результаты:</b>"
    ]

    # Обрабатываем предметы
    for subject, grade in row.items():
        if subject == "Студенч. номер" or subject == "Примечание":
            continue
        if str(grade).strip().lower() != "nan":
            grade_str = ("✅ зачёт" if str(grade).strip().lower() == "зач"
                         else "❌ незачёт" if str(grade).strip().lower() == "незач/"
            else "❌ неявка" if str(grade).strip().lower() == "неяв/"
            else "🔴 2" if str(grade).strip() == "2/"
            else f"🟢 {grade}")
            response.append(f"▪ <i>{subject}:</i> {grade_str}")

    return "\n".join(response)

# print(get_by_stud_id("1036399", FILE_PATH_PIE))
