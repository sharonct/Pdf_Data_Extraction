from extraction.image import extract_trademarks_and_logos
from extraction.text import extract_data
from combined.merged import fill_missing_images

if __name__ == "__main__":
    file_path = input('Enter PDF File Path: ')
    start_page = int(input('Enter Start Page: '))
    end_page = int(input('Enter End Page: '))
    

    df_text = extract_data(file_path, start_page, end_page)
    
    df_image = extract_trademarks_and_logos(file_path )

    fill_missing_images(df_text, df_image,'output/final.xlsx')
