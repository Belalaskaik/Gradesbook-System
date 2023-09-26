import numpy as np
import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QTableView, QVBoxLayout, QPushButton,
                             QFileDialog, QWidget, QLineEdit, QLabel, QInputDialog,
                             QAbstractItemView, QMessageBox)
from PyQt5.QtCore import QAbstractTableModel, Qt
import random


class pandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def setData(self, index, value, role=Qt.EditRole):
        column_name = self._data.columns[index.column()]
        
        # Only allow editing for the specific grade columns
        if column_name not in ['HW1', 'HW2', 'HW3', 'Quiz1', 'Quiz2', 'Quiz3', 'Quiz4', 'MidtermExam', 'FinalExam']:
            return False

        if role == Qt.EditRole:
            try:
                value = int(value)
            except ValueError:
                # If conversion to integer fails, return False indicating data hasn't been set.
                return False
            
            self._data.iat[index.row(), index.column()] = value
            
            # Recompute WeightedAverage and LetterGrade for the modified student's data
            self._data.loc[index.row(), 'WeightedAverage'] = (
                self._data.loc[index.row(), 'HW1'] + self._data.loc[index.row(), 'HW2'] + self._data.loc[index.row(), 'HW3']) * 0.20 / 3 + \
                (self._data.loc[index.row(), 'Quiz1'] + self._data.loc[index.row(), 'Quiz2'] + self._data.loc[index.row(), 'Quiz3'] + self._data.loc[index.row(), 'Quiz4']) * 0.20 / 4 + \
                self._data.loc[index.row(), 'MidtermExam'] * 0.30 + \
                self._data.loc[index.row(), 'FinalExam'] * 0.30

            conditions = [
                (self._data.loc[index.row(), 'WeightedAverage'] >= 90),
                (self._data.loc[index.row(), 'WeightedAverage'] >= 80) & (self._data.loc[index.row(), 'WeightedAverage'] < 90),
                (self._data.loc[index.row(), 'WeightedAverage'] >= 70) & (self._data.loc[index.row(), 'WeightedAverage'] < 80),
                (self._data.loc[index.row(), 'WeightedAverage'] >= 60) & (self._data.loc[index.row(), 'WeightedAverage'] < 70),
                (self._data.loc[index.row(), 'WeightedAverage'] < 60)
            ]
            grades = ['A', 'B', 'C', 'D', 'F']
            self._data.loc[index.row(), 'LetterGrade'] = np.select(conditions, grades)

            self.dataChanged.emit(index, index, [role])
            return True
        return False
    def flags(self, index):
        original_flags = super(pandasModel, self).flags(index)
        return original_flags | Qt.ItemIsEditable

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

class CSVLoader(QWidget):

    def __init__(self):
        super().__init__()
        self.df = pd.DataFrame(columns=['SID', 'FirstName', 'LastName', 'Email', 'HW1', 'HW2', 'HW3', 'Quiz1', 'Quiz2', 'Quiz3', 'Quiz4', 'MidtermExam', 'FinalExam'])
        self.initUI()
        self.model = pandasModel(self.df)
        self.view.setModel(self.model)
    
    def setupStyles(self):
        # Style for the delete button
        deleteButtonStyle = """
        QPushButton:hover {
            background-color: rgba(255, 0, 0, 0.1);   /* Red color with a low opacity for hover */
            border: 1px solid red;                   /* Red border */
        }
   
        """
        self.deleteButton.setStyleSheet(deleteButtonStyle)

    def initUI(self):
        self.layout = QVBoxLayout()

        self.importButton = QPushButton("Import CSV")
        self.importButton.clicked.connect(self.loadCSV)

        self.exportButton = QPushButton("Export CSV")
        self.exportButton.clicked.connect(self.exportCSV)
        
        self.addButton = QPushButton("Add Student")
        self.addButton.clicked.connect(self.addStudent)
        
        self.deleteButton = QPushButton("Delete Student")
        self.deleteButton.clicked.connect(self.deleteStudent)
        self.deleteButton = QPushButton("Delete Student")
        self.deleteButton.clicked.connect(self.deleteStudent)
        
        self.deleteButton = QPushButton("Delete Student")
        self.deleteButton.clicked.connect(self.deleteStudent)
        self.setupStyles()  # Call to apply the styles

        # Search by SID
        self.searchLabel = QLabel("Search by SID:")
        self.searchInput = QLineEdit()
        self.searchInput.textChanged.connect(self.search)
        
        # Search by Task
        self.taskSearchLabel = QLabel("Search by Task (e.g., HW1, Quiz1):")
        self.taskSearchInput = QLineEdit()
        self.taskSearchInput.textChanged.connect(self.displayTaskStats)
        self.taskStatsLabel = QLabel("")

        # Table view
        self.view = QTableView()
        self.view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Add UI components to layout
        self.layout.addWidget(self.importButton)
        self.layout.addWidget(self.exportButton)
        self.layout.addWidget(self.addButton)
        self.layout.addWidget(self.deleteButton)
        self.layout.addWidget(self.searchLabel)
        self.layout.addWidget(self.searchInput)
        self.layout.addWidget(self.taskSearchLabel)
        self.layout.addWidget(self.taskSearchInput)
        self.layout.addWidget(self.taskStatsLabel)
        self.layout.addWidget(self.view)
        
        self.setLayout(self.layout)

    def exportCSV(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Export CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if filePath:
            self.df.to_csv(filePath, index=False)
    
    def computeWeightedAverage(self):
        columns_to_convert = ['HW1', 'HW2', 'HW3', 'Quiz1', 'Quiz2', 'Quiz3', 'Quiz4', 'MidtermExam', 'FinalExam']
        for col in columns_to_convert:
            self.df[col] = self.df[col].astype(float)

        self.df['WeightedAverage'] = (
            self.df['HW1'] + self.df['HW2'] + self.df['HW3']) * 0.20 / 3 + \
            (self.df['Quiz1'] + self.df['Quiz2'] + self.df['Quiz3'] + self.df['Quiz4']) * 0.20 / 4 + \
            self.df['MidtermExam'] * 0.30 + \
            self.df['FinalExam'] * 0.30
    def assignLetterGrades(self):
        conditions = [
            (self.df['WeightedAverage'] >= 90),
            (self.df['WeightedAverage'] >= 80) & (self.df['WeightedAverage'] < 90),
            (self.df['WeightedAverage'] >= 70) & (self.df['WeightedAverage'] < 80),
            (self.df['WeightedAverage'] >= 60) & (self.df['WeightedAverage'] < 70),
            (self.df['WeightedAverage'] < 60)
        ]
        grades = ['A', 'B', 'C', 'D', 'F']
        self.df['LetterGrade'] = np.select(conditions, grades)


    def addStudent(self):
        details = {}
        skip_columns = ['HW1', 'HW2', 'HW3', 'Quiz1', 'Quiz2', 'Quiz3', 'Quiz4', 'MidtermExam', 'FinalExam', 'LetterGrade', 'WeightedAverage', 'SID']

        for column in self.df.columns:
            # Skip adding the letter grade, SID, and weighted average
            if column in skip_columns:
                continue

            while True:
                text, ok = QInputDialog.getText(self, f"Enter {column}", f"{column}:")

                # If the user presses cancel
                if not ok:
                    return
                
                if column in ['HW1', 'HW2', 'HW3', 'Quiz1', 'Quiz2', 'Quiz3', 'Quiz4', 'MidtermExam', 'FinalExam']:
                    try:
                        # Convert text to float and then back to string. This will ensure validity.
                        text = str(float(text))
                        break  # exit the loop if the input is valid
                    except ValueError:
                        QMessageBox.warning(self, "Input Error", f"Invalid value for {column}. Please enter a valid number.")
                        # don't break; keep looping until the input is valid or the user cancels
                else:
                    break  # if not a score column, exit the loop

            details[column] = text

        # Generate a unique random SID
        while True:
            random_sid = str(random.randint(100000, 999999))  # Generate a 6-digit random number for SID
            if random_sid not in self.df['SID'].values:
                details['SID'] = random_sid
                break

        # Append the new student details
        self.df.loc[len(self.df)] = details
        self.computeWeightedAverage()
        self.assignLetterGrades()
        self.updateModel()

    def deleteStudent(self):
        selected_row = self.view.selectionModel().selectedRows()
        if selected_row:
            index = selected_row[0].row()
            self.df.drop(index, inplace=True)
            self.df.reset_index(drop=True, inplace=True)
            self.updateModel()
        else:
            QMessageBox.warning(self, "Delete Warning", "Please select a student to delete!")

    def loadCSV(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if filePath:
            self.df = pd.read_csv(filePath)
            self.computeWeightedAverage()  # Added
            self.assignLetterGrades()      # Added
            self.model = pandasModel(self.df)
            self.view.setModel(self.model)

    def search(self):
        searchText = self.searchInput.text()
        filteredDF = self.df[self.df['SID'].astype(str).str.contains(searchText, case=False, na=False)]
        self.model = pandasModel(filteredDF)
        self.view.setModel(self.model)
    
    def updateModel(self):
        self.model = pandasModel(self.df)
        self.view.setModel(self.model)
    
    def displayTaskStats(self):
        task_name = self.taskSearchInput.text().strip()

        if task_name not in self.df.columns:
            self.taskStatsLabel.setText("Invalid task name!")
            return

        max_score = self.df[task_name].max()
        min_score = self.df[task_name].min()
        avg_score = self.df[task_name].mean()

        stats_text = f"Max: {max_score} | Min: {min_score} | Avg: {avg_score:.2f}"
        self.taskStatsLabel.setText(stats_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CSVLoader()
    window.show()
    sys.exit(app.exec_())