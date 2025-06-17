from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
app.secret_key = 'secretkey'

UPLOAD_FOLDER = 'uploads'
EXCEL_FILE = 'responses.xlsx'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Excel if not exists
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame()
    df.to_excel(EXCEL_FILE, index=False)

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
        'Contact No': request.form.get('contact_no'),
        'Mail Id': request.form.get('mail_id'),
        'Website': request.form.get('website'),
        'Payment Terms': request.form.get('payment_terms'),
        'Basis of Approval': request.form.get('basis_of_approval'),
        'Associated from': request.form.get('associated_from'),
        'Validity of Approval': request.form.get('validity_of_approval'),
        'Approved by': request.form.get('approved_by'),
        'Identification': request.form.get('identification'),
        'Feedback': request.form.get('feedback'),
        'Remarks': request.form.get('remarks'),
        'Enquired Part': request.form.get('enquired_part'),
        'Visited date': request.form.get('visited_date'),
        'NDA Signed': request.form.get('nda_signed'),
        'Detailed Evaluation': request.form.get('detailed_evaluation'),
    }
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
    session['current_machine'] = {
        'Machine': request.form.get('machine'),
        'Size': request.form.get('size'),
        'Hour Rate': request.form.get('hour_rate'),
        'Image': ''
    }

    image = request.files.get('machine_image')
    if image and image.filename:
        machine_folder = os.path.join(UPLOAD_FOLDER, secure_filename(session['current_machine']['Machine']))
        os.makedirs(machine_folder, exist_ok=True)
        filename = secure_filename(image.filename)
        filepath = os.path.join(machine_folder, filename)
        image.save(filepath)
        session['current_machine']['Image'] = filepath

    return redirect(url_for('specs_form'))

@app.route('/specs_form')
def specs_form():
    return render_template('specs_form.html', machine=session['current_machine']['Machine'], size=session['current_machine']['Size'])

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    specs = {
        'Make': request.form.get('make'),
        'Model/Year': request.form.get('model_year'),
        'Type': request.form.get('type'),
        'Axis Configuration': request.form.get('axis_config'),
        'Spindle Power': request.form.get('spindle_power'),
        'Controller': request.form.get('controller')
    }

    machine_full = {**session['current_machine'], **specs}
    session['machine_entries'].append(machine_full)

    if 'add_another' in request.form:
        return redirect(url_for('machine_entry'))
    else:
        return redirect(url_for('final_submit'))

@app.route('/final_submit')
def final_submit():
    vendor_data = session.get('vendor_data', {})
    machines = session.get('machine_entries', [])

    all_rows = []
    for m in machines:
        combined = {**vendor_data, **m}
        all_rows.append(combined)

    df_new = pd.DataFrame(all_rows)

    if os.path.exists(EXCEL_FILE):
        df_old = pd.read_excel(EXCEL_FILE)
        final_df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        final_df = df_new

    final_df.to_excel(EXCEL_FILE, index=False)

    session.clear()
    return "✅ Data and images saved successfully."

# For Render/Railway
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)







