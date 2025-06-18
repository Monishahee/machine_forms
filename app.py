from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
EXCEL_FILE = 'data/responses.xlsx'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)

# Excel init
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["Company Name", "Vendor Name", "Address", "Machine", "Size", "Hour Rate", "Image Path", "Specs", "Timestamp"])
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
    }
    session['machine_entries'] = []
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
    image_path = ''

    if image and image.filename:
        folder_name = f"{session['selected_machine'].replace(' ', '_')}_{session['selected_size']}"
        save_dir = os.path.join(UPLOAD_FOLDER, folder_name)
        os.makedirs(save_dir, exist_ok=True)

        filename = secure_filename(image.filename)
        image_path = os.path.join(save_dir, filename)
        image.save(image_path)

    session['machine_image'] = image_path
    return redirect(url_for('specs_form'))

@app.route('/specs_form')
def specs_form():
    return render_template(
        'specs_form.html',
        machine=session.get('selected_machine'),
        size=session.get('selected_size')
    )

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    spec_fields = request.form.to_dict()
    machine_data = {
        'Machine': session.get('selected_machine'),
        'Size': session.get('selected_size'),
        'Hour Rate': session.get('hour_rate'),
        'Image Path': session.get('machine_image'),
        'Specs': spec_fields
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

    if not machine_entries:
        return "❌ No machines submitted.", 400

    rows = []
    for entry in machine_entries:
        row = {
            "Company Name": vendor_data.get('Company Name'),
            "Vendor Name": vendor_data.get('Vendor Name'),
            "Address": vendor_data.get('Address'),
            "Machine": entry['Machine'],
            "Size": entry['Size'],
            "Hour Rate": entry['Hour Rate'],
            "Image Path": entry['Image Path'],
            "Specs": json.dumps(entry['Specs']),
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        rows.append(row)

    df_existing = pd.read_excel(EXCEL_FILE)
    df_new = pd.DataFrame(rows)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    df_combined.to_excel(EXCEL_FILE, index=False)

    session.clear()
    return "✅ Submission successful. Data and images saved to Excel and folders."
    if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)









