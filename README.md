PDF Trademark Extraction Tool

This tool extracts trademark information and images from a PDF document and saves them into an Excel file. It offers the flexibility to select a specific range of pages for extraction and ensures that existing images in the folder are cleared before extraction begins.
Installation

    Clone the repository:

    bash

git clone https://github.com/Keltings/Pdf_Data_Extraction.git

Install the required dependencies:

    pip install -r requirements.txt

Usage

    Run the script:

    python image_extraction.py

    Follow the on-screen prompts to enter the necessary information, including the PDF file name, Excel file name, start page number, and end page number.

    The tool will then extract trademark information and images from the specified pages and save them into the Excel file.

File Structure

    extract_trademarks.py: Main Python script for extracting trademarks and images.
    README.md: Documentation file providing information about the tool and its usage.
    requirements.txt: List of Python dependencies required for the tool.
    Images/: Folder to store extracted images.
    Data/: Folder to store the generated Excel files.

