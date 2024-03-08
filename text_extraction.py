import os
import re
import PyPDF2
import pandas as pd

def extract_data(file_path, start_page, end_page):
    data = []

    try:
        # Open the PDF file
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

            # Iterate over pages and extract data
            if end_page > 97:
                end_page = 97

            # Extract text from each page within the specified range
            for page_idx in range(start_page - 1, end_page):
                if page_idx >= num_pages:
                    break

                page = pdf_reader.pages[page_idx]
                page_content = page.extract_text()

                # Extract blocks using a regular expression
                blocks = re.findall(r'\(210\) : (\d+)\s+.*?\(220\) : (\d{2}/\d{2}/\d{4}).*?(?=\(\d{3}\)|\(210\)|$).*?\(511\) : (.*?)(?=\(\d{3}\)|\(210\)|\(730\)|\(740\)|$).*?\(730\) : (.*?)(?=\(\d{3}\)|\(210\)|\(740\)|$).*?\(740\) : (.*?)(?=\(\d{3}\)|\(210\)|$)', page_content, re.DOTALL)

                for block in blocks:
                    trademark_number = block[0]
                    filing_date = block[1].strip()
                    international_class = block[2].strip()
                    proprietor = block[3].strip()
                    representative = block[4].strip()

                    # Find and move last consecutive sequence of all uppercase letters to Image/Mark
                    words = representative.split()
                    image_mark = ""
                    for i in range(len(words) - 1, -1, -1):
                        if words[i].isupper():
                            image_mark = words[i] + " " + image_mark
                        else:
                            break
                    image_mark = image_mark.strip()

                    if image_mark:
                        representative = ' '.join(words[:i+1])

                    data.append({
                        "Trademark Number (210)": trademark_number,
                        "Application Filing Date (220)": filing_date,
                        "Class of registration (511)": international_class,
                        "Proprietor (730)": proprietor,
                        "Representative/Applicant (740)": representative,
                        "Image/Mark": image_mark
                    })

    except Exception as e:
        print(f"Error occurred: {e}")

    if not data:
        print("No data found within the specified page range.")

    return data

