# PDF & Word Converter

A simple web application that allows users to convert PDF files to Word documents and vice versa.

## Features

- PDF to Word conversion
- Word to PDF conversion
- Clean, modern user interface
- Drag and drop file upload
- Secure file handling
- Automatic file cleanup (files are deleted after 1 hour)

## Requirements

- Python 3.7+
- Flask
- pdf2docx
- docx2pdf

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

1. Start the application:

```
python app.py
```

2. Open your web browser and navigate to `http://127.0.0.1:5000`
3. Select the conversion type (PDF to Word or Word to PDF)
4. Upload your file by dragging and dropping or using the browse button
5. Click "Convert Now"
6. Download your converted file

## Notes

- Maximum file size is 16MB
- Uploaded and converted files are automatically deleted after 1 hour
- Supported file formats: PDF (.pdf) and Word (.docx)

## License

This project is open-source and free to use.
