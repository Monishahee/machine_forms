from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
from openpyxl import Workbook, load_workbook

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Create folders
UPLOAD_FOLDER = 'uploads'
EXCEL_FILE = 'data/responses.xlsx'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)

# Create Excel file if not exists
if not os.path.exists(EXCEL_FILE):
    wb = Workbook()
    ws = wb.active
    ws.title = "Responses"
    headers = [
        "Company Name", "Vendor Name", "Address", "GSTIN", "Contact Name", "Phone", "Email", "Website",
        "Payment Terms", "Basis of Approval", "Associated From", "Validity of Approval", "Approved By",
        "Identification", "Feedback", "Remarks", "Enquired Part", "Visited Date", "NDA Signed", "Detailed Evaluation",
        "Company Board Image", "Machine", "Size", "Hour Rate", "Machine Image", "Make", "Model/Year", "Type",
        "Axis Config", "X Travel", "Y Travel", "Z Travel", "A Travel", "B Travel", "C Travel", "Max Part Size",
        "Max Part Height", "Spindle Taper", "Spindle Power", "Spindle Torque", "Main Spindle RPM", "Aux Spindle RPM",
        "Max Table Load", "Coolant Pressure", "Pallet Type", "Tolerance Std", "Accuracy XYZ", "Accuracy ABC",
        "Accuracy Table", "Angle Head", "Controller", "CAD", "CAM",
        "Wire Diameter", "Taper Deg", "Cutting Thickness", "Surface Finish", "Electrode Dia", "Spindle Stroke",
        "Table Size", "Sink Size"
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
        image_path = os.path.join(UPLOAD_FOLDER, 'vendor_' + filename)
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
    session['selected_machine'] = request.form.get('machine')
    session['selected_size'] = request.form.get('size')
    session['hour_rate'] = request.form.get('hour_rate')

    image = request.files.get('machine_image')
    if image and image.filename:
        filename = secure_filename(image.filename)
        machine_folder = os.path.join(UPLOAD_FOLDER, session['selected_machine'].replace(' ', '_'))
        os.makedirs(machine_folder, exist_ok=True)
        image_path = os.path.join(machine_folder, filename)
        image.save(image_path)
        session['machine_image'] = image_path
    else:
        session['machine_image'] = ''

    return redirect(url_for('specs_form'))

@app.route('/specs_form')
def specs_form():
    return render_template('specs_form.html', machine=session.get('selected_machine'), size=session.get('selected_size'))

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    data = {**session.get('vendor_data', {})}

    machine_data = {
        'Machine': session.get('selected_machine'),
        'Size': session.get('selected_size'),
        'Hour Rate': session.get('hour_rate'),
        'Machine Image': session.get('machine_image'),
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
        'Max Table Load': request.form.get('max_table_load'),
        'Coolant Pressure': request.form.get('coolant_pressure'),
        'Pallet Type': request.form.get('pallet_type'),
        'Tolerance Std': request.form.get('tolerance_std'),
        'Accuracy XYZ': request.form.get('accuracy_xyz'),
        'Accuracy ABC': request.form.get('accuracy_abc'),
        'Accuracy Table': request.form.get('accuracy_table'),
        'Angle Head': request.form.get('angle_head'),
        'Controller': request.form.get('controller'),
        'CAD': request.form.get('cad'),
        'CAM': request.form.get('cam'),
    }

    if session.get('selected_machine') in [
        'Spark Erosion Drill', 'Spark Electrical Discharge Machining', 'Wire Electrical Discharge Machining'
    ]:
        machine_data.update({
            'Wire Diameter': request.form.get('wire_dia'),
            'Taper Deg': request.form.get('taper_deg'),
            'Cutting Thickness': request.form.get('cutting_thickness'),
            'Surface Finish': request.form.get('surface_finish'),
            'Electrode Dia': request.form.get('electrode_dia'),
            'Spindle Stroke': request.form.get('spindle_stroke'),
            'Table Size': request.form.get('table_size'),
            'Sink Size': request.form.get('sink_size'),
        })

    data.update(machine_data)

    try:
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
        row = [data.get(h, '') for h in ws[1]]
        ws.append(row)
        wb.save(EXCEL_FILE)
    except Exception as e:
        return f"❌ Error writing to Excel: {str(e)}", 500

    session.clear()
    return "✅ Submitted! All data saved to Excel + images saved."

if __name__ == '__main__':
    app.run(debug=True)




