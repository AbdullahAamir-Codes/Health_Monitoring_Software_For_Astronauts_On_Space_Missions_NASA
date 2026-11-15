from flask import Flask, render_template, redirect, url_for, request
import subprocess
import sys

app = Flask(__name__)

@app.route('/')
def Home():
    return render_template('Home.html')
# -------------------------------------------------------------------
@app.route('/HeartRate')
def HeartRate():
    return render_template('HeartRate.html')

@app.route('/StartHeartRate', methods=['POST'])
def StartHeartRate():

    subprocess.Popen([
        sys.executable,
        "Programs/HeartRateMonitor.py"
    ])

    return redirect(url_for('HeartRate'))
# -------------------------------------------------------------------

@app.route('/BloodSugar', methods=['GET', 'POST'])
def BloodSugar():

    if request.method == 'POST':

        subprocess.Popen([
            sys.executable,
            "Programs/BloodSugar.py"
        ])

        return redirect(url_for('BloodSugar'))

    return render_template('BloodSugar.html')
# -------------------------------------------------------------------

@app.route('/BodyTemperature', methods=['GET', 'POST'])
def BodyTemperature():

    if request.method == 'POST':

        subprocess.Popen([
            sys.executable,
            "Programs/BodyTemps.py"
        ])

        return redirect(url_for('BodyTemperature'))

    return render_template('BodyTemperature.html')
# -------------------------------------------------------------------
@app.route('/BloodPressure', methods=['GET', 'POST'])
def BloodPressure():

    if request.method == 'POST':

        subprocess.Popen([
            sys.executable,
            "Programs/BloodPressure.py"
        ])

        return redirect(url_for('BloodPressure'))

    return render_template('BloodPressure.html')
# -------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)