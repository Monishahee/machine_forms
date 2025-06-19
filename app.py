from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Folder setup
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
EXCEL_FILE = os.path.join(DATA_FOLDER, 'responses.xlsx')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# Temporary store
session_data = {}

def save_to_excel(data):
    df = pd.DataFrame([data])
    if not os.path.exists(EXCEL_FILE):
        df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
    else:
        existing = pd.read_excel(EXCEL_FILE, engine='openpyxl')
        final_df = pd.concat([existing, df], ignore_index=True)
        final_df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')

@app.route('/')
def index():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    try:
        session_data['company_name'] = request.form.get('company_name', '')
        session_data['vendor_name'] = request.form.get('vendor_name', '')
        session_data['address'] = request.form.get('address', '')
        session_data['email'] = request.form.get('email', '')
        session_data['phone'] = request.form.get('phone', '')
        session_data['gstin'] = request.form.get('gstin', '')
        session_data['website'] = request.form.get('website', '')
        session_data['payment_terms'] = request.form.get('payment_terms', '')
        session_data['associated_from'] = request.form.get('associated_from', '')
        session_data['validity'] = request.form.get('validity', '')
        session_data['approved_by'] = request.form.get('approved_by', '')
        session_data['identification'] = request.form.get('identification', '')
        session_data['feedback'] = request.form.get('feedback', '')
        session_data['remarks'] = request.form.get('remarks', '')
        session_data['enquired_part'] = request.form.get('enquired_part', '')
        session_data['visited_date'] = request.form.get('visited_date', '')
        session_data['contact_name'] = request.form.get('contact_name', '')
        session_data['contact_no'] = request.form.get('contact_no', '')
        session_data['contact_email'] = request.form.get('contact_email', '')
        session_data['nda_signed'] = request.form.get('nda_signed', '')
        session_data['detailed_evaluation'] = request.form.get('detailed_evaluation', '')

        image = request.files.get('board_image')
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            session_data['company_image'] = filename
        else:
            session_data['company_image'] = ''
        return redirect('/machine_entry')
    except Exception as e:
        return f"Error in /submit_vendor: {str(e)}"

@app.route('/machine_entry', methods=['GET', 'POST'])
def machine_entry():
    if request.method == 'POST':
        session_data['machine'] = request.form.get('machine', '')
        session_data['size'] = request.form.get('size', '')
        session_data['hour_rate'] = request.form.get('hour_rate', '')

        images = request.files.getlist('machine_images')
        image_filenames = []
        for img in images:
            if img and img.filename:
                filename = secure_filename(img.filename)
                img.save(os.path.join(UPLOAD_FOLDER, filename))
                image_filenames.append(filename)
        session_data['machine_images'] = ', '.join(image_filenames)
        return redirect('/specs_form')
    return render_template('machine_entry.html')

@app.route('/specs_form')
def specs_form():
    return render_template('specs_form.html', machine=session_data.get('machine'), size=session_data.get('size'))

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    try:
        fields = [
            'make', 'model_year', 'type', 'axis_config', 'x_travel', 'y_travel', 'z_travel',
            'a_travel', 'b_travel', 'c_travel', 'max_part_size', 'max_part_height',
            'spindle_taper', 'spindle_power', 'spindle_torque', 'main_spindle_rpm',
            'aux_spindle_rpm', 'max_table_load', 'coolant_pressure', 'pallet_type',
            'tolerance_standard', 'accuracy_xyz', 'accuracy_abc', 'accuracy_table',
            'angle_head', 'controller', 'cad_software', 'cam_software',
            'wire_diameter', 'taper_degree', 'max_cutting_thickness', 'surface_finish',
            'electrode_diameter', 'spindle_stroke', 'table_size', 'sink_size'
        ]
        for field in fields:
            session_data[field] = request.form.get(field, '')

        action = request.form.get('action')
        save_to_excel(session_data.copy())

        if action == 'add':
            return redirect('/machine_entry')
        elif action == 'submit':
            return redirect('/final_submit')
        else:
            return "Unknown action."
    except Exception as e:
        return f"Error in /submit_specs: {str(e)}"

@app.route('/final_submit')
def final_submit():
    return render_template('final_submit.html')

@app.route('/view_responses')
def view_responses():
    try:
        if not os.path.exists(EXCEL_FILE):
            return "<h3>No responses yet.</h3>"
        df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
        return render_template('view_responses.html',
                               tables=[df.to_html(classes='table table-striped', index=False, escape=False)],
                               titles=df.columns.values)
    except Exception as e:
        return f"<h3>Error loading responses: {str(e)}</h3>"

@app.route('/download_excel')
def download_excel():
    return send_from_directory(DATA_FOLDER, 'responses.xlsx', as_attachment=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)












