import numpy as np
import yadisk
import pandas as pd
from io import BytesIO

import os
from dotenv import load_dotenv, find_dotenv

from config import FILE_PATH_ALL

load_dotenv(find_dotenv())
y = yadisk.YaDisk(token=os.getenv("OAUTH_TOKEN"))


def read_excel_from_yadisk(file_path):
    # Скачиваем файл в память
    file_bytes = BytesIO()
    y.download(file_path, file_bytes)
    file_bytes.seek(0)

    # Читаем Excel файл
    return pd.ExcelFile(file_bytes, engine='openpyxl')


# Использование

def get_df(file_path):
    try:
        excel_data = read_excel_from_yadisk(file_path)

        all_sheets = excel_data.parse(sheet_name=None)
        # combined_df = combined_df.drop(columns=combined_df.filter(like="№").columns)
        #
        # fio_index = combined_df.columns.get_loc("ФИО студента")
        # combined_df = combined_df.drop(columns=combined_df.columns[fio_index:fio_index + 3])
        #
        # combined_df = combined_df.drop(columns="Основа обучения")
        # combined_df = combined_df.dropna(subset=["Студенч. номер"])
        # combined_df["Студенч. номер"] = combined_df["Студенч. номер"].apply(lambda x: f"{str(x)[:7]}")

        # Создаем пустой DataFrame для объединенных данных
        # Создаем пустой DataFrame для объединенных данных
        # Создаем пустой DataFrame для объединенных данных
        # Создаем пустой DataFrame для объединенных данных
        combined_df = pd.DataFrame()

        for sheet_name, df in all_sheets.items():

            # Создаем копию для работы
            df_filled = df.copy()

            # Обрабатываем объединенные ячейки
            for col in df_filled.columns:
                if len(df_filled) > 1 and not pd.isna(df_filled[col].iloc[0]) and pd.isna(df_filled[col].iloc[1]):
                    df_filled.loc[df_filled.index[1], col] = df_filled[col].iloc[0]
                if len(df_filled) > 2 and not pd.isna(df_filled[col].iloc[1]) and pd.isna(df_filled[col].iloc[2]):
                    df_filled.loc[df_filled.index[2], col] = df_filled[col].iloc[1]

            # Ищем строку с "№ п/п"
            header_row_index = None
            for i in range(min(4, len(df_filled))):
                cell_value = str(df_filled.iloc[i, 0])
                if "№ п/п" in cell_value or "п/п" in cell_value:
                    header_row_index = i
                    break

            if header_row_index is not None:
                try:
                    # Создаем корректный DataFrame с заголовками
                    df_corrected = df_filled.iloc[header_row_index:].copy()

                    # Получаем заголовки и обрабатываем дубликаты
                    raw_columns = df_corrected.iloc[0].astype(str).tolist()
                    new_columns = []
                    seen_columns = {}

                    for i, col in enumerate(raw_columns):
                        if col in seen_columns:
                            # Если столбец уже встречался, добавляем суффикс
                            seen_columns[col] += 1
                            new_col_name = f"{col}_{seen_columns[col]}"
                        else:
                            seen_columns[col] = 1
                            new_col_name = col
                        new_columns.append(new_col_name)

                    # Устанавливаем уникальные заголовки
                    df_corrected.columns = new_columns
                    df_corrected = df_corrected[1:]  # удаляем строку заголовков
                    df_corrected = df_corrected.reset_index(drop=True)
                    df_corrected = df_corrected.dropna(how='all')  # удаляем пустые строки

                    # ОБЪЕДИНЕНИЕ с добавлением отсутствующих столбцов
                    if combined_df.empty:
                        combined_df = df_corrected
                    else:
                        # Добавляем отсутствующие столбцы в оба DataFrame
                        all_columns = set(combined_df.columns) | set(df_corrected.columns)

                        for col in all_columns:
                            if col not in combined_df.columns:
                                combined_df[col] = None
                            if col not in df_corrected.columns:
                                df_corrected[col] = None

                        # Теперь объединяем
                        combined_df = pd.concat([combined_df, df_corrected], ignore_index=True)

                except Exception as e:
                    print(f"❌ Ошибка при обработке листа '{sheet_name}': {e}")
                    continue
            else:
                print(f"⚠️ Лист '{sheet_name}' - '№ п/п' не найден, лист пропущен")

        # Выводим финальный результат
        combined_df = combined_df.drop(columns=combined_df.filter(like="№").columns)
        fio_index = combined_df.columns.get_loc("ФИО студента")
        combined_df = combined_df.drop(columns=combined_df.columns[fio_index:fio_index + 3])

        combined_df = combined_df.drop(columns="Основа обучения")
        combined_df = combined_df.dropna(subset=["Студенч. номер"])
        combined_df["Студенч. номер"] = combined_df["Студенч. номер"].apply(lambda x: f"{str(x)[:7]}")
        return combined_df
    except Exception as e:
        return f"Ошибка: {e}"


# print(get_df(FILE_PATH_ALL))


def get_by_stud_id(stud_id):
    paths = [FILE_PATH_ALL]
    for file_path in paths:
        df = get_df(file_path)
        if df["Студенч. номер"].isin([stud_id]).any():
            row = df.loc[df["Студенч. номер"] == stud_id].iloc[0]
            return row
    return False


# print(get_by_stud_id("1036512"))


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
        if str(grade).strip().lower() != "none" and str(grade).strip().lower() != "nan":
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
