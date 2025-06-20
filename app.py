from flask import Flask, render_template, request, redirect, send_from_directory, url_for
import os
import pandas as pd
from werkzeug.utils import secure_filename
from tinydb import TinyDB
db = TinyDB('data/responses.json')  # Static file that survives restarts


app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
EXCEL_FILE = os.path.join(DATA_FOLDER, 'responses.xlsx')
JSON_FILE = os.path.join(DATA_FOLDER, 'responses.json')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

db = TinyDB(JSON_FILE)
session_data = {}

def save_to_excel():
    data = db.all()
    if data:
        df = pd.DataFrame(data)
        df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')

@app.route('/')
def index():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    session_data.clear()  # Clear previous data
    form = request.form

    for field in [
        'company_name', 'vendor_name', 'address', 'email', 'phone', 'gstin',
        'website', 'payment_terms', 'associated_from', 'validity', 'approved_by',
        'identification', 'feedback', 'remarks', 'enquired_part', 'visited_date',
        'contact_name', 'contact_no', 'contact_email', 'nda_signed', 'detailed_evaluation'
    ]:
        session_data[field] = form.get(field, '')

    image = request.files.get('board_image')
    if image and image.filename:
        filename = secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER, filename))
        session_data['company_image'] = filename
    else:
        session_data['company_image'] = ''

    return redirect('/machine_entry')

@app.route('/machine_entry', methods=['GET', 'POST'])
def machine_entry():
    if request.method == 'POST':
        session_data['machine'] = request.form.get('machine', '')
        session_data['size'] = request.form.get('size', '')
        session_data['hour_rate'] = request.form.get('hour_rate', '')

        image_files = request.files.getlist('machine_images')
        image_filenames = []
        for img in image_files:
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

        # Save to TinyDB (static JSON)
        db.insert(session_data.copy())

        # Optional: still save to Excel for downloads
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
        records = db.all()
        if not records:
            return "<h3>No responses yet.</h3>"
        return render_template('view_responses.html', records=records)
    except Exception as e:
        return f"<h3>Error loading responses: {str(e)}</h3>"



@app.route('/download_excel')
def download_excel():
    return send_from_directory(DATA_FOLDER, 'responses.xlsx', as_attachment=True)

@app.route('/download_json')
def download_json():
    return send_from_directory('data', 'responses.json', as_attachment=True)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)













