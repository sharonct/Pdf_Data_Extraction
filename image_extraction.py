import os
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
import fitz  # PyMuPDF
from PIL import Image as PILImage
import re

def extract_trademarks_and_logos(pdf_file, output_excel):
    # Define paths for the folders
    images_folder = "Images"
    data_folder = "Data"
    images_path = os.path.join(data_folder, images_folder)
    excel_path = os.path.join(data_folder, output_excel)

    # Create the folders if they don't exist
    os.makedirs(images_path, exist_ok=True)

    # Create a workbook and add a worksheet
    wb = Workbook()
    ws = wb.active
    ws.append(['TradeMarkNo.', 'Images'])

    doc = fitz.open(pdf_file)
    row = 2  # Start from the second row to leave space for the header

    for page in doc:
        text = page.get_text()
        images = page.get_images(full=True)
        #print(page)
        trademark_numbers = re.findall(r'\(210\): (\d+) \(220\)', text)
        logos = []
        image_index = 0

        for trademark_number in trademark_numbers:
            last_word_caps = trademark_number.split()[-1].isupper()

            if not last_word_caps and image_index < len(images):
                try:
                    image_path = os.path.join(images_path, f"{trademark_number}.png")
                    pix = fitz.Pixmap(doc, images[image_index][0])
                    pil_image = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    pil_image = pil_image.resize((50, 50))
                    pil_image.save(image_path)
                    logos.append(image_path)
                    image_index += 1
                except Exception as e:
                    print(f"Error saving image: {e}")
            else:
                logos.append(None)

        for idx, trademark_number in enumerate(trademark_numbers):
            image_path = logos[idx]
            if image_path:
                img_xl = XLImage(image_path)
                img_xl.anchor = ws.cell(row=row, column=2).coordinate
                ws.add_image(img_xl)
            else:
                ws.cell(row=row, column=2).value = "No Image"
            ws.cell(row=row, column=1).value = trademark_number
            row += 1

    wb.save(excel_path)

if __name__ == "__main__":
    extract_trademarks_and_logos("November_2023_Journal.pdf", "images.xlsx")
