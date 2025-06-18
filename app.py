from flask import Flask, render_template, request, redirect, url_for
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# === Google Sheets Setup ===
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("MachineFormResponses").sheet1  # Replace with your sheet name

# === Routes ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/machine_entry', methods=['POST'])
def machine_entry():
    # Get form data
    machine = request.form['machine']
    size = request.form['size']
    hour_rate = request.form['hour_rate']

    # Handle images
    image_urls = []
    for file in request.files.getlist('machine_images'):
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_urls.append(filepath)

    # Save to session or hidden form
    return render_template('specs_form.html', machine=machine, size=size,
                           hour_rate=hour_rate, image_urls=",".join(image_urls))

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    # Gather all form data
    data = {
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
        'Spindle Power': request.form.get('spindle_power'),
        'Controller': request.form.get('controller'),
        # Add more fields as needed...
    }

    # Save to Google Sheets
    sheet.append_row(list(data.values()))

    return render_template('final_submit.html')

@app.route('/view')
def view_responses():
    records = sheet.get_all_records()
    return render_template('view_responses.html', responses=records)










