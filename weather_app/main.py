"""Weather Application using Flet v0.28.3"""

import flet as ft
from weather_service import WeatherService
from config import Config


class WeatherApp:
    """Main Weather Application class."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.search_history = []
        self.last_weather_data = None  # ✅ store last weather data for dynamic re-render
        self.setup_page()
        self.build_ui()
        self.current_unit = "metric"

    # ------------------ BASIC UI SETUP ------------------ #

    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
        self.page.padding = 20
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()

    def get_theme_color(self):
        """Return background color based on current theme."""
        return ft.Colors.BLUE_900 if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLUE_50

    def add_to_history(self, city: str):
        """Add city to search history."""
        if city not in self.search_history:
            self.search_history.insert(0, city)
            self.search_history = self.search_history[:5]  # Keep last 5

    def build_history_dropdown(self):
        """Build dropdown with search history."""
        return ft.Dropdown(
            label="Recent Searches",
            options=[ft.dropdown.Option(city) for city in self.search_history],
            on_change=lambda e: self.load_from_history(e.control.value),
            expand=True
        )
    
    def update_history_dropdown(self):
        """Refresh the search history dropdown."""
        if hasattr(self, "history_dropdown"):
            self.history_dropdown.options = [
                ft.dropdown.Option(city) for city in self.search_history
            ]
            self.page.update()

    def load_from_history(self, city: str):
        """Load weather for a city from search history."""
        if city:
            self.city_input.value = city
            self.page.update()
            self.page.run_task(self.get_weather) 


    # ------------------ THEME TOGGLE ------------------ #

    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE

        # Update main container color
        self.weather_container.bgcolor = self.get_theme_color()

        # 🔁 Re-render weather info if already loaded
        if self.last_weather_data:
            self.display_weather(self.last_weather_data)

        self.page.update()

    # ------------------ UI BUILD ------------------ #

    def build_ui(self):
        """Build the user interface."""
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        self.current_unit = 'metric'
        self.current_temp = 0.0
        self.feels_like = 0.0

        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_100 if is_dark else ft.Colors.BLUE_700,
        )

        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )

        self.unit_button = ft.TextButton(
            text="°C / °F",
            on_click=self.toggle_units,
        )

        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
        )

        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )

        self.weather_container = ft.Container(
            visible=False,
            bgcolor=self.get_theme_color(),
            border_radius=10,
            padding=20,
        )

        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )

        self.loading = ft.ProgressRing(visible=False)

        self.history_dropdown = self.build_history_dropdown()

        self.page.add(
            ft.Column(
                [
                    ft.Row(
                        [self.title, self.theme_button],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.city_input,
                    ft.Row(
                        [self.search_button,self.history_dropdown],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        )
    
    # ----------------------- MISC ---------------------- #

    def toggle_units(self, e):
        """Toggle between Celsius and Fahrenheit."""
        if self.current_unit == "metric":
            self.current_unit = "imperial"
            # Convert existing temperature
            self.current_temp = (self.current_temp * 9/5) + 32
            self.feels_like = (self.feels_like * 9/5) + 32
            self.update_display()
        else:
            self.current_unit = "metric"
            self.current_temp = (self.current_temp - 32) * 5/9
            self.feels_like = (self.feels_like - 32) * 5/9
            self.update_display()

    # ------------------ WEATHER LOGIC ------------------ #

    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)

    async def get_weather(self):
        """Fetch and display weather + forecast data."""
        city = self.city_input.value.strip()

        if not city:
            self.show_error("Please enter a city name")
            return

        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()

        try:
            # Fetch current weather and forecast data
            weather_data = await self.weather_service.get_weather(city)
            self.forecast_data = await self.weather_service.get_forecast(city)

            # Update display with both
            self.display_weather(weather_data)
            self.update_display()

            #Add to history
            self.add_to_history(city)
            self.update_history_dropdown()


        except Exception as e:
            self.show_error(str(e))
        finally:
            self.loading.visible = False
            self.page.update()


    def display_weather(self, data: dict):
        """Display weather information with dynamic theming."""
        self.last_weather_data = data

        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)

        # ✅ Convert API data based on current unit before displaying
        if self.current_unit == "imperial":
            temp = (temp * 9 / 5) + 32
            feels_like = (feels_like * 9 / 5) + 32
        elif self.current_unit == "metric":
            # OpenWeather usually returns Kelvin if no unit param — convert to °C
            if temp > 200:  # crude check for Kelvin
                temp -= 273.15
                feels_like -= 273.15

        self.current_temp = temp
        self.city_name = city_name
        self.country = country
        self.feels_like = feels_like
        self.humidity = humidity
        self.description = description
        self.icon_code = icon_code
        self.wind_speed = wind_speed

        self.update_display()

        
    def update_display(self):
        # Theme-aware colors
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        text_color = ft.Colors.WHITE if is_dark else ft.Colors.BLACK
        sub_text_color = ft.Colors.GREY_400 if is_dark else ft.Colors.GREY_700
        container_color = ft.Colors.BLUE_900 if is_dark else ft.Colors.BLUE_50
        divider_color = ft.Colors.GREY_700 if is_dark else ft.Colors.GREY_300
        card_color = ft.Colors.BLUE_GREY_900 if is_dark else ft.Colors.BLUE_GREY_50
        unit_symbol = "°C" if self.current_unit == 'metric' else '°F'

        # --- MAIN WEATHER DISPLAY ---
        weather_column = [
            self.unit_button,
            ft.Text(
                f"{self.city_name}, {self.country}",
                size=24,
                weight=ft.FontWeight.BOLD,
                color=text_color,
            ),
            ft.Row(
                [
                    ft.Image(
                        src=f"https://openweathermap.org/img/wn/{self.icon_code}@2x.png",
                        width=100,
                        height=100,
                    ),
                    ft.Text(
                        self.description,
                        size=20,
                        italic=True,
                        color=text_color,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Text(
                f"{self.current_temp:.1f}{unit_symbol}",
                size=48,
                weight=ft.FontWeight.BOLD,
                color=text_color,
            ),
            ft.Text(
                f"Feels like {self.feels_like:.1f}{unit_symbol}",
                size=16,
                color=sub_text_color,
            ),
            ft.Divider(color=divider_color),
            ft.Row(
                [
                    self.create_info_card(
                        ft.Icons.WATER_DROP,
                        "Humidity",
                        f"{self.humidity}%",
                        is_dark=is_dark,
                    ),
                    self.create_info_card(
                        ft.Icons.AIR,
                        "Wind Speed",
                        f"{self.wind_speed} m/s",
                        is_dark=is_dark,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            ),
        ]

        # --- 5-DAY FORECAST INTEGRATION ---
        if hasattr(self, "forecast_data") and self.forecast_data:
            forecasts = []
            for entry in self.forecast_data.get("list", []):
                if "12:00:00" in entry["dt_txt"]:
                    forecasts.append(entry)
                if len(forecasts) >= 5:
                    break

            if not forecasts:
                forecasts = self.forecast_data["list"][:5]  # fallback

            forecast_cards = []
            from datetime import datetime

            for entry in forecasts:
                date = entry["dt_txt"].split(" ")[0]
                day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%a")
                temp = entry["main"]["temp"]
                description = entry["weather"][0]["description"].title()
                icon_code = entry["weather"][0]["icon"]

                forecast_cards.append(
                    ft.Container(
                        bgcolor=card_color,
                        border_radius=10,
                        padding=10,
                        width=100,
                        content=ft.Column(
                            [
                                ft.Text(day_name, size=16, weight=ft.FontWeight.BOLD, color=text_color),
                                ft.Image(
                                    src=f"https://openweathermap.org/img/wn/{icon_code}.png",
                                    width=50,
                                    height=50,
                                ),
                                ft.Text(f"{temp:.1f}{unit_symbol}", size=18, color=text_color),
                                ft.Text(description, size=12, color=sub_text_color, text_align=ft.TextAlign.CENTER),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=5,
                        ),
                    )
                )

            weather_column.extend([
                ft.Divider(color=divider_color),
                ft.Text("5-Day Forecast", size=18, weight=ft.FontWeight.BOLD, color=text_color),
                ft.Row(
                    controls=forecast_cards,
                    alignment=ft.MainAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.ALWAYS,
                ),
            ])

        # --- Final Layout ---
        self.weather_container.content = ft.Column(
            weather_column,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.weather_container.bgcolor = container_color
        self.weather_container.visible = True
        self.error_message.visible = False
        self.page.update()

        # --- High Temperature Alert ---
        if (self.current_unit == "metric" and self.current_temp > 35) or \
            (self.current_unit == "imperial" and self.current_temp > 95):
            alert = ft.Banner(
                bgcolor=ft.Colors.AMBER_100 if not is_dark else ft.Colors.AMBER_900,
                leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.AMBER, size=40),
                content=ft.Text("⚠️ High temperature alert!", color=text_color),
                actions=[
                    ft.TextButton("Dismiss", on_click=lambda e: self.page.close(alert))
                ],
            )
            self.page.open(alert)


    # ------------------ HELPERS ------------------ #

    def create_info_card(self, icon, label, value, is_dark=False):
        """Create a small info card with icon, label, and value that adapts to theme."""
        text_color = ft.Colors.WHITE if is_dark else ft.Colors.BLACK
        sub_color = ft.Colors.GREY_400 if is_dark else ft.Colors.GREY_700
        card_bg = ft.Colors.BLUE_GREY_900 if is_dark else ft.Colors.BLUE_GREY_50

        return ft.Container(
            bgcolor=card_bg,
            border_radius=10,
            padding=10,
            content=ft.Column(
                [
                    ft.Icon(icon, color=text_color),
                    ft.Text(label, size=14, color=sub_color),
                    ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=text_color),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.page.update()


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)
