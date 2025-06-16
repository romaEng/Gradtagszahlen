import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from crudHandler import CrudHandler
from accessify import protected

@dataclass
class CityData:
    """Data class for city information"""
    name: str
    latitude: float
    longitude: float

@dataclass
class CalculationResult:
    """Data class for calculation results"""
    city_name: str
    gradtagszahl: float
    heating_days_count: int
    period_start: str
    period_end: str
    room_temperature: float
    heating_limit: float

class GradtagszahlenCalculator:
    """
    Calculator for heating degree days (Gradtagszahlen) according to VDI 2067
    
    Formula: Gt = Σ(room_temp - outdoor_temp) for all heating days
    Heating day: outdoor_temp < heating_limit
    """
    
    def __init__(self, crud_handler: CrudHandler):
        """
        Initialize calculator with CRUD handler
        
        Args:
            crud_handler: Instance of CrudHandler for API requests
        """
        self.crud_handler = crud_handler
        self.logger = logging.getLogger(__name__)
        
    def calculate_for_cities(
        self,
        cities: List[CityData],
        start_date: str,
        end_date: str,
        room_temperature: float = 20.0,
        heating_limit: float = 15.0
        ) -> Dict[str, CalculationResult]:
        """
        Calculate heating degree days for multiple cities
        
        Args:
            cities: List of CityData objects
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            room_temperature: Target indoor temperature (default: 20°C)
            heating_limit: Temperature below which heating is needed (default: 15°C)
            
        Returns:
            Dictionary with city names as keys and CalculationResult as values
            
        Raises:
            ValueError: For invalid date formats or parameters
            Exception: For API or calculation errors
        """
        self.logger.info(f"Starting calculation for {len(cities)} cities")
        self.logger.info(f"Period: {start_date} to {end_date}")
        self.logger.info(f"Room temp: {room_temperature}°C, Heating limit: {heating_limit}°C")
        
        # Validate inputs
        self._validate_inputs(cities, start_date, end_date, room_temperature, heating_limit)
        
        results = {}
        
        for city in cities:
            try:
                self.logger.info(f"Processing city: {city.name}")
                
                # Get temperature data for the city
                temperature_data = self._fetch_temperature_data(
                    city, start_date, end_date)
                
                # Calculate heating degree days
                gradtagszahl, heating_days = self._calculate_heating_degree_days(
                    temperature_data, room_temperature, heating_limit)
                
                # Create result object
                result = CalculationResult(
                    city_name=city.name,
                    gradtagszahl=gradtagszahl,
                    heating_days_count=heating_days,
                    period_start=start_date,
                    period_end=end_date,
                    room_temperature=room_temperature,
                    heating_limit=heating_limit)
                
                results[city.name] = result
                
                self.logger.info(
                    f"{city.name}: {gradtagszahl:.1f}, "
                    f"({heating_days} heating days)"
                )
                
            except Exception as e:
                self.logger.error(f"Error processing {city.name}: {e}")
                # Continue with other cities, don't fail completely
                continue
                
        self.logger.info(f"Calculation completed for {len(results)}/{len(cities)} cities")
        return results
    
    @protected
    def _validate_inputs(
        self,
        cities: List[CityData],
        start_date: str,
        end_date: str,
        room_temperature: float,
        heating_limit: float
        ) -> None:
        """Validate input parameters"""
        if not cities:
            raise ValueError("Cities list cannot be empty")
            
        # Validate date formats
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Use 'YYYY-MM-DD'")
            
        if start_dt >= end_dt:
            raise ValueError("Start date must be before end date")
            
        if room_temperature <= heating_limit:
            raise ValueError("Room temperature must be higher than heating limit")
            
        # Validate city coordinates
        for city in cities:
            if not (-90 <= city.latitude <= 90):
                raise ValueError(f"Invalid latitude for {city.name}: {city.latitude}")
            if not (-180 <= city.longitude <= 180):
                raise ValueError(f"Invalid longitude for {city.name}: {city.longitude}")
    
    @protected
    def _fetch_temperature_data(
        self,
        city: CityData,
        start_date: str,
        end_date: str
        ) -> List[float]:
        """
        Fetch daily mean temperature data from Open-Meteo API
        
        Args:
            city: CityData object with coordinates
            start_date: Start date string
            end_date: End date string
            
        Returns:
            List of daily mean temperatures in Celsius
        """

        params = {
            'latitude': city.latitude,
            'longitude': city.longitude,
            'start_date': start_date,
            'end_date': end_date,
            'daily': 'temperature_2m_mean',
            'timezone': 'auto'}
        
        try:
            response = self.crud_handler.get('archive', params)
            
            # Extract temperature data
            if 'daily' not in response or 'temperature_2m_mean' not in response['daily']:
                raise ValueError(f"Invalid API response for {city.name}")
                
            temperatures = response['daily']['temperature_2m_mean']
            
            # Filter out None values
            valid_temperatures = [temp for temp in temperatures if temp is not None]
            
            if not valid_temperatures:
                raise ValueError(f"No valid temperature data for {city.name}")
                
            self.logger.debug(f"Fetched {len(valid_temperatures)} temperature values for {city.name}")
            return valid_temperatures
            
        except Exception as e:
            raise Exception(f"Failed to fetch temperature data for {city.name}: {e}")
    
    @protected
    def _calculate_heating_degree_days(
        self,
        temperatures: List[float],
        room_temperature: float,
        heating_limit: float
        ) -> Tuple[float, int]:
        """
        Calculate heating degree days from temperature data
        
        Args:
            temperatures: List of daily mean temperatures
            room_temperature: Target indoor temperature
            heating_limit: Temperature below which heating is needed
            
        Returns:
            Tuple of (total_gradtagszahl, number_of_heating_days)
        """
        total_gradtagszahl = 0.0
        heating_days = 0
        
        for temp in temperatures:
            # Check if it's a heating day
            if temp < heating_limit:
                # Calculate heating degree day value
                daily_gradtag = room_temperature - temp
                total_gradtagszahl += daily_gradtag
                heating_days += 1
                
        self.logger.debug(f"Calculated {total_gradtagszahl:.1f} Kd from {heating_days} heating days")
        return total_gradtagszahl, heating_days
    
    def get_calculation_summary(self, results: Dict[str, CalculationResult]) -> str:
        """
        Generate a formatted summary of calculation results
        
        Args:
            results: Dictionary of calculation results
            
        Returns:
            Formatted summary string
        """
        if not results:
            return "No calculation results available."
            
        summary_lines = [
            "=== GRADTAGSZAHLEN BERECHNUNG ===",
            f"Zeitraum: {list(results.values())[0].period_start} bis {list(results.values())[0].period_end}",
            f"Raumtemperatur: {list(results.values())[0].room_temperature}°C",
            f"Heizgrenze: {list(results.values())[0].heating_limit}°C",
            "",
            "Ergebnisse:"
        ]
        
        # Sort cities by heating degree days (descending)
        sorted_results = sorted(
            results.items(), 
            key=lambda x: x[1].gradtagszahl, 
            reverse=True
        )
        
        for city_name, result in sorted_results:
            summary_lines.append(
                f"  {city_name:20} {result.gradtagszahl:8.1f} Kd "
                f"({result.heating_days_count} Heiztage)"
            )
            
        return "\n".join(summary_lines)


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize calculator with Open-Meteo API
    crud_handler = CrudHandler("https://archive-api.open-meteo.com/v1")
    calculator = GradtagszahlenCalculator(crud_handler)
    
    # Example cities
    cities = [
        CityData("Berlin", 52.5244, 13.4105),
        CityData("München", 48.1351, 11.5820),
        CityData("Hamburg", 53.5511, 9.9937)
    ]
    
    try:
        # Calculate for last heating season (example: Oct 2022 - Apr 2023)
        results = calculator.calculate_for_cities(
            cities=cities,
            start_date="2022-10-01",
            end_date="2023-04-30",
            room_temperature=20.0,
            heating_limit=15.0
        )
        
        # Print summary
        print(calculator.get_calculation_summary(results))
        
    except Exception as e:
        print(f"Calculation failed: {e}")
