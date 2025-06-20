from flask import Flask, render_template, request, redirect, send_from_directory
import os
import pandas as pd
import base64
import requests
from werkzeug.utils import secure_filename
from tinydb import TinyDB
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FOLDER'] = 'data'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

EXCEL_FILE = os.path.join(app.config['DATA_FOLDER'], 'responses.xlsx')
TINYDB_FILE = os.path.join(app.config['DATA_FOLDER'], 'responses.json')
db = TinyDB(TINYDB_FILE)
session_data = {}

# Replace this with your deployed Google Apps Script Web App URL
GOOGLE_SCRIPT_WEB_APP_URL = ""

def upload_to_google_script(data, image_path):
    try:
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")
        payload = {
            **data,
            "image_base64": image_base64,
            "image_name": os.path.basename(image_path)
        }
        response = requests.post(GOOGLE_SCRIPT_WEB_APP_URL, json=payload)
        print("Google Upload Response:", response.text)
    except Exception as e:
        print("Google Upload Error:", str(e))

def save_to_local(data):
    db.insert(data)
    df = pd.DataFrame(db.all())
    df.to_excel(EXCEL_FILE, index=False)

@app.route('/')
def index():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    try:
        form = request.form
        session_data.update({
            'company_name': form.get('company_name', ''),
            'vendor_name': form.get('vendor_name', ''),
            'address': form.get('address', ''),
            'email': form.get('email', ''),
            'phone': form.get('phone', ''),
            'gstin': form.get('gstin', ''),
            'website': form.get('website', ''),
            'payment_terms': form.get('payment_terms', ''),
            'associated_from': form.get('associated_from', ''),
            'validity': form.get('validity', ''),
            'approved_by': form.get('approved_by', ''),
            'identification': form.get('identification', ''),
            'feedback': form.get('feedback', ''),
            'remarks': form.get('remarks', ''),
            'enquired_part': form.get('enquired_part', ''),
            'visited_date': form.get('visited_date', ''),
            'contact_name': form.get('contact_name', ''),
            'contact_no': form.get('contact_no', ''),
            'contact_email': form.get('contact_email', ''),
            'nda_signed': form.get('nda_signed', ''),
            'detailed_evaluation': form.get('detailed_evaluation', '')
        })

        image = request.files.get('board_image')
        if image and image.filename:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            session_data['company_image'] = filename
        else:
            session_data['company_image'] = ''

        return redirect('/machine_entry')
    except Exception as e:
        return f"Error in /submit_vendor: {str(e)}"

@app.route('/machine_entry', methods=['GET', 'POST'])
def machine_entry():
    try:
        if request.method == 'POST':
            session_data['machine'] = request.form.get('machine', '')
            session_data['size'] = request.form.get('size', '')
            session_data['hour_rate'] = request.form.get('hour_rate', '')

            images = request.files.getlist('machine_images')
            image_names = []
            for img in images:
                if img and img.filename:
                    filename = secure_filename(img.filename)
                    img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_names.append(filename)
            session_data['machine_images'] = ', '.join(image_names)

            return redirect('/specs_form')

        return render_template('machine_entry.html')
    except Exception as e:
        return f"Error in /machine_entry: {str(e)}"

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

        session_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Save locally
        save_to_local(session_data.copy())

        # Send to Google Apps Script
        if session_data.get('company_image'):
            upload_to_google_script(session_data.copy(), os.path.join(app.config['UPLOAD_FOLDER'], session_data['company_image']))

        action = request.form.get('action')
        if action == 'add':
            return redirect('/machine_entry')
        return redirect('/final_submit')
    except Exception as e:
        return f"Error in /submit_specs: {str(e)}"

@app.route('/final_submit')
def final_submit():
    return render_template('final_submit.html')

@app.route('/view_responses')
def view_responses():
    try:
        records = db.all()
        return render_template("view_responses.html", records=records)
    except Exception as e:
        return f"Error loading responses: {str(e)}"

@app.route('/download_excel')
def download_excel():
    try:
        return send_from_directory(app.config['DATA_FOLDER'], 'responses.xlsx', as_attachment=True)
    except Exception as e:
        return f"Download Error: {str(e)}"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)

















