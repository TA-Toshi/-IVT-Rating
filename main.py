import yadisk
import pandas as pd
from io import BytesIO

# Настройки
OAUTH_TOKEN = 'y0__xD5u5uzBhiP2jYgqtfH3BJPdoNuBfWhA76z5-DYzuauTa1Ngw'
FILE_PATH = 'Загрузки/Текущая успеваемость 1 курс/ИВТ журнал оценок.xlsx'  # Например, 'Рабочие/данные.xlsx'


y = yadisk.YaDisk(token=OAUTH_TOKEN)


def read_excel_from_yadisk(file_path):
    # Скачиваем файл в память
    file_bytes = BytesIO()
    y.download(file_path, file_bytes)
    file_bytes.seek(0)

    # Читаем Excel файл
    return pd.ExcelFile(file_bytes)


# Использование
try:
    excel_data = read_excel_from_yadisk(FILE_PATH)

    # Чтение всех листов
    for sheet_name in excel_data.sheet_names:
        df = excel_data.parse(sheet_name)
        print(f"Лист: {sheet_name}")
        print(df.iat[1, 1])

except Exception as e:
    print(f"Ошибка: {e}")
