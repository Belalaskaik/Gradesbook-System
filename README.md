# Gradesbook System

A GUI-based gradebook system built using PyQt5 and pandas. This application allows users to manage student grades, compute weighted averages, and assign letter grades. The application was developed using Python 3.11.5.

## Features
- Import and export student data from and to CSV files.
- Add and delete student records.
- Compute weighted averages for student grades.
- Assign letter grades based on weighted averages.
- Search for students by their SID or task.

## Installation
1. Ensure you have Python 3.11.5 installed. If not, download and install it from the [official Python website](https://www.python.org/downloads/).
2. Install `pipenv` if you haven't already:
```bash
 pip install pipenv
```
4. Clone the repository:
```bash
git clone https://github.com/Belalaskaik/Gradesbook-System.git
```
4. Navigate to the repository directory:

```bash
cd Gradesbook-System
```

5. Install the required packages using `pipenv`:
```bash
pipenv install -r requirements.txt
```
6. Activate the virtual environment:
```bash
pipenv shell
```
7. Run the application:
```bash
python dgui.py
```
## Usage
- Use the "Import CSV" button to load student data from a CSV file.
- Use the "Export CSV" button to save student data to a CSV file.
- Use the "Add Student" button to add a new student record.
- Use the "Delete Student" button to remove a selected student record.
- Search for students by their SID or task using the provided search fields.
