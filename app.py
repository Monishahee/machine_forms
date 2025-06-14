from flask import Flask, render_template, request, redirect, session
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Paths
DATA_FOLDER = 'data'
EXCEL_PATH = os.path.join(DATA_FOLDER, 'responses.xlsx')
os.makedirs(DATA_FOLDER, exist_ok=True)

# Machine & size options
MACHINES = [
    'Vertical Turning Turret', 'Vertical Turning Ram', 'Turning Lathe', 'Turning CNC',
    'Conventional Milling', '3 Axis Vertical Machining Center', '3 Axis Horizontal Machining Center',
    '4 Axis Vertical Machining Center', '4 Axis Horizontal Machining Center', '4 Axis Turn Mill',
    '5 axis Milling', '5 Axis Mill Turn', '5 Axis Turn Mill',
    'Surface Grinding', 'Cylindrical Grinding',
    'Spark Erosion Drill', 'Spark Electrical Discharge Machining', 'Wire Electrical Discharge Machining'
]
SIZES = ['S1[Part Size (<=200)]', 'S2[Part Size (<=500)]', 'M1[Part Size (<=800)]', 'M2[Part Size (<=1000)]', 'L1[Part Size (<=1200)]', 'L2[Part Size (<=1500)]' , 'SP[Part Size (>1500)]' ]

def is_special(machine):
    return machine in [
        'Spark Erosion Drill',
        'Spark Electrical Discharge Machining',
        'Wire Electrical Discharge Machining'
    ]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_customer', methods=['POST'])
def submit_customer():
    session['customer'] = {
        'Company Name': request.form['company'],
        'Vendor Name': request.form['vendor'],
        'Address': request.form['address']
    }
    session['entries'] = []
    return redirect('/machine_form')

@app.route('/machine_form')
def machine_form():
    return render_template('machine_form.html', machines=MACHINES, sizes=SIZES)

@app.route('/submit_machine', methods=['POST'])
def submit_machine():
    session['current'] = {
        'Machine': request.form['machine'],
        'Size': request.form['size'],
        'Rate': request.form['rate'],
        'Quantity': request.form['quantity']
    }
    return redirect('/specs_form')

@app.route('/specs_form')
def specs_form():
    machine = session.get('current', {}).get('Machine', '')
    special = is_special(machine)
    return render_template('specs_form.html', special=special)

@app.route('/submit_specifications', methods=['POST'])
def submit_specifications():
    spec_data = request.form.to_dict()
    entry = {}
    entry.update(session.get('customer', {}))
    entry.update(session.get('current', {}))
    entry.update(spec_data)
    entry['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entries = session.get('entries', [])
    entries.append(entry)
    session['entries'] = entries

    return render_template('entry_submitted.html')

@app.route('/final_submit')
def final_submit():
    entries = session.get('entries', [])
    df = pd.DataFrame(entries)
    if os.path.exists(EXCEL_PATH):
        existing = pd.read_excel(EXCEL_PATH)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_excel(EXCEL_PATH, index=False)
    session.clear()
    return "✅ All entries successfully submitted and saved to Excel."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)










