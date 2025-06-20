from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import os
import pandas as pd
import base64
import requests
from werkzeug.utils import secure_filename
from tinydb import TinyDB
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-very-secret-key' 

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FOLDER'] = 'data'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

EXCEL_FILE = os.path.join(app.config['DATA_FOLDER'], 'responses.xlsx')
TINYDB_FILE = os.path.join(app.config['DATA_FOLDER'], 'responses.json')
db = TinyDB(TINYDB_FILE)
session_data = {}

# Replace this with your deployed Google Apps Script Web App URL
GOOGLE_SCRIPT_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwqMZacuJruJUpX3Kj6okBxdDHuafp5M0OmqhBjhItMGoGhMz1l-hOR7uixKQWfU64y/exec"

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

@app.route('/specs_form', methods=['GET', 'POST'])
def specs_form():
    if request.method == 'POST':
        specs = request.form.to_dict()
        # You can process/store specs here
        flash("✅ Specifications submitted successfully.")
        return redirect(url_for('view_responses'))

    machine = session.get('machine', 'Unknown Machine')
    size = session.get('size', 'Unknown Size')
    return render_template('specs_form.html', machine=machine, size=size)


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
    import pandas as pd
    import os
    from flask import send_from_directory
    from datetime import datetime

    entries = []  # or pull from DB
    # Example fallback if you are not using SQLAlchemy:
    if os.path.exists("data/responses.json"):
        import json
        with open("data/responses.json") as f:
            entries = json.load(f)

    df = pd.DataFrame(entries)
    os.makedirs("data", exist_ok=True)
    out_path = "data/responses.xlsx"
    df.to_excel(out_path, index=False, engine="openpyxl")
    return send_from_directory("data", "responses.xlsx", as_attachment=True)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)

















