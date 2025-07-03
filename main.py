import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QDateEdit, QDoubleSpinBox,
    QListWidget, QGroupBox, QFormLayout, QSpacerItem, QSizePolicy,
    QListWidgetItem, QMessageBox, QInputDialog, QAbstractSpinBox
)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from datetime import datetime, date

class GradtagsberechnungGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gradtagszahlen-Berechnung")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for inputs
        left_panel = self.create_left_panel()
        
        # Right panel
        right_panel = self.create_right_panel()
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 1)    # 30% width
        main_layout.addWidget(right_panel, 2)   # 70% width
        
    def create_left_panel(self):
        """Create the left input panel"""
        left_widget = QWidget()
        left_widget.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_widget)
        
        # Title
        title = QLabel("Gradtagszahlen-Berechnung")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)
        
        # === ZEITRAUM SECTION ===
        zeitraum_group = QGroupBox("Berechnungszeitraum")
        zeitraum_layout = QFormLayout(zeitraum_group)
        
        # Start date
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate(2023, 10, 1))  # Default: Oct 1st
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd.MM.yyyy")
        zeitraum_layout.addRow("Startdatum:", self.start_date)
        
        # End date
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate(2024, 4, 30))  # Default: Apr 30th
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd.MM.yyyy")
        zeitraum_layout.addRow("Enddatum:", self.end_date)
        
        left_layout.addWidget(zeitraum_group)
        
        # === PARAMETER SECTION ===
        parameter_group = QGroupBox("Berechnungsparameter")
        parameter_layout = QFormLayout(parameter_group)
        
        # Room temperature
        self.room_temp = QDoubleSpinBox()
        self.room_temp.setRange(-100.0, 100.0)
        self.room_temp.setValue(20.0)
        self.room_temp.setSuffix(" °C")
        self.room_temp.setDecimals(1)
        self.room_temp.setKeyboardTracking(False) # Disable immediate update on typing
        self.room_temp.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType) # Adaptive step size
        parameter_layout.addRow("Raumtemperatur:", self.room_temp)
        
        # Heating limit
        self.heating_limit = QDoubleSpinBox()
        self.heating_limit.setRange(-100.0, 100.0)
        self.heating_limit.setValue(15.0)
        self.heating_limit.setSuffix(" °C")
        self.heating_limit.setDecimals(1)
        self.heating_limit.setKeyboardTracking(False) # Disable immediate update on typing
        self.heating_limit.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        parameter_layout.addRow("Heizgrenze:", self.heating_limit)
        
        left_layout.addWidget(parameter_group)
        
        # === STÄDTE SECTION ===
        cities_group = QGroupBox("Städte für Berechnung")
        cities_layout = QVBoxLayout(cities_group)
        
        # City list
        self.city_list = QListWidget()
        self.city_list.setMaximumHeight(150)
        # Add some default cities
        self.add_default_cities()
        cities_layout.addWidget(self.city_list)
        
        # City management buttons
        city_buttons_layout = QHBoxLayout()
        
        self.add_city_btn = QPushButton("Stadt hinzufügen")
        self.add_city_btn.clicked.connect(self.add_city)
        city_buttons_layout.addWidget(self.add_city_btn)
        
        self.edit_city_btn = QPushButton("Bearbeiten")
        self.edit_city_btn.clicked.connect(self.edit_city)
        city_buttons_layout.addWidget(self.edit_city_btn)
        
        self.remove_city_btn = QPushButton("Entfernen")
        self.remove_city_btn.clicked.connect(self.remove_city)
        city_buttons_layout.addWidget(self.remove_city_btn)
        
        cities_layout.addLayout(city_buttons_layout)
        left_layout.addWidget(cities_group)
        
        # === ACTION BUTTONS ===
        action_group = QGroupBox("Aktionen")
        action_layout = QVBoxLayout(action_group)
        
        # Calculate button
        self.calculate_btn = QPushButton("Berechnung starten")
        self.calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.calculate_btn.clicked.connect(self.start_calculation)
        action_layout.addWidget(self.calculate_btn)
        
        # Export button
        self.export_btn = QPushButton("Ergebnisse exportieren")
        self.export_btn.setEnabled(False)  # Initially disabled
        self.export_btn.clicked.connect(self.export_results)
        action_layout.addWidget(self.export_btn)
        
        # Clear button
        self.clear_btn = QPushButton("Zurücksetzen")
        self.clear_btn.clicked.connect(self.reset_form)
        action_layout.addWidget(self.clear_btn)
        
        left_layout.addWidget(action_group)
        
        # Add stretch to push everything to top
        left_layout.addStretch()
        
        return left_widget
    
    def create_right_panel(self):
        """Create placeholder for right panel (results/map)"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        placeholder = QLabel("Hier werden Ergebnisse und Karte angezeigt")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 10px;
                color: #888;
                font-size: 16px;
                padding: 50px;
            }
        """)
        
        right_layout.addWidget(placeholder)
        return right_widget
    
    def add_default_cities(self):
        """Add some default German cities"""
        default_cities = [
            ("Berlin", 52.5244, 13.4105),
            ("München", 48.1351, 11.5820),
            ("Hamburg", 53.5511, 9.9937),
            ("Köln", 50.9375, 6.9603),
            ("Frankfurt", 50.1109, 8.6821)
        ]
        
        for name, lat, lon in default_cities:
            item_text = f"{name} ({lat:.4f}, {lon:.4f})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, {'name': name, 'lat': lat, 'lon': lon})
            self.city_list.addItem(item)
    
    def add_city(self):
        """Add a new city via dialog"""
        from city_dialog import CityDialog  # Would need separate dialog class
        # For now, simple input dialog
        name, ok = QInputDialog.getText(self, "Stadt hinzufügen", "Stadtname:")
        if ok and name:
            lat, ok = QInputDialog.getDouble(self, "Koordinaten", "Breitengrad:", 
                                           decimals=4, min=-90, max=90)
            if ok:
                lon, ok = QInputDialog.getDouble(self, "Koordinaten", "Längengrad:", 
                                               decimals=4, min=-180, max=180)
                if ok:
                    item_text = f"{name} ({lat:.4f}, {lon:.4f})"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, {'name': name, 'lat': lat, 'lon': lon})
                    self.city_list.addItem(item)
    
    def edit_city(self):
        """Edit selected city"""
        current = self.city_list.currentItem()
        if current:
            data = current.data(Qt.UserRole)
            # Here you would open edit dialog
            QMessageBox.information(self, "Info", f"Bearbeitung von {data['name']} würde hier implementiert")
    
    def remove_city(self):
        """Remove selected city"""
        current_row = self.city_list.currentRow()
        if current_row >= 0:
            item = self.city_list.takeItem(current_row)
    
    def start_calculation(self):
        """Start the heating degree days calculation"""
        # Get all input values
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        room_temp = self.room_temp.value()
        heating_limit = self.heating_limit.value()
        
        # Get cities from list
        cities = []
        for i in range(self.city_list.count()):
            item = self.city_list.item(i)
            city_data = item.data(Qt.UserRole)
            cities.append(city_data)
        
        if not cities:
            QMessageBox.warning(self, "Warnung", "Bitte mindestens eine Stadt auswählen!")
            return
        
        # Here would be the actual calculation call
        QMessageBox.information(self, "Info", 
                              f"Berechnung gestartet für {len(cities)} Städte\n"
                              f"Zeitraum: {start_date} bis {end_date}\n"
                              f"Parameter: {room_temp}°C / {heating_limit}°C")
        
        # Enable export button after calculation
        self.export_btn.setEnabled(True)
    
    def export_results(self):
        """Export calculation results"""
        QMessageBox.information(self, "Info", "Export-Funktionalität würde hier implementiert")
    
    def reset_form(self):
        """Reset all form fields to defaults"""
        self.start_date.setDate(QDate(2023, 10, 1))
        self.end_date.setDate(QDate(2024, 4, 30))
        self.room_temp.setValue(20.0)
        self.heating_limit.setValue(15.0)
        self.export_btn.setEnabled(False)

def main():
    app = QApplication(sys.argv)
    window = GradtagsberechnungGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
