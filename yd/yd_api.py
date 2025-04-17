import numpy as np
import yadisk
import pandas as pd
from io import BytesIO

import config


y = yadisk.YaDisk(token=config.OAUTH_TOKEN)


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
            response.append(f" - <i>{subject}:</i> {grade_str}")

    return "\n".join(response)


# print(get_by_stud_id("1036399", FILE_PATH_PIE))


def find_diff_cells(df1, df2):
    # Проверка на совпадение размеров, индексов и столбцов
    if df1.shape != df2.shape:
        raise ValueError("DataFrames must have the same shape")
    if not df1.index.equals(df2.index):
        raise ValueError("Indices do not match")
    if not df1.columns.equals(df2.columns):
        raise ValueError("Columns do not match")

    # Создание маски различий с учётом NaN
    mask = (df1 != df2) & ~(df1.isna() & df2.isna())

    # Получение индексов строк и столбцов
    rows, cols = np.where(mask)

    # Формирование списка кортежей (индекс, столбец)
    diff_cells = [(df1.index[row], df1.columns[col]) for row, col in zip(rows, cols)]

    return diff_cells


old_df = None


def check_upd(file_paths):
    global old_df
    new_df = get_df(file_paths[0])
    for i in file_paths[1:]:
        new_df = pd.concat([new_df, get_df(i)], ignore_index=True)
    if old_df is None:
        old_df = new_df
        return None
    if not old_df.equals(new_df):
        upds_list = []
        upds = find_diff_cells(old_df, new_df)
        for upd in upds:
            upds_list.append((upd, new_df[upd[1]][upd[0]], new_df["Студенч. номер"][upd[0]]))
        old_df = new_df
        return upds_list
    return None

