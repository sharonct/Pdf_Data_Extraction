import fitz  # PyMuPDF
from PIL import Image as PILImage
import re
import pandas as pd
import io

def extract_trademarks_and_logos(pdf_file):
    doc = fitz.open(pdf_file)

    trademark_data = []

    for page in doc:
        text = page.get_text()
        images = page.get_images(full=True)

        trademark_numbers = re.findall(r'\(210\): (\d+) \(220\)', text)  # Extract numbers between (210): and (220):
        image_index = 0

        for trademark_number in trademark_numbers:
            last_word_caps = trademark_number.split()[-1].isupper()

            if not last_word_caps and image_index < len(images):
                try:
                    pix = fitz.Pixmap(doc, images[image_index][0])
                    pil_image = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    pil_image = pil_image.resize((50, 50))  # Resize the image to 50x50
                    img_bytes = io.BytesIO()
                    pil_image.save(img_bytes, format='PNG')
                    img_bytes = img_bytes.getvalue()
                    trademark_data.append({'TrademarkNo': trademark_number, 'ImageData': img_bytes})
                    image_index += 1
                except Exception as e:
                    print(f"Error processing image: {e}")
                    trademark_data.append({'TrademarkNo': trademark_number, 'ImageData': None})
            else:
                trademark_data.append({'TrademarkNo': trademark_number, 'ImageData': None})

    df = pd.DataFrame(trademark_data)
    return df

