import sys
import os
import tempfile
import requests
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QDateEdit, QDoubleSpinBox,
    QListWidget, QGroupBox, QFormLayout, QListWidgetItem, QMessageBox, QDialog,
    QScrollArea, QFrame)
from PyQt5.QtCore import QDate, Qt, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView
from Library.gradtagszahlenCalculator import GradtagszahlenCalculator, CityData
from Library.crudHandler import CrudHandler

class CityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adresse hinzufügen")
        self.setGeometry(200, 200, 800, 600)
        self.setModal(True)
        self.selected_lat = 52.5244
        self.selected_lon = 13.4105
        self.selected_address = ""

        layout = QVBoxLayout(self)
        address_group = QGroupBox("Adresseingabe")
        address_layout = QFormLayout(address_group)
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("z.B. Berlin, Deutschland oder Musterstraße 1, PLZ Musterstadt")
        address_layout.addRow("Adresse:", self.address_input)
        self.search_btn = QPushButton("Suchen")
        self.search_btn.clicked.connect(self.search_address)
        address_layout.addRow("", self.search_btn)
        layout.addWidget(address_group)
        map_group = QGroupBox("Kartenansicht")
        map_layout = QVBoxLayout(map_group)
        self.map_view = QWebEngineView()
        self.create_map()
        map_layout.addWidget(self.map_view)
        layout.addWidget(map_group)
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Hinzufügen")
        self.add_btn.clicked.connect(self.accept_city)
        self.add_btn.setStyleSheet("""
            QPushButton {background-color: #4CAF50; color: white; font-weight: bold; padding: 8px 16px; border: none; border-radius: 4px;}
        """)
        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.add_btn)
        layout.addLayout(button_layout)

    def create_map(self):
        try:
            lat = self.selected_lat
            lon = self.selected_lon
            address = self.selected_address.replace("'", "&#39;")
            leaflet_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset='utf-8'/>
                <meta name='viewport' content='width=device-width, initial-scale=1.0'>
                <title>Karte</title>
                <link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'/>
                <style> #map {{ height: 100vh; width: 100vw; margin:0; }} html, body {{ height:100%; margin:0; }} </style>
            </head>
            <body>
                <div id='map'></div>
                <script src='https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'></script>
                <script>
                    var map = L.map('map').setView([{lat}, {lon}], 13);
                    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                        maxZoom: 19,
                        attribution: '© OpenStreetMap contributors'
                    }}).addTo(map);
                    var marker = L.marker([{lat}, {lon}]).addTo(map)
                        .bindPopup('<b>Ausgewählter Standort</b><br>{address}')
                        .openPopup();
                </script>
            </body>
            </html>
            """
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8')
            temp_file.write(leaflet_html)
            temp_file.close()
            self.map_view.load(QUrl.fromLocalFile(temp_file.name))
        except Exception as e:
            print(f"Map creation error: {e}")
            if hasattr(self, 'map_view'):
                self.map_view.setHtml(f"<h3>Karte konnte nicht geladen werden: {e}</h3>")

    def search_address(self):
        address = self.address_input.text().strip()
        if not address:
            QMessageBox.warning(self, "Warnung", "Bitte eine Adresse eingeben!")
            return
        self.search_btn.setText("Suche...")
        self.search_btn.setEnabled(False)
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {'q': address, 'format': 'json', 'limit': 1, 'addressdetails': 1}
            headers = {'User-Agent': 'Gradtagszahlen-Tool'}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data:
                result = data[0]
                self.selected_lat = float(result['lat'])
                self.selected_lon = float(result['lon'])
                self.selected_address = result.get('display_name', address)
                self.create_map()
                QMessageBox.information(self, "Gefunden!", f"Adresse gefunden:\n{self.selected_address}\n\nKoordinaten:\nLat: {self.selected_lat:.6f}\nLon: {self.selected_lon:.6f}")
            else:
                QMessageBox.warning(self, "Nicht gefunden", f"Keine Ergebnisse für '{address}' gefunden.\nBitte überprüfen Sie die Schreibweise.")
        except requests.exceptions.Timeout:
            QMessageBox.critical(self, "Fehler", "Zeitüberschreitung bei der Suche. Bitte erneut versuchen.")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Fehler", "Keine Internetverbindung. Bitte Verbindung prüfen.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Suchfehler: {str(e)}")
        finally:
            self.search_btn.setText("Suchen")
            self.search_btn.setEnabled(True)

    def accept_city(self):
        if not self.selected_address and not self.address_input.text().strip():
            QMessageBox.warning(self, "Warnung", "Bitte eine Adresse eingeben und suchen!")
            return
        if not self.selected_address:
            self.selected_address = self.address_input.text().strip()
        reply = QMessageBox.question(self, "Adresse hinzufügen", f"Adresse hinzufügen?\n\nAdresse: {self.selected_address}\nKoordinaten: {self.selected_lat:.6f}, {self.selected_lon:.6f}", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.accept()

class GradtagsberechnungGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gradtagszahlen-Berechnung")
        self.setGeometry(100, 100, 1200, 800)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 2)

    def create_left_panel(self):
        left_widget = QWidget()
        left_widget.setMaximumWidth(600)
        left_layout = QVBoxLayout(left_widget)
        title = QLabel("Gradtagszahlen-Berechnung")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)
        zeitraum_group = QGroupBox("Berechnungszeitraum")
        zeitraum_layout = QFormLayout(zeitraum_group)
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate(2023, 10, 1))
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd.MM.yyyy")
        zeitraum_layout.addRow("Startdatum:", self.start_date)
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate(2024, 4, 30))
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd.MM.yyyy")
        zeitraum_layout.addRow("Enddatum:", self.end_date)
        left_layout.addWidget(zeitraum_group)
        parameter_group = QGroupBox("Berechnungsparameter")
        parameter_layout = QFormLayout(parameter_group)
        self.room_temp = QDoubleSpinBox()
        self.room_temp.setRange(-100.0, 100.0)
        self.room_temp.setValue(20.0)
        self.room_temp.setSuffix(" °C")
        self.room_temp.setDecimals(1)
        parameter_layout.addRow("Raumtemperatur:", self.room_temp)
        self.heating_limit = QDoubleSpinBox()
        self.heating_limit.setRange(-100.0, 100.0)
        self.heating_limit.setValue(15.0)
        self.heating_limit.setSuffix(" °C")
        self.heating_limit.setDecimals(1)
        parameter_layout.addRow("Heizgrenze:", self.heating_limit)
        left_layout.addWidget(parameter_group)
        cities_group = QGroupBox("Adressen für Berechnung")
        cities_layout = QVBoxLayout(cities_group)
        self.city_list = QListWidget()
        self.city_list.setMinimumHeight(300)
        self.city_list.setMaximumHeight(300)
        cities_layout.addWidget(self.city_list)
        city_buttons_layout = QHBoxLayout()
        self.add_city_btn = QPushButton("Adresse hinzufügen")
        self.add_city_btn.clicked.connect(self.add_city)
        city_buttons_layout.addWidget(self.add_city_btn)
        self.remove_city_btn = QPushButton("Entfernen")
        self.remove_city_btn.clicked.connect(self.remove_city)
        city_buttons_layout.addWidget(self.remove_city_btn)
        cities_layout.addLayout(city_buttons_layout)
        left_layout.addWidget(cities_group)
        action_group = QGroupBox("Aktionen")
        action_layout = QVBoxLayout(action_group)
        self.calculate_btn = QPushButton("Berechnung starten")
        self.calculate_btn.setStyleSheet("""
            QPushButton {background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border: none; border-radius: 5px;}
            QPushButton:hover {background-color: #45a049;}
        """)
        self.calculate_btn.clicked.connect(self.start_calculation)
        action_layout.addWidget(self.calculate_btn)
        self.export_btn = QPushButton("Ergebnisse exportieren")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_results)
        action_layout.addWidget(self.export_btn)
        self.clear_btn = QPushButton("Zurücksetzen")
        self.clear_btn.clicked.connect(self.reset_form)
        action_layout.addWidget(self.clear_btn)
        left_layout.addWidget(action_group)
        left_layout.addStretch()
        return left_widget

    def create_right_panel(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Results section
        results_group = QGroupBox("Berechnungsergebnisse")
        results_layout = QVBoxLayout(results_group)
        
        # Scrollable results list
        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(200)
        results_layout.addWidget(self.results_list)
        
        # Charts section
        charts_group = QGroupBox("Temperaturverlauf")
        charts_layout = QVBoxLayout(charts_group)
        
        # Scrollable area for charts
        charts_scroll = QScrollArea()
        charts_scroll.setWidgetResizable(True)
        charts_container = QWidget()
        self.charts_container_layout = QVBoxLayout(charts_container)
        charts_scroll.setWidget(charts_container)
        charts_layout.addWidget(charts_scroll)
        
        # Add groups to main layout
        right_layout.addWidget(results_group)
        right_layout.addWidget(charts_group)
        
        return right_widget

    def add_city(self):
        dialog = CityDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            address_parts = dialog.selected_address.split(',')
            city_name = address_parts[0].strip()
            if len(city_name) > 30 and len(address_parts) > 1:
                city_name = f"{address_parts[0].strip()}, {address_parts[1].strip()}"
            item_text = f"{dialog.selected_address} ({dialog.selected_lat:.4f}, {dialog.selected_lon:.4f})"
            item = QListWidgetItem(item_text)
            item.setToolTip(dialog.selected_address)
            item.setData(Qt.UserRole, {
                'name': city_name,
                'lat': dialog.selected_lat,
                'lon': dialog.selected_lon,
                'full_address': dialog.selected_address
            })
            self.city_list.addItem(item)
            QMessageBox.information(self, "Erfolg", f"Adresse '{dialog.selected_address}' wurde hinzugefügt!")

    def remove_city(self):
        current_row = self.city_list.currentRow()
        if current_row >= 0:
            self.city_list.takeItem(current_row)

    def start_calculation(self):
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        room_temp = self.room_temp.value()
        heating_limit = self.heating_limit.value()
        cities = []
        for i in range(self.city_list.count()):
            item = self.city_list.item(i)
            city_data = item.data(Qt.UserRole)
            cities.append(CityData(
                name=city_data['name'],
                latitude=city_data['lat'],
                longitude=city_data['lon']
            ))
        if not cities:
            QMessageBox.warning(self, "Warnung", "Bitte mindestens eine Adresse auswählen!")
            return
        self.results_list.clear()
        for i in reversed(range(self.charts_container_layout.count())):
            widget = self.charts_container_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        # Initialisiere API-Handler und Calculator
        crud_handler = CrudHandler("https://archive-api.open-meteo.com/v1")
        calculator = GradtagszahlenCalculator(crud_handler)
        try:
            results = calculator.calculate_for_cities(
                cities=cities,
                start_date=start_date,
                end_date=end_date,
                room_temperature=room_temp,
                heating_limit=heating_limit
            )
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Berechnung fehlgeschlagen: {e}")
            return
        # Für jede Stadt: Temperaturdaten abfragen und Diagramm erzeugen
        for city in cities:
            city_name = city.name
            result = results.get(city_name)
            if not result:
                continue
            # Temperaturdaten für Plot abfragen
            try:
                temps = calculator.get_temperature_data(city, start_date, end_date)
            except Exception as e:
                QMessageBox.warning(self, "Warnung", f"Temperaturdaten für {city_name} konnten nicht geladen werden: {e}")
                continue
            # Heiztage und Differenzen berechnen
            daily_hdds = []
            for temp in temps:
                if temp < heating_limit:
                    hdd = room_temp - temp
                    daily_hdds.append(hdd)
                else:
                    daily_hdds.append(0)
            # Ergebnistext
            result_text = (f"{city_name}: \n"
                         f"Gradtagszahl: {result.gradtagszahl:.1f}\n"
                         f"Durchschnittstemperatur: {sum(temps)/len(temps):.1f}°C\n"
                         f"Heiztage: {result.heating_days_count}")
            item = QListWidgetItem(result_text)
            # Abwechselnd einfärben
            if self.results_list.count() % 2 == 1:
                item.setBackground(Qt.lightGray)
            self.results_list.addItem(item)
            # Datumsliste erzeugen
            start = datetime.strptime(start_date, "%Y-%m-%d")
            dates = [(start + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(len(temps))]
            self.create_temperature_chart(
                city_name,
                dates,
                temps,
                room_temp,
                heating_limit,
                daily_hdds
            )
        self.export_btn.setEnabled(True)

    def create_temperature_chart(self, city_name, dates, temperatures, room_temp, heating_limit, hdds):
        chart_container = QWidget()
        chart_layout = QVBoxLayout(chart_container)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.setSpacing(0)
        web_view = QWebEngineView()
        web_view.setMinimumHeight(400)
        web_view.setMaximumHeight(400)
        fig = go.Figure()
        # Temperaturkurve als Treppenfunktion (hv), keine Marker
        fig.add_trace(go.Scatter(
            x=dates,
            y=temperatures,
            name='Außentemperatur',
            line=dict(color='#2196F3', shape='hv'),
            hovertemplate='%{y:.1f}°C<extra></extra>',
            mode='lines'
        ))
        # Raumtemperatur-Linie
        fig.add_trace(go.Scatter(
            x=dates,
            y=[room_temp]*len(dates),
            name='Raumtemperatur',
            line=dict(color='#FF9800', dash='dash')
        ))
        # Heizgrenze-Linie
        fig.add_trace(go.Scatter(
            x=dates,
            y=[heating_limit]*len(dates),
            name='Heizgrenze',
            line=dict(color='#F44336', dash='dash')
        ))
        # Heizbedarf-Flächen: Für jeden Block von Heiztagen eine eigene Fläche
        block_start = None
        for i, temp in enumerate(temperatures + [None]):  # +[None] für Blockende am Schluss
            if temp is not None and temp < heating_limit:
                if block_start is None:
                    block_start = i
            else:
                if block_start is not None:
                    block_end = i
                    # Block von block_start bis block_end-1
                    x_block = dates[block_start:block_end] + dates[block_start:block_end][::-1]
                    y_block = [room_temp]*(block_end-block_start) + temperatures[block_start:block_end][::-1]
                    fig.add_trace(go.Scatter(
                        x=x_block,
                        y=y_block,
                        fill='toself',
                        fillcolor='rgba(255, 152, 0, 0.2)',
                        line=dict(width=0),
                        name='Heizbedarf' if block_start == 0 else None,
                        showlegend=(block_start == 0),
                        hoverinfo='skip',
                    ))
                    block_start = None
        fig.update_layout(
            title=f'Temperaturverlauf - {city_name}',
            xaxis_title='Datum',
            yaxis_title='Temperatur (°C)',
            hovermode='x unified',
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255, 255, 255, 0.8)'
            )
        )
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8')
        temp_file.write(fig.to_html(include_plotlyjs='cdn', full_html=True))
        temp_file.close()
        web_view.load(QUrl.fromLocalFile(temp_file.name))
        chart_layout.addWidget(web_view)
        chart_container.setMinimumHeight(400)
        chart_container.setMaximumHeight(400)
        self.charts_container_layout.addWidget(chart_container)

    def export_results(self):
        QMessageBox.information(self, "Info", "Export-Funktionalität würde hier implementiert")

    def reset_form(self):
        self.start_date.setDate(QDate(2023, 10, 1))
        self.end_date.setDate(QDate(2024, 4, 30))
        self.room_temp.setValue(20.0)
        self.heating_limit.setValue(15.0)
        self.export_btn.setEnabled(False)
        self.results_list.clear()
        
        # Clear all charts
        for i in reversed(range(self.charts_container_layout.count())):
            widget = self.charts_container_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

def main():
    app = QApplication(sys.argv)
    window = GradtagsberechnungGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
