from flask import Flask, render_template, request, redirect, url_for, session
import os
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key'

UPLOAD_FOLDER = 'static/uploads'
EXCEL_FILE = 'data/responses.xlsx'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    vendor_data = {key: request.form.get(key, '') for key in request.form}

    image = request.files.get('company_image')
    if image and image.filename:
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.filename}")
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)
        vendor_data['Company Board Image'] = image_path
    else:
        vendor_data['Company Board Image'] = ''

    session['vendor_data'] = vendor_data
    session['machines'] = []

    return redirect(url_for('machine_entry'))

@app.route('/machine_entry')
def machine_entry():
    return render_template('machine_entry.html')

@app.route('/machine_entry', methods=['POST'])
def submit_machine_entry():
    machine = request.form.get('machine')
    size = request.form.get('size')
    hour_rate = request.form.get('hour_rate')

    image_files = request.files.getlist('machine_images')
    image_paths = []
    for image in image_files:
        if image and image.filename:
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image.filename}")
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)
            image_paths.append(image_path)

    session['current_machine'] = {
        'Machine': machine,
        'Size': size,
        'Hour Rate': hour_rate,
        'Image Paths': image_paths
    }

    return redirect(url_for('specs_form'))

@app.route('/specs_form')
def specs_form():
    machine = session['current_machine']['Machine']
    size = session['current_machine']['Size']
    return render_template('specs_form.html', machine=machine, size=size)

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    specs = {key: request.form.get(key, '') for key in request.form}
    machine_info = session.get('current_machine', {})
    machine_info.update(specs)
    session['machines'].append(machine_info)

    if request.form['action'] == 'add':
        return redirect(url_for('machine_entry'))
    else:
        all_rows = []
        for machine in session['machines']:
            row = session['vendor_data'].copy()
            row.update(machine)
            row['Machine Images'] = ', '.join(machine.get('Image Paths', []))
            all_rows.append(row)

        df = pd.DataFrame(all_rows)

        if os.path.exists(EXCEL_FILE):
            existing_df = pd.read_excel(EXCEL_FILE)
            df = pd.concat([existing_df, df], ignore_index=True)

        df.to_excel(EXCEL_FILE, index=False)

        session.pop('vendor_data', None)
        session.pop('machines', None)
        session.pop('current_machine', None)

        return render_template('final_submit.html')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)










