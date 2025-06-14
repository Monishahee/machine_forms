from flask import Flask, render_template, request, redirect, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'macreq_secret_key'

# Create data folder if not exists
if not os.path.exists('data'):
    os.makedirs('data')

excel_file = 'data/responses.xlsx'

# Special spec machines
SPECIAL = ['Spark Erosion Drill', 'Spark Electrical Discharge Machining', 'Wire Electrical Discharge Machining']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_customer', methods=['POST'])
def set_customer():
    session['customer'] = {
        'company': request.form['company'],
        'vendor': request.form['vendor'],
        'address': request.form['address']
    }
    return redirect('/specs_form')

@app.route('/specs_form')
def specs_form():
    if 'customer' not in session:
        return redirect('/')
    return render_template('specs_form.html', machine="", size="", special=False)

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    cust = session.get('customer', {})
    machine = request.form.get('machine', '')
    size = request.form.get('size', '')
    rate = request.form.get('rate', '')

    specs = request.form.to_dict()
    specs.pop('rate', None)  # remove rate from specs, it's added separately

    row_data = {
        'Company Name': cust.get('company', ''),
        'Vendor Name': cust.get('vendor', ''),
        'Address': cust.get('address', ''),
        'Machine': machine,
        'Size': size,
        'Rate per Hour': rate
    }
    row_data.update(specs)

    # Save to Excel
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
        df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
    else:
        df = pd.DataFrame([row_data])

    df.to_excel(excel_file, index=False)

    return redirect('/specs_form')

@app.route('/success')
def success():
    session.clear()
    return "✅ All machine entries saved successfully. Thank you!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)












