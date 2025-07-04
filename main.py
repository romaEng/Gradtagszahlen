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
import requests
import json

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
        self.setModal(True)
        
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
        try:
            # Create folium map
            m = folium.Map(
                location=[self.selected_lat, self.selected_lon],
                zoom_start=12,
                tiles='OpenStreetMap')
            
            # Add tile layers for satellite view
            folium.TileLayer(
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri',
                name='Satellit',
                overlay=False,
                control=True).add_to(m)
            
            # Add CartoDB Positron (clean style)
            folium.TileLayer(
                tiles='CartoDB positron',
                name='Hell',
                overlay=False,
                control=True).add_to(m)
            
            # Add marker with better popup
            popup_text = f"""
            <b>Ausgewählter Standort</b><br>
            Breitengrad: {self.selected_lat:.6f}<br>
            Längengrad: {self.selected_lon:.6f}<br>
            {f'<br>{self.selected_address}' if self.selected_address else ''}
            """
            
            folium.Marker(
                [self.selected_lat, self.selected_lon],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip="Klicken für Details",
                icon=folium.Icon(color='red', icon='home')).add_to(m)
            
            # Add layer control
            folium.LayerControl().add_to(m)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8')
            m.save(temp_file.name)
            temp_file.close()
            
            # Load in web view
            self.map_view.load(QUrl.fromLocalFile(temp_file.name))
            
        except Exception as e:
            print(f"Map creation error: {e}")
            # Fallback: show error in web view
            error_html = f"""
            <html><body>
            <h3>Karte konnte nicht geladen werden</h3>
            <p>Fehler: {str(e)}</p>
            <p>Koordinaten: {self.selected_lat:.6f}, {self.selected_lon:.6f}</p>
            </body></html>
            """
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8')
            temp_file.write(error_html)
            temp_file.close()
            self.map_view.load(QUrl.fromLocalFile(temp_file.name))
        
    def search_address(self):
        """Search for address using Nominatim geocoding"""
        address = self.address_input.text().strip()
        if not address:
            QMessageBox.warning(self, "Warnung", "Bitte eine Adresse eingeben!")
            return
        
        # Show searching message
        self.search_btn.setText("Suche...")
        self.search_btn.setEnabled(False)
        
        try:
            # Use Nominatim (OpenStreetMap) for geocoding
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1}
            
            headers = {
                'User-Agent': 'Gradtagszahlen-Tool'}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data:
                # Found address
                result = data[0]
                self.selected_lat = float(result['lat'])
                self.selected_lon = float(result['lon'])
                self.selected_address = result.get('display_name', address)
                
                # Update map
                self.create_map()
                
                QMessageBox.information(self, "Gefunden!", 
                    f"Adresse gefunden:\n{self.selected_address}\n\n"
                    f"Koordinaten:\n"
                    f"Lat: {self.selected_lat:.6f}\n"
                    f"Lon: {self.selected_lon:.6f}")
            else:
                QMessageBox.warning(self, "Nicht gefunden", 
                    f"Keine Ergebnisse für '{address}' gefunden.\n"
                    "Bitte überprüfen Sie die Schreibweise.")
                
        except requests.exceptions.Timeout:
            QMessageBox.critical(self, "Fehler", 
                "Zeitüberschreitung bei der Suche. Bitte erneut versuchen.")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Fehler", 
                "Keine Internetverbindung. Bitte Verbindung prüfen.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Suchfehler: {str(e)}")
        
        finally:
            # Reset button
            self.search_btn.setText("Suchen")
            self.search_btn.setEnabled(True)
        
    def accept_city(self):
        """Accept the selected city"""
        if not self.selected_address and not self.address_input.text().strip():
            QMessageBox.warning(self, "Warnung", "Bitte eine Adresse eingeben und suchen!")
            return
        
        # Use searched address or manual input
        if not self.selected_address:
            self.selected_address = self.address_input.text().strip()
        
        # Confirm the selection
        reply = QMessageBox.question(self, "Stadt hinzufügen", 
            f"Stadt hinzufügen?\n\n"
            f"Adresse: {self.selected_address}\n"
            f"Koordinaten: {self.selected_lat:.6f}, {self.selected_lon:.6f}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:
            self.accept()  # Close dialog with success

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
        
        if dialog.exec() == QDialog.Accepted:
            # Extract city name from address (get first part before comma)
            address_parts = dialog.selected_address.split(',')
            city_name = address_parts[0].strip()
            
            # If still too long, take first two parts
            if len(city_name) > 30 and len(address_parts) > 1:
                city_name = f"{address_parts[0].strip()}, {address_parts[1].strip()}"
            
            # Create list item
            item_text = f"{dialog.selected_address} ({dialog.selected_lat:.4f}, {dialog.selected_lon:.4f})"
            item = QListWidgetItem(item_text)
            item.setToolTip(dialog.selected_address)
            item.setData(Qt.UserRole, {
                'name': city_name,
                'lat': dialog.selected_lat,
                'lon': dialog.selected_lon,
                'full_address': dialog.selected_address
            })
            
            # Add to list
            self.city_list.addItem(item)
            
            # Show success message
            QMessageBox.information(self, "Erfolg", f"Adresse '{dialog.selected_address}' wurde hinzugefügt!")
    
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
