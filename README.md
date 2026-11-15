# 🚀 Astro Health – Astronaut Health Monitoring System

> **Platform:** Windows (PowerShell)

## Overview

**Astro Health** is a health monitoring software project designed to help monitor astronauts' vital health indicators during space missions. Space environments, particularly microgravity, can affect the human body, making continuous health monitoring important for astronaut safety and wellbeing.

The project provides an accessible dashboard where health measurements can be monitored, analysed and displayed, helping identify unusual changes that may require further medical attention.

## 🎯 Project Objectives

- Monitor astronauts' vital health indicators.
- Display health measurements through a user-friendly dashboard.
- Identify readings that fall outside selected monitoring ranges.
- Provide health information to support astronaut wellbeing during space missions.
- Explore how software and sensor technology can support healthcare in space.

## ✨ Features

Astro Health includes the following monitoring sections:

- **Blood Pressure:** Monitor systolic and diastolic blood pressure readings.
- **Heart Rate:** Measure and display heart rate in beats per minute (BPM).
- **Blood Sugar:** Monitor glucose levels and identify low, elevated or high readings.
- **Body Temperature:** Display body temperature measurements.
- **Health Dashboard:** Present health information in an organised and accessible interface.

Additional features may include:

- Real-time data updates.
- Health readings and historical records.
- Graphs and visual representations of health measurements.
- Alerts for unusual readings.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language and application logic |
| Flask | Backend framework and routing |
| HTML5 | Webpage structure |
| CSS3 | Styling and responsive design |
| JavaScript | Interactive webpage functionality |
| Bootstrap | User interface components and layout |
| NumPy | Numerical calculations and data processing |
| OpenCV | Camera-based image processing and experimentation |
| SciPy | Signal processing and analysis |

## 💻 Requirements

- **Windows 10 or Windows 11**
- **Python 3.9 or newer** – download from [python.org](https://www.python.org/downloads/windows/) and tick **"Add Python to PATH"** during installation
- **Git** – download from [git-scm.com](https://git-scm.com/download/win)
- **PowerShell** (included with Windows)

To check that Python and Git are installed, open PowerShell and run:

```powershell
python --version
git --version
```

## ⚙️ Installation and Setup

All commands below are run in **PowerShell**.

### 1. Clone the repository

```powershell
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the project folder

Cloning creates a folder named after the repository. Move into it:

```powershell
cd YOUR_REPOSITORY_FOLDER_NAME
```

> Already have the project on your computer (for example, you downloaded it or created the repository locally)? Skip steps 1 and 2 and simply open PowerShell in the project folder, the one that contains `app.py`.

### 3. Create a virtual environment

```powershell
python -m venv venv
```

### 4. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

When the environment is active, you will see `(venv)` at the start of your PowerShell prompt.

> **Getting a "running scripts is disabled on this system" error?**
> Allow scripts for the current PowerShell session only, then activate again:
>
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\venv\Scripts\Activate.ps1
> ```

### 5. Install dependencies

```powershell
pip install -r requirements.txt
```

If you do not have a `requirements.txt` file yet, install the necessary packages individually:

```powershell
pip install flask numpy scipy opencv-python
```

### 6. Run the application

```powershell
python app.py
```

### 7. Open the application

Visit the following address in your browser:

```text
http://127.0.0.1:5000/
```

To stop the application, press `Ctrl + C` in the PowerShell window.

## ▶️ Running the App Again Later

Each time you come back to the project, open PowerShell and run:

```powershell
cd YOUR_REPOSITORY_FOLDER_NAME
.\venv\Scripts\Activate.ps1
python app.py
```

To leave the virtual environment when you are finished:

```powershell
deactivate
```

## 🔬 How It Works

Astro Health uses a Python-based backend to process health measurements and a Flask web application to display information through a browser.

The application follows this general process:

1. Health measurements are collected or entered into the system.
2. Python processes and analyses the collected readings.
3. The system compares measurements against selected monitoring ranges.
4. Results are displayed on the relevant health monitoring webpage.
5. Unusual measurements can be highlighted to support further assessment.

The system is designed to allow future integration with wearable health sensors and other monitoring devices.

## 🌌 Project Innovation

Astro Health focuses on the challenges of monitoring human health in space. Astronauts experience physiological changes during spaceflight, particularly due to microgravity.

By combining software development, health data processing and interactive visualisation, the project explores how digital health monitoring could support astronaut safety during long-duration missions.

The modular design also allows additional monitoring features and sensor integrations to be developed in the future.

## 🚀 Future Improvements

- Integrate real wearable health-monitoring sensors.
- Implement continuous health data collection.
- Add interactive graphs showing historical readings.
- Introduce personalised health monitoring thresholds.
- Develop automated notifications for unusual measurements.
- Improve data storage and health record management.
- Explore secure transmission of astronaut health information.

## ⚠️ Disclaimer

Astro Health is an educational and development project. Unless connected to validated medical-grade sensors and clinically verified software, readings and classifications should be treated as demonstrations rather than medical measurements or diagnoses. The application is not intended to replace professional medical advice.

## 👨‍💻 Development

Developed as a software project exploring astronaut health monitoring and the application of technology to healthcare during space missions.

**Project Name:** Astro Health
**Main Language:** Python
**Framework:** Flask
**Interface:** HTML, CSS and JavaScript
**Platform:** Windows

---

*Building technology to support healthier and safer space exploration. 🚀*
