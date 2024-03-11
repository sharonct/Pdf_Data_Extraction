import pandas as pd
from extraction.image import extract_trademarks_and_logos
from extraction.text import extract_data
from combined.merged import fill_missing_images

if __name__ == "__main__":
    file_path = input('Enter PDF File Path: ')
    start_page = int(input('Enter Start Page: '))
    end_page = int(input('Enter End Page: '))
    

    data = extract_data(file_path, start_page, end_page)

    df = pd.DataFrame(data)
    df.to_excel("output/text.xlsx", index=False)

    extract_trademarks_and_logos(file_path, "output/images.xlsx")
    
    fill_missing_images("output/text.xlsx", "output/images.xlsx", "output/final.xlsx")
