import PyPDF2
import re
import pandas as pd

def extract_info(block):
    trademark_number_match = re.search(r'210\)\s*:?\s*(\d+)', block)
    filing_date_match = re.search(r'\(220\) : (\d{2}/\d{2}/\d{4})', block)
    class_registration_match = re.search(r'\(511\) : (.*?)(?=\(\d{3}\)|\(220\)|\(210\)|$)', block, re.DOTALL)
    proprietor_match = re.search(r'\(730\)\s*:\s*(.*?)(?=\(740\)|$)', block, re.DOTALL)
    representative_match = re.search(r'\(740\) : (.*?)(?=\(\d{3}\)|$)', block, re.DOTALL)

    trademark_number = trademark_number_match.group(1) if trademark_number_match else ''
    filing_date = filing_date_match.group(1) if filing_date_match else ''
    class_registration = class_registration_match.group(1).strip() if class_registration_match else ''
    proprietor = proprietor_match.group(1).strip() if proprietor_match else ''
    representative = representative_match.group(1).strip() if representative_match else ''

    # Extracting data for Image/Mark column
    image_mark = ''
    if representative:
        # Move words after "None" to the Image/Mark column
        if "None" in representative:
            words_after_none = representative.split("None", 1)[-1].strip()
            if words_after_none:
                image_mark = words_after_none
                representative = representative.replace(words_after_none, "").strip()
        else:
            # Check from the end if the words are all uppercase
            words = representative.split()
            all_caps_words = []
            for word in reversed(words):
                if word.isupper():
                    all_caps_words.insert(0, word)
                else:
                    break
            if all_caps_words:
                # If all words are uppercase, move them to the Image/Mark column
                image_mark = ' '.join(all_caps_words)
                # Remove the all-uppercase words from the Representative column
                representative = ' '.join(words[:-len(all_caps_words)])

    return trademark_number, filing_date, class_registration, proprietor, representative, image_mark

def extract_data(file_path, start_page, end_page):
    data = {
        "Trademark Number (210)": [],
        "Application Filing Date (220)": [],
        "Class of registration (511)": [],
        "Proprietor/Owner (730)": [],
        "Representative/Applicant (740)": [],
        "Image/Mark": []
    }

    try:
        # Open the PDF file
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

            # Iterate over pages within the specified range
            block = ''  # Initialize block
            for page_idx in range(start_page - 1, min(end_page, num_pages)):
                page = pdf_reader.pages[page_idx]
                page_content = page.extract_text()

                # Split page content by lines and remove newline characters
                lines = [line.strip() for line in page_content.split('\n')]

                # Filter out lines that contain the page header text or page numbers
                lines = [line for line in lines if not any(header_text in line for header_text in ['(19) KE - Industrial Property Journal -', '_________', 'Page']) and not line.isdigit() and not '(19) KE - Industrial Pr operty Journal - No.' in line]
                # Iterate over lines to identify blocks
                for line in lines:
                    if '210' in line:
                        # If a new block starts, extract info from the previous block
                        if block:
                            info = extract_info(block)
                            if info:
                                data["Trademark Number (210)"].append(info[0])
                                data["Application Filing Date (220)"].append(info[1])
                                data["Class of registration (511)"].append(info[2])
                                data["Proprietor/Owner (730)"].append(info[3])
                                data["Representative/Applicant (740)"].append(info[4])
                                data["Image/Mark"].append(info[5])
                        # Start a new block
                        block = line
                    else:
                        # Append line to the current block
                        block += ' ' + line

            # Extract info from the last block on the last page
            if block:
                info = extract_info(block)
                if info:
                    data["Trademark Number (210)"].append(info[0])
                    data["Application Filing Date (220)"].append(info[1])
                    data["Class of registration (511)"].append(info[2])
                    data["Proprietor/Owner (730)"].append(info[3])
                    data["Representative/Applicant (740)"].append(info[4])
                    data["Image/Mark"].append(info[5])

    except Exception as e:
        print(f"Error occurred: {e}")

    if not data:
        print("No data found within the specified page range.")

    df = pd.DataFrame(data)

    return df

