import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QDateEdit, QDoubleSpinBox,
    QListWidget, QGroupBox, QFormLayout, QSpacerItem, QSizePolicy,
    QListWidgetItem, QMessageBox, QInputDialog, QAbstractSpinBox, QDialog)
from PySide6.QtCore import QDate, Qt, QUrl, QTimer
from PySide6.QtGui import QFont
from datetime import datetime, date
from PySide6.QtWebEngineWidgets import QWebEngineView
import folium
import tempfile
import os

class CityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Stadt hinzufügen")
        self.setGeometry(200, 200, 800, 600)
        self.setWindowModality(Qt.ApplicationModal)
        
        # Store coordinates
        self.selected_lat = 52.5244  # Default Berlin
        self.selected_lon = 13.4105
        self.selected_address = ""
        
        layout = QVBoxLayout(self)
        
        # Address input section
        address_group = QGroupBox("Adresseingabe")
        address_layout = QFormLayout(address_group)
        
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("z.B. Berlin, Deutschland oder Musterstraße 1, PLZ Musterstadt")
        address_layout.addRow("Adresse:", self.address_input)
        
        self.search_btn = QPushButton("Suchen")
        self.search_btn.clicked.connect(self.search_address)
        address_layout.addRow("", self.search_btn)
        
        layout.addWidget(address_group)
        
        # Map section
        map_group = QGroupBox("Kartenansicht")
        map_layout = QVBoxLayout(map_group)
        
        self.map_view = QWebEngineView()
        self.create_map()
        map_layout.addWidget(self.map_view)
        
        layout.addWidget(map_group)
        
        # Buttons section
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Hinzufügen")
        self.add_btn.clicked.connect(self.accept_city)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
        """)
        
        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.add_btn)
        
        layout.addLayout(button_layout)
        
    def create_map(self):
        """Create interactive map with folium"""
        # Create folium map
        m = folium.Map(
                location=[self.selected_lat, self.selected_lon],
                zoom_start=10,
                tiles='OpenStreetMap')
        
        # Add tile layers for satellite view
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite',
            overlay=False,
            control=True).add_to(m)
        
        # Add marker
        folium.Marker(
            [self.selected_lat, self.selected_lon],
            popup=f"Lat: {self.selected_lat:.4f}, Lon: {self.selected_lon:.4f}",
            draggable=True).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add click event JavaScript
        click_js = """
        function onMapClick(e) {
            // This would need more complex implementation for coordinate updates
        }
        """
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html')
        m.save(temp_file.name)
        temp_file.close()
        
        # Load in web view
        self.map_view.load(QUrl.fromLocalFile(temp_file.name))
        
    def search_address(self):
        """Search for address and update map"""
        address = self.address_input.text().strip()
        if not address:
            QMessageBox.warning(self, "Warnung", "Bitte eine Adresse eingeben!")
            return
            
        # Here you would implement geocoding
        # For now, just show message
        QMessageBox.information(self, "Info", f"Suche nach: {address}\n(Geocoding wird implementiert)")
        
        # Mock coordinates (in real implementation, use geocoding service)
        self.selected_address = address
        # Update map with new coordinates
        self.create_map()
        
    def accept_city(self):
        """Accept the selected city"""
        if not self.address_input.text().strip():
            QMessageBox.warning(self, "Warnung", "Bitte eine Adresse eingeben!")
            return
            
        self.selected_address = self.address_input.text().strip()
        self.close()

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
    
    def add_city(self):
        """Add a new city via dialog"""
        dialog = CityDialog(self)
        dialog.show()
        
        # Wait for dialog to close (non-blocking)
        def on_dialog_closed():
            if hasattr(dialog, 'selected_address') and dialog.selected_address:
                # Extract city name from address (simple approach)
                city_name = dialog.selected_address.split(',')[0].strip()
                
                item_text = f"{city_name} ({dialog.selected_lat:.4f}, {dialog.selected_lon:.4f})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, {
                    'name': city_name, 
                    'lat': dialog.selected_lat, 
                    'lon': dialog.selected_lon})
                self.city_list.addItem(item)
        
        dialog.destroyed.connect(on_dialog_closed)
    
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
