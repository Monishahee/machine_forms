
from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
EXCEL_FILE = 'responses.xlsx'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Shared form data stored in memory
session_data = {}

@app.route('/')
def index():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    global session_data

    # Get form fields
    data = request.form.to_dict()

    # Save uploaded company board image
    company_image = request.files.get('company_image')
    if company_image and company_image.filename:
        filename = secure_filename(company_image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        company_image.save(image_path)
        data['company_image'] = image_path
    else:
        data['company_image'] = ''

    # Store in session
    session_data = data

    return redirect(url_for('machine_entry'))

@app.route('/machine_entry', methods=['GET', 'POST'])
def machine_entry():
    if request.method == 'POST':
        global session_data
        machine_data = request.form.to_dict()

        # Save machine images
        images = request.files.getlist('machine_images')
        image_paths = []
        for image in images:
            if image and image.filename:
                filename = secure_filename(image.filename)
                path = os.path.join(UPLOAD_FOLDER, filename)
                image.save(path)
                image_paths.append(path)

        machine_data['machine_images'] = ', '.join(image_paths)
        session_data.update(machine_data)

        return redirect(url_for('specs_form', machine=machine_data['machine'], size=machine_data['size']))
    
    return render_template('machine_entry.html')

@app.route('/specs_form')
def specs_form():
    machine = request.args.get('machine')
    size = request.args.get('size')
    return render_template('specs_form.html', machine=machine, size=size)

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    global session_data
    spec_data = request.form.to_dict()
    session_data.update(spec_data)

    # Save to Excel
    save_to_excel(session_data)

    return render_template('final_submit.html')

def save_to_excel(data_dict):
    # Convert to DataFrame
    df = pd.DataFrame([data_dict])

    if os.path.exists(EXCEL_FILE):
        existing_df = pd.read_excel(EXCEL_FILE)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
    else:
        combined_df = df

    combined_df.to_excel(EXCEL_FILE, index=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)












