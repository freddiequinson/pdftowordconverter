from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Configure templates path for Vercel deployment
app.template_folder = os.path.abspath('../templates')
app.static_folder = os.path.abspath('../static')

def allowed_file(filename):
    allowed_extensions = {'pdf', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

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
        # Secure the filename and get file extension
        original_filename = secure_filename(file.filename)
        file_extension = get_file_extension(original_filename)
        
        # Determine conversion type based on file extension
        if file_extension == 'pdf':
            output_type = 'Word'
            new_extension = 'docx'
        elif file_extension == 'docx':
            output_type = 'PDF'
            new_extension = 'pdf'
        
        # Generate a demo filename
        original_name = original_filename.rsplit('.', 1)[0]
        suggested_filename = f"{original_name}.{new_extension}"
        
        # In this demo version, we don't actually convert the file
        # Instead, we show a message explaining that this is a demo
        
        # Return a demo result page
        return render_template('result.html', 
                              download_url="#", 
                              original_filename=original_filename,
                              output_type=output_type,
                              suggested_filename=suggested_filename,
                              demo_mode=True)
    else:
        return jsonify({'error': 'File type not allowed. Please upload a PDF or DOCX file.'}), 400

@app.route('/download')
def download_info():
    return jsonify({
        'message': 'This is a demo version. To use the full converter, please download and run the application locally.'
    })

# Vercel serverless function handler
def handler(event, context):
    return app(event, context)

# For local development
if __name__ == '__main__':
    app.run(debug=True)
