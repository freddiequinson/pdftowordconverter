import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
import threading
import time

# Conversion libraries
from pdf2docx import Converter as PDFToDocxConverter
from docx2pdf import convert as docx_to_pdf_convert

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['DOWNLOAD_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def pdf_to_docx(pdf_path, docx_path):
    try:
        # Convert PDF to DOCX
        converter = PDFToDocxConverter(pdf_path)
        converter.convert(docx_path)
        converter.close()
        return True
    except Exception as e:
        print(f"Error converting PDF to DOCX: {str(e)}")
        return False

def docx_to_pdf(docx_path, pdf_path):
    try:
        # Convert DOCX to PDF
        docx_to_pdf_convert(docx_path, pdf_path)
        return True
    except Exception as e:
        print(f"Error converting DOCX to PDF: {str(e)}")
        return False

def cleanup_old_files():
    """Delete files older than 1 hour"""
    while True:
        current_time = time.time()
        for folder in [app.config['UPLOAD_FOLDER'], app.config['DOWNLOAD_FOLDER']]:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    # If file is older than 1 hour, delete it
                    if current_time - os.path.getmtime(file_path) > 3600:
                        os.remove(file_path)
        time.sleep(3600)  # Check every hour

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    # Check if a file was uploaded
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Secure the filename and generate a unique name
        original_filename = secure_filename(file.filename)
        file_extension = get_file_extension(original_filename)
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the uploaded file
        file.save(upload_path)
        
        # Determine conversion type based on file extension
        if file_extension == 'pdf':
            # Convert PDF to DOCX
            output_filename = f"{uuid.uuid4()}.docx"
            output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)
            success = pdf_to_docx(upload_path, output_path)
            output_type = 'Word'
        elif file_extension == 'docx':
            # Convert DOCX to PDF
            output_filename = f"{uuid.uuid4()}.pdf"
            output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)
            success = docx_to_pdf(upload_path, output_path)
            output_type = 'PDF'
        
        if success:
            # Generate download link
            download_url = url_for('download_file', filename=output_filename)
            original_name = original_filename.rsplit('.', 1)[0]
            new_extension = 'docx' if file_extension == 'pdf' else 'pdf'
            suggested_filename = f"{original_name}.{new_extension}"
            
            return render_template('result.html', 
                                  download_url=download_url, 
                                  original_filename=original_filename,
                                  output_type=output_type,
                                  suggested_filename=suggested_filename)
        else:
            flash(f'Error converting {file_extension.upper()} file. Please try again.')
            return redirect(url_for('index'))
    else:
        flash('File type not allowed. Please upload a PDF or DOCX file.')
        return redirect(url_for('index'))

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
