from flask import Flask, render_template, request, redirect
import os
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
EXCEL_FILE = os.path.join(DATA_FOLDER, 'responses.xlsx')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# Temporary store for all form data
session_data = {}

# Utility: Save data to Excel
def save_to_excel(data):
    df = pd.DataFrame([data])
    
    # If file doesn't exist, write new Excel file
    if not os.path.exists(EXCEL_FILE):
        df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
    else:
        try:
            # Try reading existing data
            existing = pd.read_excel(EXCEL_FILE, engine='openpyxl')
            final_df = pd.concat([existing, df], ignore_index=True)
            final_df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            print("Overwriting corrupted Excel file with fresh data.")
            # Overwrite corrupted file with new data
            df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')


@app.route('/')
def index():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    # Safely collect all inputs
    session_data['company_name'] = request.form.get('company_name', '')
    session_data['vendor_name'] = request.form.get('vendor_name', '')
    session_data['address'] = request.form.get('address', '')
    session_data['email'] = request.form.get('email', '')
    session_data['phone'] = request.form.get('phone', '')
    session_data['gstin'] = request.form.get('gstin', '')
    session_data['contact_name'] = request.form.get('contact_name', '')
    session_data['contact_no'] = request.form.get('contact_no', '')
    session_data['contact_email'] = request.form.get('contact_email', '')
    session_data['website'] = request.form.get('website', '')
    session_data['payment_terms'] = request.form.get('payment_terms', '')

    image = request.files.get('company_image')
    if image and image.filename:
        filename = secure_filename(image.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        image.save(filepath)
        session_data['company_image'] = filename
    else:
        session_data['company_image'] = ''

    # Now redirect to machine form
    return redirect('/machine_entry')

@app.route('/machine_entry', methods=['GET', 'POST'])
def machine_entry():
    if request.method == 'POST':
        session_data['machine'] = request.form.get('machine', '')
        session_data['size'] = request.form.get('size', '')
        session_data['hour_rate'] = request.form.get('hour_rate', '')

        # Handle multiple images
        images = request.files.getlist('machine_images')
        image_filenames = []
        for img in images:
            if img and img.filename:
                fname = secure_filename(img.filename)
                img.save(os.path.join(UPLOAD_FOLDER, fname))
                image_filenames.append(fname)
        session_data['machine_images'] = ', '.join(image_filenames)

        return redirect('/specs_form')
    return render_template('machine_entry.html')

@app.route('/specs_form')
def specs_form():
    return render_template('specs_form.html',
        machine=session_data.get('machine'),
        size=session_data.get('size'))

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    try:
        spec_fields = [
            'make', 'model_year', 'type', 'axis_config', 'x_travel', 'y_travel', 'z_travel',
            'a_travel', 'b_travel', 'c_travel', 'max_part_size', 'max_part_height',
            'spindle_taper', 'spindle_power', 'spindle_torque', 'main_spindle_rpm',
            'aux_spindle_rpm', 'max_table_load', 'coolant_pressure', 'pallet_type',
            'tolerance_standard', 'accuracy_xyz', 'accuracy_abc', 'accuracy_table',
            'angle_head', 'controller', 'cad_software', 'cam_software',
            'wire_diameter', 'taper_degree', 'max_cutting_thickness', 'surface_finish',
            'electrode_diameter', 'spindle_stroke', 'table_size', 'sink_size'
        ]

        for field in spec_fields:
            session_data[field] = request.form.get(field, '')

        action = request.form.get('action')
        save_to_excel(session_data.copy())

        if action == 'add':
            return redirect('/machine_entry')
        else:
            return redirect('/final_submit')
    except Exception as e:
        return f"<h3>Error occurred: {str(e)}</h3>", 500

@app.route('/final_submit')
def final_submit():
    return render_template('final_submit.html')

@app.route('/view_responses')
def view_responses():
    if not os.path.exists(EXCEL_FILE):
        return "<h3>No responses yet.</h3>"
    df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
    return render_template('view_responses.html',
                           tables=[df.to_html(classes='table', index=False)],
                           titles=df.columns.values)
from flask import send_file

@app.route('/download_responses')
def download_responses():
    if os.path.exists(EXCEL_FILE):
        return send_file(EXCEL_FILE, as_attachment=True)
    return "<h3>No response file found to download.</h3>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)












