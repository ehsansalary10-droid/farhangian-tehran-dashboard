import openpyxl
import os


EXCEL_FILE = os.path.join(
    "data",
    "داشبورد هوشمند ساختار دانشگاه فرهنگیان استان تهران.xlsx"
)


def read_excel_data():

    if not os.path.exists(EXCEL_FILE):
        return []

    try:

        workbook = openpyxl.load_workbook(
            EXCEL_FILE,
            data_only=True
        )

        sheet = workbook["داده‌های ساختاری"]

        rows = list(
            sheet.iter_rows(
                values_only=True
            )
        )

        if not rows:
            return []

        # حذف ردیف عنوان
        data = rows[1:]

        return data

    except Exception as error:

        print(
            "خطا در خواندن فایل Excel:",
            error
        )

        return []