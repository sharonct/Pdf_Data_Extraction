import pandas as pd
from image_extraction import extract_trademarks_and_logos
from text_extraction import extract_data
from combined.merged import fill_missing_images

if __name__ == "__main__":
    file_path = input('Enter PDF File Path: ')
    start_page = int(input('Enter Start Page: '))
    end_page = int(input('Enter End Page: '))

    data = extract_data(file_path, start_page, end_page)

    df = pd.DataFrame(data)
    df.to_excel("Data/text.xlsx", index=False)

    extract_trademarks_and_logos(file_path, "Data/images.xlsx")
    
    fill_missing_images("Data/text.xlsx", "Data/images.xlsx", "Data/output.xlsx")
