from flask import Flask, render_template, request, redirect, url_for
import os
import base64
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

GOOGLE_SCRIPT_WEBAPP_URL = 'https://script.google.com/macros/s/AKfycbwWZhx0c40Bcn-JxuhTGfNlkK4gu0oYUFMMR3q2uwSfAy4BL9BSZLFc5dgQHYHUwvQ/exec'  # Replace this!

# --- Function to Upload to Google Apps Script ---
def upload_to_google_script(data, image_path):
    image_base64 = ""
    image_name = ""

    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode("utf-8")
        image_name = os.path.basename(image_path)

    payload = {
        **data,
        "image_base64": image_base64,
        "image_name": image_name
    }

    try:
        response = requests.post(GOOGLE_SCRIPT_WEBAPP_URL, json=payload)
        print("✅ Google Script Response:", response.text)
    except Exception as e:
        print("❌ Upload failed:", str(e))

# --- Global session temp store ---
session_data = {}

@app.route('/')
def index():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    session_data['company_name'] = request.form.get('company_name', '')
    session_data['vendor_name'] = request.form.get('vendor_name', '')
    session_data['email'] = request.form.get('email', '')
    session_data['phone'] = request.form.get('phone', '')
    session_data['gstin'] = request.form.get('gstin', '')
    session_data['address'] = request.form.get('address', '')
    session_data['contact_name'] = request.form.get('contact_name', '')
    session_data['contact_no'] = request.form.get('contact_no', '')
    session_data['contact_email'] = request.form.get('contact_email', '')
    session_data['website'] = request.form.get('website', '')
    session_data['payment_terms'] = request.form.get('payment_terms', '')

    # Save uploaded image
    image = request.files.get('board_image')
    filename = ''
    if image and image.filename:
        filename = secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER, filename))
    session_data['company_image'] = filename

    return redirect('/machine_entry')

@app.route('/machine_entry', methods=['GET', 'POST'])
def machine_entry():
    if request.method == 'POST':
        session_data['machine'] = request.form.get('machine', '')
        session_data['size'] = request.form.get('size', '')
        session_data['hour_rate'] = request.form.get('hour_rate', '')

        # Save multiple machine images (optional)
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

        # Upload to Google Sheet + Drive
        board_image_path = os.path.join(UPLOAD_FOLDER, session_data.get('company_image', ''))
        upload_to_google_script(session_data, board_image_path)

        action = request.form.get('action')
        if action == 'add':
            return redirect('/machine_entry')
        elif action == 'submit':
            return redirect('/final_submit')
        else:
            return "Invalid action."
    except Exception as e:
        return f"Error in /submit_specs: {str(e)}"

@app.route('/final_submit')
def final_submit():
    return render_template('final_submit.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)














