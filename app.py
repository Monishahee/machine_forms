from flask import Flask, render_template, request, redirect, send_from_directory, url_for
import os
import pandas as pd
from werkzeug.utils import secure_filename
from tinydb import TinyDB

app = Flask(__name__)

# Folder setup
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# DB & Excel file
DB_PATH = os.path.join(DATA_FOLDER, 'responses.json')
EXCEL_FILE = os.path.join(DATA_FOLDER, 'responses.xlsx')
db = TinyDB(DB_PATH)

# Temp storage for multi-step form
session_data = {}

def save_to_excel():
    """Regenerates the Excel from TinyDB data"""
    df = pd.DataFrame(db.all())
    df.to_excel(EXCEL_FILE, index=False)

@app.route('/')
def index():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    try:
        session_data.clear()  # clear for each new submission
        session_data['vendor'] = {
            'company_name': request.form.get('company_name', ''),
            'vendor_name': request.form.get('vendor_name', ''),
            'address': request.form.get('address', ''),
            'email': request.form.get('email', ''),
            'phone': request.form.get('phone', ''),
            'gstin': request.form.get('gstin', ''),
            'website': request.form.get('website', ''),
            'payment_terms': request.form.get('payment_terms', ''),
            'associated_from': request.form.get('associated_from', ''),
            'validity': request.form.get('validity', ''),
            'approved_by': request.form.get('approved_by', ''),
            'identification': request.form.get('identification', ''),
            'feedback': request.form.get('feedback', ''),
            'remarks': request.form.get('remarks', ''),
            'enquired_part': request.form.get('enquired_part', ''),
            'visited_date': request.form.get('visited_date', ''),
            'contact_name': request.form.get('contact_name', ''),
            'contact_no': request.form.get('contact_no', ''),
            'contact_email': request.form.get('contact_email', ''),
            'nda_signed': request.form.get('nda_signed', ''),
            'detailed_evaluation': request.form.get('detailed_evaluation', '')
        }

        image = request.files.get('board_image')
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            session_data['vendor']['company_image'] = filename
        else:
            session_data['vendor']['company_image'] = ''

        return redirect('/machine_entry')
    except Exception as e:
        return f"Error in /submit_vendor: {str(e)}"

@app.route('/machine_entry', methods=['GET', 'POST'])
def machine_entry():
    if request.method == 'POST':
        session_data['machine'] = {
            'machine': request.form.get('machine', ''),
            'size': request.form.get('size', ''),
            'hour_rate': request.form.get('hour_rate', '')
        }

        images = request.files.getlist('machine_images')
        image_filenames = []
        for img in images:
            if img and img.filename:
                filename = secure_filename(img.filename)
                img.save(os.path.join(UPLOAD_FOLDER, filename))
                image_filenames.append(filename)
        session_data['machine']['machine_images'] = ', '.join(image_filenames)

        return redirect('/specs_form')
    return render_template('machine_entry.html')

@app.route('/specs_form')
def specs_form():
    return render_template('specs_form.html',
                           machine=session_data.get('machine', {}).get('machine', ''),
                           size=session_data.get('machine', {}).get('size', ''))

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
        session_data['specs'] = {field: request.form.get(field, '') for field in fields}

        # Merge all subdicts into one
        final_record = {**session_data['vendor'], **session_data['machine'], **session_data['specs']}
        db.insert(final_record)
        save_to_excel()

        action = request.form.get('action')
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

        # Render images if any
        for rec in records:
            if 'company_image' in rec and rec['company_image']:
                rec['company_image'] = f"<img src='/uploads/{rec['company_image']}' width='100'/>"
            if 'machine_images' in rec and rec['machine_images']:
                rec['machine_images'] = '<br>'.join(
                    [f"<img src='/uploads/{img.strip()}' width='100'/>" for img in rec['machine_images'].split(',')]
                )

        df = pd.DataFrame(records)
        return render_template('view_responses.html',
                               tables=[df.to_html(classes='table table-striped', escape=False, index=False)],
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














