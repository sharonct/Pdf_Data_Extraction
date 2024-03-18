from extraction.process_pdf import process_pdf
from combined.merged import fill_missing_images
from openpyxl import Workbook
import os

if __name__ == "__main__":
    folder_path = input('Enter Folder Path: ')
    output_excel_path = 'output/final.xlsx'
    output_excel = Workbook()

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_file_path = os.path.join(folder_path, filename)
            df_text, df_image = process_pdf(pdf_file_path)
            fill_missing_images(df_text, df_image, output_excel, sheet_name=filename)

    output_excel.save(output_excel_path)
    print("Excel file created successfully.")