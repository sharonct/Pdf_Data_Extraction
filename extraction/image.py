from io import BytesIO
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
import fitz  # PyMuPDF
from PIL import Image as PILImage
import re
import pandas as pd

def extract_trademarks_and_logos(pdf_file):
    # Open the PDF document
    doc = fitz.open(pdf_file)

    # Start from the second row to leave space for the header

    # Lists to store trademarks with and without capitalized last words
    trademarks_with_caps = []
    trademarks_without_caps = []
    trademark_data = []

        # Iterate through each page of the PDF
    for page_num, page in enumerate(doc, start=1):
        # Extract text from the page
        text = page.get_text()

        # Extract images from the page and sort them based on their y-coordinates
        # Extract images from the page
        images = page.get_images(full=True)

    # Sort images based on their y-coordinates (top to bottom)
# Sort images based on their image numbers
        images = sorted(images, key=lambda img: img[0])
        # Reset image_index for each new page
        image_index = 0

        # Extract trademark numbers from the text between (210) and (220)
        trademarks_210_220 = re.findall(r'(\d+)\s*\(220\)', text, re.DOTALL)

        # Extract trademark numbers from the text after (740)
        trademarks_740 = re.findall(r'\(210\):(.+?)(?=\(210\)|$)', text, re.DOTALL)

        # Lists to store trademarks with and without capitalized last words
        trademarks_with_caps = []
        trademarks_without_caps = []

        # Zip the two lists together
        for trademark_210_220, trademark_740 in zip(trademarks_210_220, trademarks_740):
            # Check if the last word of the trademark_740 is in capital letters
            last_word_caps = re.findall(r'[A-Z]+$', trademark_740.strip())
            words_after_none = re.findall(r'None\s*(\w+)', trademark_740.strip())


            # Check if the last word of the trademark is capitalized
            if last_word_caps or words_after_none:
                trademarks_with_caps.append(trademark_210_220)
                
            else:
                # If neither condition is met, add the trademark to trademarks_without_caps
                trademarks_without_caps.append(trademark_210_220)

        # Assign images to trademarks without capitalized last words
        for trademark_number in trademarks_without_caps:
            if image_index < len(images):
                try:
                    pix = fitz.Pixmap(doc, images[image_index][0])
                    pil_image = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    pil_image = pil_image.resize((50, 50))  # Resize the image to 50x50

                    # Create an in-memory file-like object
                    img_bytes = BytesIO()
                    pil_image.save(img_bytes, format="PNG")

                    img_bytes = img_bytes.getvalue()
                    trademark_data.append({'TrademarkNo': trademark_number, 'ImageData': img_bytes})
                    image_index += 1

                except Exception as e:
                    print(f"Error processing image: {e}")
                    trademark_data.append({'TrademarkNo': trademark_number, 'ImageData': None})
            else:
                trademark_data.append({'TrademarkNo': trademark_number, 'ImageData': None})

        # Reset image_index at the end of each page iteration
        image_index = 0


    df = pd.DataFrame(trademark_data)
    return df
