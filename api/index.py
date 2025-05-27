from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
import os
import io
import uuid
import base64
import tempfile
from werkzeug.utils import secure_filename
import json

# Conversion libraries
from pdf2docx import Converter as PDFToDocxConverter
from docx2pdf import convert as docx_to_pdf_convert

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Configure templates path for Vercel deployment
app.template_folder = os.path.abspath('../templates')
app.static_folder = os.path.abspath('../static')

# In-memory storage for files (for demo purposes)
# In a production app, you would use a proper cloud storage service
TEMP_STORAGE = {}

def allowed_file(filename):
    allowed_extensions = {'pdf', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def pdf_to_docx(pdf_data, output_path):
    try:
        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(pdf_data)
            temp_pdf_path = temp_pdf.name
        
        # Convert PDF to DOCX
        converter = PDFToDocxConverter(temp_pdf_path)
        converter.convert(output_path)
        converter.close()
        
        # Clean up the temporary PDF file
        os.unlink(temp_pdf_path)
        
        return True
    except Exception as e:
        print(f"Error converting PDF to DOCX: {str(e)}")
        return False

def docx_to_pdf(docx_data, output_path):
    try:
        # Create a temporary file for the DOCX
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
            temp_docx.write(docx_data)
            temp_docx_path = temp_docx.name
        
        # Convert DOCX to PDF
        docx_to_pdf_convert(temp_docx_path, output_path)
        
        # Clean up the temporary DOCX file
        os.unlink(temp_docx_path)
        
        return True
    except Exception as e:
        print(f"Error converting DOCX to PDF: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Secure the filename and generate a unique name
        original_filename = secure_filename(file.filename)
        file_extension = get_file_extension(original_filename)
        file_id = str(uuid.uuid4())
        
        # Read the file data
        file_data = file.read()
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            if file_extension == 'pdf':
                # Convert PDF to DOCX
                output_filename = f"{file_id}.docx"
                output_path = os.path.join(temp_dir, output_filename)
                success = pdf_to_docx(file_data, output_path)
                output_type = 'Word'
                mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif file_extension == 'docx':
                # Convert DOCX to PDF
                output_filename = f"{file_id}.pdf"
                output_path = os.path.join(temp_dir, output_filename)
                success = docx_to_pdf(file_data, output_path)
                output_type = 'PDF'
                mime_type = 'application/pdf'
            
            if success:
                # Read the converted file
                with open(output_path, 'rb') as f:
                    converted_data = f.read()
                
                # Store in memory (in a real app, you'd use cloud storage)
                TEMP_STORAGE[file_id] = {
                    'data': converted_data,
                    'filename': output_filename,
                    'mime_type': mime_type
                }
                
                # Generate download link
                download_url = url_for('download_file', file_id=file_id)
                original_name = original_filename.rsplit('.', 1)[0]
                new_extension = 'docx' if file_extension == 'pdf' else 'pdf'
                suggested_filename = f"{original_name}.{new_extension}"
                
                return render_template('result.html', 
                                      download_url=download_url, 
                                      original_filename=original_filename,
                                      output_type=output_type,
                                      suggested_filename=suggested_filename)
            else:
                return jsonify({'error': f'Error converting {file_extension.upper()} file'}), 500
    else:
        return jsonify({'error': 'File type not allowed. Please upload a PDF or DOCX file.'}), 400

@app.route('/download/<file_id>')
def download_file(file_id):
    if file_id not in TEMP_STORAGE:
        return jsonify({'error': 'File not found or expired'}), 404
    
    file_info = TEMP_STORAGE[file_id]
    
    # Create an in-memory file-like object
    file_data = io.BytesIO(file_info['data'])
    
    # Send the file
    return send_file(
        file_data,
        mimetype=file_info['mime_type'],
        as_attachment=True,
        download_name=file_info['filename']
    )

# Vercel serverless function handler
def handler(event, context):
    return app(event, context)

# For local development
if __name__ == '__main__':
    app.run(debug=True)
