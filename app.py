from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
from openpyxl import Workbook, load_workbook

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Paths
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
EXCEL_FILE = os.path.join(DATA_FOLDER, 'responses.xlsx')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# Initialize Excel file if not exists
if not os.path.exists(EXCEL_FILE):
    wb = Workbook()
    ws = wb.active
    ws.title = 'Responses'
    headers = [
        'Company Name', 'Vendor Name', 'Address', 'GSTIN', 'Contact Name', 'Phone', 'Email', 'Website',
        'Payment Terms', 'Basis of Approval', 'Associated From', 'Validity of Approval', 'Approved By',
        'Identification', 'Feedback', 'Remarks', 'Enquired Part', 'Visited Date', 'NDA Signed', 'Detailed Evaluation',
        'Machine', 'Size', 'Hour Rate',
        'Make', 'Model/Year', 'Type', 'Axis Configuration', 'X-axis Travel', 'Y-axis Travel', 'Z-axis Travel',
        'A-axis Travel', 'B-axis Travel', 'C-axis Travel', 'Max Part Size', 'Max Part Height', 'Spindle Taper',
        'Spindle Power', 'Spindle Torque', 'Main Spindle Max RPM', 'Aux Spindle Max RPM', 'Max Table Load',
        'Thru Coolant Pressure', 'Pallet type', 'Tolerance Std', 'Accuracy X/Y/Z', 'Accuracy A/B/C',
        'Accuracy Table', 'Angle Head', 'Controller', 'CAD', 'CAM', 'Vendor Image', 'Machine Image'
    ]
    ws.append(headers)
    wb.save(EXCEL_FILE)

@app.route('/')
def vendor_form():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    session['vendor_data'] = {
        'Company Name': request.form.get('company_name'),
        'Vendor Name': request.form.get('vendor_name'),
        'Address': request.form.get('address'),
        'GSTIN': request.form.get('gstin'),
        'Contact Name': request.form.get('contact_name'),
        'Phone': request.form.get('phone'),
        'Email': request.form.get('email'),
        'Website': request.form.get('website'),
        'Payment Terms': request.form.get('payment_terms'),
        'Basis of Approval': request.form.get('basis_of_approval'),
        'Associated From': request.form.get('associated_from'),
        'Validity of Approval': request.form.get('validity_of_approval'),
        'Approved By': request.form.get('approved_by'),
        'Identification': request.form.get('identification'),
        'Feedback': request.form.get('feedback'),
        'Remarks': request.form.get('remarks'),
        'Enquired Part': request.form.get('enquired_part'),
        'Visited Date': request.form.get('visited_date'),
        'NDA Signed': request.form.get('nda_signed'),
        'Detailed Evaluation': request.form.get('detailed_evaluation'),
    }

    image = request.files.get('company_board')
    if image and image.filename:
        filename = secure_filename(image.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)
        session['vendor_data']['Company Board Image'] = image_path
    else:
        session['vendor_data']['Company Board Image'] = ''

    return redirect(url_for('machine_entry'))

@app.route('/machine_entry')
def machine_entry():
    machines = [
        'Vertical Turning Turret', 'Vertical Turning Ram', 'Turning Lathe', 'Turning CNC',
        'Conventional Milling', '3 Axis Vertical Machining Center', '3 Axis Horizontal Machining Center',
        '4 Axis Vertical Machining Center', '4 Axis Horizontal Machining Center', '4 Axis Turn Mill',
        '5 axis Milling', '5 Axis Mill Turn', '5 Axis Turn Mill', 'Surface Grinding',
        'Cylindrical Grinding', 'Spark Erosion Drill', 'Spark Electrical Discharge Machining',
        'Wire Electrical Discharge Machining'
    ]
    sizes = ['S1', 'S2', 'M1', 'M2', 'L1', 'L2']
    return render_template('machine_entry.html', machines=machines, sizes=sizes)

@app.route('/submit_machine', methods=['POST'])
def submit_machine():
    session['machine_data'] = {
        'Machine': request.form.get('machine'),
        'Size': request.form.get('size'),
        'Hour Rate': request.form.get('hour_rate')
    }

    image = request.files.get('machine_image')
    if image and image.filename:
        folder_name = f"{session['machine_data']['Machine']}_{session['machine_data']['Size']}".replace(' ', '_')
        folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        filename = secure_filename(image.filename)
        image_path = os.path.join(folder_path, filename)
        image.save(image_path)
        session['machine_data']['Machine Image'] = image_path
        session['vendor_data']['Company Board Image'] = session['vendor_data'].get('Company Board Image', '')
    else:
        session['machine_data']['Machine Image'] = ''

    return redirect(url_for('specs_form'))

@app.route('/specs_form')
def specs_form():
    return render_template('specs_form.html', machine=session['machine_data']['Machine'], size=session['machine_data']['Size'])

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    specs = {
        'Make': request.form.get('make'),
        'Model/Year': request.form.get('model_year'),
        'Type': request.form.get('type'),
        'Axis Configuration': request.form.get('axis_config'),
        'X-axis Travel': request.form.get('x_travel'),
        'Y-axis Travel': request.form.get('y_travel'),
        'Z-axis Travel': request.form.get('z_travel'),
        'A-axis Travel': request.form.get('a_travel'),
        'B-axis Travel': request.form.get('b_travel'),
        'C-axis Travel': request.form.get('c_travel'),
        'Max Part Size': request.form.get('max_part_size'),
        'Max Part Height': request.form.get('max_part_height'),
        'Spindle Taper': request.form.get('spindle_taper'),
        'Spindle Power': request.form.get('spindle_power'),
        'Spindle Torque': request.form.get('spindle_torque'),
        'Main Spindle Max RPM': request.form.get('main_spindle_rpm'),
        'Aux Spindle Max RPM': request.form.get('aux_spindle_rpm'),
        'Max Table Load': request.form.get('max_table_load'),
        'Thru Coolant Pressure': request.form.get('coolant_pressure'),
        'Pallet type': request.form.get('pallet_type'),
        'Tolerance Std': request.form.get('tolerance_std'),
        'Accuracy X/Y/Z': request.form.get('accuracy_xyz'),
        'Accuracy A/B/C': request.form.get('accuracy_abc'),
        'Accuracy Table': request.form.get('accuracy_table'),
        'Angle Head': request.form.get('angle_head'),
        'Controller': request.form.get('controller'),
        'CAD': request.form.get('cad'),
        'CAM': request.form.get('cam'),
    }

    # Combine all data
    combined = {
        **session['vendor_data'],
        **session['machine_data'],
        **specs
    }

    # Save to Excel
    wb = load_workbook(EXCEL_FILE)
    ws = wb['Responses']
    row = [combined.get(col, '') for col in ws[1]]
    ws.append(row)
    wb.save(EXCEL_FILE)

    return "✅ Submission complete. Data saved to Excel and images stored."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)





