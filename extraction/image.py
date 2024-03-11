from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
import fitz  # PyMuPDF
from PIL import Image as PILImage
import re
import os
import shutil

def clear_directory(directory):
    """
    Clears all images in the specified directory.
    """
    try:
        # Iterate over all files in the directory
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            # Check if the file is a regular file
            if os.path.isfile(file_path):
                # Remove the file
                os.remove(file_path)
    except Exception as e:
        print(f"Error occurred while clearing the image directory: {e}")

def extract_trademarks_and_logos(pdf_file, output_excel):
    wb = Workbook()
    ws = wb.active
    ws.append(['TradeMarkNo.', 'Images','Image Path'])

    doc = fitz.open(pdf_file)
    clear_directory('output/images')

    row = 2  # Start from the second row to leave space for the header

    for page in doc:
        text = page.get_text()
        images = page.get_images(full=True)

        trademark_numbers = re.findall(r'\(210\): (\d+) \(220\)', text)  # Extract numbers between (210): and (220):
        logos = []
        image_index = 0

        for trademark_number in trademark_numbers:
            # Check if the last word of the trademark is in capital letters
            last_word_caps = trademark_number.split()[-1].isupper()

            # If the last word is not in capital letters and we have images available
            if not last_word_caps and image_index < len(images):
                try:
                    image_path = f"output/images/{trademark_number}.png"
                    pix = fitz.Pixmap(doc, images[image_index][0])
                    pil_image = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    pil_image = pil_image.resize((50, 50))  # Resize the image to 50x50
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
                ws.cell(row=row, column=3).value = image_path
            else:
                ws.cell(row=row, column=2).value = "No Image"
            ws.cell(row=row, column=1).value = trademark_number
            row += 1

    wb.save(output_excel)
