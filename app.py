from flask import Flask, render_template, request, redirect, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'macreqsecret'

DATA_FILE = 'data/responses.xlsx'

if not os.path.exists('data'):
    os.makedirs('data')

@app.route('/')
def index():
    machine_list = [
        "Vertical Turning Turret", "Vertical Turning Ram", "Turning Lathe", "Turning CNC",
        "Conventional Milling", "3 Axis Vertical Machining Center", "3 Axis Horizontal Machining Center",
        "4 Axis Vertical Machining Center", "4 Axis Horizontal Machining Center", "4 Axis Turn Mill",
        "5 axis Milling", "5 Axis Mill Turn", "5 Axis Turn Mill", "Surface Grinding", "Cylindrical Grinding",
        "Spark Erosion Drill", "Spark Electrical Discharge Machining", "Wire Electrical Discharge Machining"
    ]
    return render_template("index.html", machine_list=machine_list)

@app.route('/add_machine', methods=['POST'])
def add_machine():
    if not session.get('customer_details_filled'):
        session['company'] = request.form['company']
        session['vendor'] = request.form['vendor']
        session['address'] = request.form['address']
        session['customer_details_filled'] = True

    machine_name = request.form['machine_name']
    machine_size = request.form['machine_size']
    session['current_machine'] = machine_name
    session['current_size'] = machine_size

    return render_template("specs_form.html", machine_name=machine_name, machine_size=machine_size)

@app.route('/submit_specs', methods=['POST'])
def submit_specs():
    entry = {
        "Company": session['company'],
        "Vendor": session['vendor'],
        "Address": session['address'],
        "Machine Name": session['current_machine'],
        "Machine Size": session['current_size'],
        "Quantity": request.form.get("quantity"),
        "Rate": request.form.get("rate"),
        "Make": request.form.get("make"),
        "Model/Year": request.form.get("model_year"),
        "Type": request.form.get("type"),
        "Axis Config": request.form.get("axis_config"),
        "X Travel": request.form.get("x_travel"),
        "Y Travel": request.form.get("y_travel"),
        "Z Travel": request.form.get("z_travel"),
        "A Travel": request.form.get("a_travel"),
        "B Travel": request.form.get("b_travel"),
        "C Travel": request.form.get("c_travel"),
        "Max Part Dia": request.form.get("max_part_dia"),
        "Max Part Height": request.form.get("max_part_height"),
        "Spindle Taper": request.form.get("spindle_taper"),
        "Spindle Power": request.form.get("spindle_power"),
        "Spindle Torque": request.form.get("spindle_torque"),
        "Main Spindle RPM": request.form.get("main_spindle_rpm"),
        "Aux Spindle RPM": request.form.get("aux_spindle_rpm"),
        "Max Table Load": request.form.get("max_table_load"),
        "Coolant Pressure": request.form.get("coolant_pressure"),
        "Pallet Type": request.form.get("pallet_type"),
        "Tolerance Standard": request.form.get("tolerance_standard"),
        "Accuracy XYZ": request.form.get("accuracy_xyz"),
        "Accuracy ABC": request.form.get("accuracy_abc"),
        "Accuracy Table": request.form.get("accuracy_table"),
        "Angle Head": request.form.get("angle_head"),
        "Controller": request.form.get("controller"),
        "CAD Software": request.form.get("cad_software"),
        "CAM Software": request.form.get("cam_software"),
    }

    # Add special specs only for 3 machines
    if session['current_machine'] in ["Spark Erosion Drill", "Spark Electrical Discharge Machining", "Wire Electrical Discharge Machining"]:
        entry.update({
            "Wire Diameter": request.form.get("wire_diameter"),
            "Taper Degree": request.form.get("taper_degree"),
            "Max Cutting Thickness": request.form.get("max_cut_thickness"),
            "Surface Finish (Ra)": request.form.get("surface_finish"),
            "Electrode Diameter": request.form.get("electrode_diameter"),
            "Spindle Stroke": request.form.get("spindle_stroke"),
            "Table Size": request.form.get("table_size"),
            "Sink Size": request.form.get("sink_size"),
        })

    if not session.get('entries'):
        session['entries'] = []

    session['entries'].append(entry)
    session.modified = True

    return redirect('/')

@app.route('/submit_all', methods=['POST'])
def submit_all():
    if session.get('entries'):
        df = pd.DataFrame(session['entries'])
        if os.path.exists(DATA_FILE):
            df_existing = pd.read_excel(DATA_FILE)
            df = pd.concat([df_existing, df], ignore_index=True)
        df.to_excel(DATA_FILE, index=False)
        session.clear()
    return "<h2>✅ All machine entries submitted successfully and saved to Excel.</h2><a href='/'>Back to Home</a>"

if __name__ == '__main__':
    app.run(debug=True)
