import PyPDF2
import re
import pandas as pd

def extract_info(block):
    trademark_number_match = re.search(r'(\d+)\s*\(220\)', block)
    filing_date_match = re.search(r'\(220\)[^:]*:?\s*(\d{1,2}/\d{1,2}/\d{2,4})', block)
    class_registration_match = re.search(r'\(511\)\s*\D*(\d.*?)\s*(?=\(\d{3}\)|$)', block, re.DOTALL)              
    proprietor_match = re.search(r'\(730\)\s*(?:[^:]*:\s*)?(.*?)(?=\(\d{3}\)|$)', block, re.DOTALL)                          
    representative_match = re.search(r'\(740\)\s*(?:[^:]*:\s*)?(.*?)(?=\(\d{3}\)|$)', block, re.DOTALL)

    trademark_number = trademark_number_match.group(1) if trademark_number_match else ''
    filing_date = filing_date_match.group(1) if filing_date_match else ''
    class_registration = class_registration_match.group(1).strip() if class_registration_match else ''
    proprietor = proprietor_match.group(1).strip() if proprietor_match else ''
    representative = representative_match.group(1).strip() if representative_match else ''

    # Extracting data for Image/Mark column
    image_mark = ''

    # Function to split text after "Kenya" and move capitalized words to Image/Mark column
    def move_words_after_kenya(text):
        kenya_match = re.search(r'K\s*e\s*n\s*y\s*a', text, re.IGNORECASE)
        if kenya_match:
            kenya_index = kenya_match.end()
            kenya_part = text[:kenya_index].strip()  # Include "Kenya" and preceding text
            words_after_kenya = text[kenya_index:].strip()

            if words_after_kenya:
                image_mark = words_after_kenya
                return kenya_part, image_mark

        return text, ""


    if representative:
        # Apply the move_words_after_kenya function to the Representative/Applicant (740) column
        representative, image_mark = move_words_after_kenya(representative)


        # Move words after "None" to the Image/Mark column
        if "None" in representative:
            words_after_none = representative.split("None", 1)[-1].strip()
            if words_after_none:
                image_mark = words_after_none
                representative = representative.replace(words_after_none, "").strip()
        else:
            # Check from the end if the words are all uppercase (excluding "NAIROBI")
            words = representative.split()
            all_caps_words = []
            nairobi_found = False
            for word in reversed(words):
                if word.upper() == "NAIROBI":
                    nairobi_found = True
                    continue
                if word.isupper():
                    all_caps_words.insert(0, word)
                else:
                    break
            if all_caps_words:
                # If there are uppercase words (excluding "NAIROBI"), move them to the Image/Mark column
                image_mark = ' '.join(all_caps_words)
                # Remove the all-uppercase words from the Representative column
                representative = ' '.join(words[:-len(all_caps_words)])
            elif nairobi_found:
                # If "NAIROBI" is found but there are no other all-caps words, leave the representative column unchanged
                pass

    return trademark_number, filing_date, class_registration, proprietor, representative, image_mark

def extract_data(file_path):
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
            for page_idx in range(num_pages):
                page = pdf_reader.pages[page_idx]
                page_content = page.extract_text()

                # Split page content by lines and remove newline characters
                lines = [line.strip() for line in page_content.split('\n')]            

                def is_header(line):
                    header_patterns = [
                        r'Industrial Property Journal',  # Text similar to Industrial Property Journal
                        r'\(19\) KE - Industrial Property Journal - No\. \d{4}/\d{2} \d{2}/\d{2}/\d{4}', # e.g., (19) KE - Industrial Property Journal - No. 2024/02 29/02/2024
                        r'\(19\) KE - Industrial\s*Pr\s*operty Journal - No\.\s*\d{4}/\d{2}\s+\d{2}/\d{2}\s+/\s*\d{4}', # e.g., (19) KE - Industrial Pr operty Journal - No. 2023/10   31/10 /2023                        
                        r'\(\d+\) KE - Industrial Property Journal - No\. \d+/\d+ \d+/\d+/\d+',  # More general pattern for header
                    ]
                    return any(re.search(pattern, line) for pattern in header_patterns)

                # Filter out lines that match any of the header patterns, contain digits, "Page",
                # or consist of only underscores
                lines = [re.sub(r'_+', '', line) for line in lines if not is_header(line) 
                        and not line.isdigit() 
                        and "Page" not in line 
                        and not all(c == '_' for c in line.strip())]
                              
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

    # Function to remove commas from the Image/Mark column
    def remove_commas(text):
        return text.replace(',', '')
    
    data["Image/Mark"] = [remove_commas(text) for text in data["Image/Mark"]]

    df = pd.DataFrame(data)

    # Replace empty strings with NaN values
    df.replace('', pd.NA, inplace=True)

    # Drop rows with data only in one column
    df = df.dropna(subset=df.columns, thresh=2)

    return df
