from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
import pandas as pd
from openpyxl import load_workbook

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
EXCEL_FILE = 'responses.xlsx'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def vendor_form():
    return render_template('vendor_form.html')

@app.route('/submit_vendor', methods=['POST'])
def submit_vendor():
    vendor_data = {
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
        vendor_data['Company Board Image'] = image_path
    else:
        vendor_data['Company Board Image'] = ''

    session['vendor_data'] = vendor_data
    session['machine_entries'] = []

    return redirect(url_for('machine_entry'))

@app.route('/machine_entry')
def machine_entry():
    machines = [
        'Vertical Turning Turret', 'Turning Lathe', '5 Axis Milling', 'Spark Erosion Drill'
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
        machine_folder = os.path.join(UPLOAD_FOLDER, secure_filename(session['selected_machine']))
        os.makedirs(machine_folder, exist_ok=True)
        filename = secure_filename(image.filename)
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
    machine_data = {
        'Machine': session.get('selected_machine'),
        'Size': session.get('selected_size'),
        'Hour Rate': session.get('hour_rate'),
        'Machine Image': session.get('machine_image'),
        'Make': request.form.get('make'),
        'Model/Year': request.form.get('model_year'),
        'Type': request.form.get('type'),
        'Spindle Power': request.form.get('spindle_power'),
        'Controller': request.form.get('controller')
        # Add more fields as needed
    }

    session['machine_entries'].append(machine_data)
    session.modified = True

    if 'add_another' in request.form:
        return redirect(url_for('machine_entry'))
    else:
        return redirect(url_for('final_submit'))

@app.route('/final_submit')
def final_submit():
    vendor_data = session.get('vendor_data', {})
    machine_entries = session.get('machine_entries', [])

    all_data = []

    for machine in machine_entries:
        row = {**vendor_data, **machine}
        all_data.append(row)

    df = pd.DataFrame(all_data)

    if not os.path.exists(EXCEL_FILE):
        df.to_excel(EXCEL_FILE, index=False)
    else:
        existing = pd.read_excel(EXCEL_FILE)
        combined = pd.concat([existing, df], ignore_index=True)
        combined.to_excel(EXCEL_FILE, index=False)

    session.clear()
    return "✅ Data and images saved to Excel and folders successfully!"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)






