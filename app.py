from flask import Flask, render_template, request, redirect, url_for
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from werkzeug.utils import secure_filename

# ===== Flask App Setup =====
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===== Google Sheets Setup =====
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)

# Open the target Google Sheet
sheet = client.open("MachineFormResponses").sheet1  # Must match your sheet name

# ===== ROUTES =====

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/machine_entry', methods=['POST'])
def machine_entry():
    machine = request.form.get('machine')
    size = request.form.get('size')
    hour_rate = request.form.get('hour_rate')

    # Handle multiple images
    image_urls = []
    for file in request.files.getlist('machine_images'):
        if file and file.filename:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            image_urls.append(path)

    return render_template('specs_form.html',
                           machine=machine,
                           size=size,
                           hour_rate=hour_rate,
                           image_urls=",".join(image_urls))

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    # Collect all form fields (basic + specifications)
    data = {
        'Company Name': request.form.get('company_name'),
        'Vendor Manager': request.form.get('vendor_name'),
        'Address': request.form.get('address'),
        'Email': request.form.get('email'),
        'Phone': request.form.get('phone'),
        'GSTIN': request.form.get('gstin'),
        'Contact Name': request.form.get('contact_name'),
        'Contact No': request.form.get('contact_no'),
        'Mail Id': request.form.get('mail_id'),
        'Website': request.form.get('website'),
        'Payment Terms': request.form.get('payment_terms'),
        'Machine': request.form.get('machine'),
        'Size': request.form.get('size'),
        'Hour Rate': request.form.get('hour_rate'),
        'Make': request.form.get('make'),
        'Model/Year': request.form.get('model_year'),
        'Type': request.form.get('type'),
        'Axis Config': request.form.get('axis_config'),
        'X Travel': request.form.get('x_travel'),
        'Y Travel': request.form.get('y_travel'),
        'Z Travel': request.form.get('z_travel'),
        'A Travel': request.form.get('a_travel'),
        'B Travel': request.form.get('b_travel'),
        'C Travel': request.form.get('c_travel'),
        'Max Part Size': request.form.get('max_part_size'),
        'Max Part Height': request.form.get('max_part_height'),
        'Spindle Taper': request.form.get('spindle_taper'),
        'Spindle Power': request.form.get('spindle_power'),
        'Spindle Torque': request.form.get('spindle_torque'),
        'Main Spindle RPM': request.form.get('main_spindle_rpm'),
        'Aux Spindle RPM': request.form.get('aux_spindle_rpm'),
        'Tool Changer': request.form.get('tool_changer'),
        'Tool Capacity': request.form.get('tool_capacity'),
        'Tool Holder': request.form.get('tool_holder'),
        'Controller': request.form.get('controller'),
        'Cycle Time (min)': request.form.get('cycle_time'),
        'Accuracy (microns)': request.form.get('accuracy'),
        'Material Machined': request.form.get('material_machined'),
        'CAD/CAM Software': request.form.get('cadcam'),
        'Coolant Type': request.form.get('coolant'),
        'Inspection Equipment': request.form.get('inspection_equipment'),
        'Image URLs': request.form.get('image_urls')  # Comma-separated
    }

    # Save to Google Sheet
    sheet.append_row(list(data.values()))

    return render_template('final_submit.html')

@app.route('/view')
def view_responses():
    records = sheet.get_all_records()
    return render_template('view_responses.html', responses=records)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)












