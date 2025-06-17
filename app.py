from flask import Flask, render_template, request, redirect, url_for, session
import os
import pandas as pd
from werkzeug.utils import secure_filename
from openpyxl import load_workbook

app = Flask(__name__)
app.secret_key = 'secret'

# Upload directories
VENDOR_IMG_DIR = 'uploads/vendor_images'
MACHINE_IMG_DIR = 'uploads/machine_images'
EXCEL_PATH = 'responses.xlsx'

os.makedirs(VENDOR_IMG_DIR, exist_ok=True)
os.makedirs(MACHINE_IMG_DIR, exist_ok=True)

# Ensure Excel has headers
if not os.path.exists(EXCEL_PATH):
    df = pd.DataFrame(columns=[
        "Company Name", "Vendor Name", "Address", "GSTIN", "Contact Name", "Phone",
        "Email", "Website", "Payment Terms", "Basis of Approval", "Associated From",
        "Validity of Approval", "Approved By", "Identification", "Feedback", "Remarks",
        "Enquired Part", "Visited Date", "NDA Signed", "Detailed Evaluation",
        "Vendor Image Path", "Machine", "Size", "Hour Rate", "Machine Image Path",
        "Make", "Model/Year", "Type", "Axis Configuration", "X-axis Travel", "Y-axis Travel", "Z’-axis Travel",
        "A’-axis Travel", "B’-axis Travel", "C’-axis Travel", "Max Part Size", "Max Part Height",
        "Spindle Taper", "Spindle Power", "Spindle Torque", "Main Spindle Max RPM",
        "Aux Spindle Max RPM", "Max Table Load", "Thru Coolant Pressure", "Pallet type",
        "Positional Tolerance Standard", "Positional Accuracy X/Y/Z", "Positional Accuracy A/B/C",
        "Positional Accuracy Table", "Angle Head", "Controller", "CAD Software", "CAM Software",
        "Wire Diameter", "Taper Degree", "Max Cutting Thickness", "Surface Finish (Ra)",
        "Electrode Diameter", "Spindle Stroke", "Table Size", "Sink Size"
    ])
    df.to_excel(EXCEL_PATH, index=False, sheet_name="Responses")

@app.route('/')
def vendor_form():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    session['vendor_data'] = {field: request.form.get(field.replace(' ', '_').lower()) for field in [
        'Company Name', 'Vendor Name', 'Address', 'GSTIN', 'Contact Name', 'Phone', 'Email',
        'Website', 'Payment Terms', 'Basis of Approval', 'Associated From', 'Validity of Approval',
        'Approved By', 'Identification', 'Feedback', 'Remarks', 'Enquired Part',
        'Visited Date', 'NDA Signed', 'Detailed Evaluation'
    ]}

    # Save company board image
    image = request.files.get('company_board')
    if image and image.filename:
        filename = secure_filename(image.filename)
        vendor_image_path = os.path.join(VENDOR_IMG_DIR, filename)
        image.save(vendor_image_path)
        session['vendor_data']['Vendor Image Path'] = vendor_image_path
    else:
        session['vendor_data']['Vendor Image Path'] = ''

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
        filename = secure_filename(image.filename)
        machine_image_path = os.path.join(MACHINE_IMG_DIR, filename)
        image.save(machine_image_path)
        session['machine_data']['Machine Image Path'] = machine_image_path
    else:
        session['machine_data']['Machine Image Path'] = ''

    return redirect(url_for('specs_form'))

@app.route('/specs_form')
def specs_form():
    return render_template('specs_form.html', machine=session.get('machine_data', {}).get('Machine'), size=session.get('machine_data', {}).get('Size'))

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    specs_fields = [
        'Make', 'Model/Year', 'Type', 'Axis Configuration', 'X-axis Travel', 'Y-axis Travel',
        'Z’-axis Travel', 'A’-axis Travel', 'B’-axis Travel', 'C’-axis Travel', 'Max Part Size',
        'Max Part Height', 'Spindle Taper', 'Spindle Power', 'Spindle Torque', 'Main Spindle Max RPM',
        'Aux Spindle Max RPM', 'Max Table Load', 'Thru Coolant Pressure', 'Pallet type',
        'Positional Tolerance Standard', 'Positional Accuracy X/Y/Z', 'Positional Accuracy A/B/C',
        'Positional Accuracy Table', 'Angle Head', 'Controller', 'CAD Software', 'CAM Software',
        'Wire Diameter', 'Taper Degree', 'Max Cutting Thickness', 'Surface Finish (Ra)',
        'Electrode Diameter', 'Spindle Stroke', 'Table Size', 'Sink Size'
    ]

    specs_data = {field: request.form.get(field.replace(' ', '_').lower()) for field in specs_fields}

    full_data = {**session.get('vendor_data', {}), **session.get('machine_data', {}), **specs_data}

    try:
        # Append to Excel
        existing_df = pd.read_excel(EXCEL_PATH, sheet_name="Responses")
        updated_df = pd.concat([existing_df, pd.DataFrame([full_data])], ignore_index=True)
        with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl', mode='w') as writer:
            updated_df.to_excel(writer, index=False, sheet_name="Responses")

        session.clear()
        return "✅ Submission successful! Data saved to Excel."

    except Exception as e:
        return f"❌ Excel Save Error: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)





