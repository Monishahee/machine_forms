from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import os, pandas as pd, base64, requests, json
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

GOOGLE_SCRIPT_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwteB36SfHCJguUaEvUa85G6hjTAMVohlybmNYjvh8uP_ZfPyQoivDoqeblmXYA4IzD/exec"

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

    ordered_fields = [
        'timestamp', 'company_name', 'vendor_name', 'address', 'email', 'phone', 'gstin',
        'website', 'payment_terms', 'associated_from', 'validity', 'approved_by',
        'identification', 'feedback', 'remarks', 'enquired_part', 'visited_date',
        'contact_name', 'contact_no', 'contact_email', 'nda_signed', 'detailed_evaluation',
        'machine', 'size', 'hour_rate', 'machine_images',
        'make', 'model_year', 'type', 'axis_config', 'x_travel', 'y_travel', 'z_travel',
        'a_travel', 'b_travel', 'c_travel', 'max_part_size', 'max_part_height',
        'spindle_taper', 'spindle_power', 'spindle_torque', 'main_spindle_rpm',
        'aux_spindle_rpm', 'max_table_load', 'coolant_pressure', 'pallet_type',
         'accuracy_xyz', 'accuracy_abc', 'accuracy_table',
        'angle_head', 'controller', 'cad_software', 'cam_software',
        'wire_diameter', 'taper_degree', 'max_cutting_thickness', 'surface_finish',
        'electrode_diameter', 'spindle_stroke', 'table_size', 'sink_size',
        'company_image'
    ]

    all_data = db.all()
    df = pd.DataFrame(all_data)

    # Ensure all ordered fields exist
    for field in ordered_fields:
        if field not in df.columns:
            df[field] = ''

    # Reorder and save
    df = df[ordered_fields]
    df.to_excel(EXCEL_FILE, index=False)

@app.route('/')
def index():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    try:
        for field in request.form:
            session[field] = request.form.get(field, '')
        image = request.files.get('board_image')
        if image and image.filename:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            session['company_image'] = filename
        else:
            session['company_image'] = ''
        return redirect('/machine_entry')
    except Exception as e:
        return f"Error in /submit_vendor: {str(e)}"

@app.route('/machine_entry', methods=['GET', 'POST'])
def machine_entry():
    try:
        if request.method == 'POST':
            session['machine'] = request.form.get('machine', '')
            session['size'] = request.form.get('size', '')
            session['hour_rate'] = request.form.get('hour_rate', '')

            images = request.files.getlist('machine_images')
            image_names = []
            for img in images:
                if img and img.filename:
                    filename = secure_filename(img.filename)
                    img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_names.append(filename)
            session['machine_images'] = ', '.join(image_names)
            return redirect('/specs_form')
        return render_template('machine_entry.html')
    except Exception as e:
        return f"Error in /machine_entry: {str(e)}"

@app.route('/specs_form', methods=['GET'])
def specs_form():
    try:
        machine = session.get('machine', 'Unknown Machine')
        size = session.get('size', 'Unknown Size')
        return render_template('specs_form.html', machine=machine, size=size)
    except Exception as e:
        return f"Error in /specs_form: {str(e)}"

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
            session[field] = request.form.get(field, '')
        session['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        full_data = dict(session)
        save_to_local(full_data)

        if full_data.get('company_image'):
            upload_to_google_script(full_data, os.path.join(app.config['UPLOAD_FOLDER'], full_data['company_image']))

        if request.form.get('action') == 'add':
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

        display_order = [
            'timestamp', 'company_name', 'vendor_name', 'address', 'email', 'phone', 'gstin',
            'website', 'payment_terms', 'associated_from', 'validity', 'approved_by',
            'identification', 'feedback', 'remarks', 'enquired_part', 'visited_date',
            'contact_name', 'contact_no', 'contact_email', 'nda_signed', 'detailed_evaluation',
            'machine', 'size', 'hour_rate', 'machine_images',
            'make', 'model_year', 'type', 'axis_config', 'x_travel', 'y_travel', 'z_travel',
            'a_travel', 'b_travel', 'c_travel', 'max_part_size', 'max_part_height',
            'spindle_taper', 'spindle_power', 'spindle_torque', 'main_spindle_rpm',
            'aux_spindle_rpm', 'max_table_load', 'coolant_pressure', 'pallet_type',
            'tolerance_standard', 'accuracy_xyz', 'accuracy_abc', 'accuracy_table',
            'angle_head', 'controller', 'cad_software', 'cam_software',
            'wire_diameter', 'taper_degree', 'max_cutting_thickness', 'surface_finish',
            'electrode_diameter', 'spindle_stroke', 'table_size', 'sink_size',
            'company_image'
        ]

        df = pd.DataFrame(records)
        for field in display_order:
            if field not in df.columns:
                df[field] = ''
        df = df[display_order]

        return render_template("view_responses.html", records=df.to_dict(orient='records'), headers=display_order)
    except Exception as e:
        return f"Error loading responses: {str(e)}"


@app.route('/download_excel')
def download_excel():
    if os.path.exists(EXCEL_FILE):
        return send_from_directory(app.config['DATA_FOLDER'], 'responses.xlsx', as_attachment=True)
    return "Excel file not found."

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)

















