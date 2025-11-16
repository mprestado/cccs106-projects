import flet as ft
from weather_service import WeatherService
from config import Config, CUSTOM_ICONS
import asyncio
import httpx

class WeatherApp:
    """Main Weather Application class."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.search_history = []
        self.last_weather_data = None 
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
        self.page.run_task(self._auto_fetch_location)

    def get_theme_color(self):
        """Return background color based on current theme."""
        return ft.Colors.BLUE_900 if self.page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLUE_50

    def add_to_history(self, city: str):
        """Add city to search history."""
        if city not in self.search_history:
            self.search_history.insert(0, city)
            self.search_history = self.search_history[:10]  # Keep last 10 cuz y not

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

        if hasattr(self, 'description'):
            is_dark = self.page.theme_mode == ft.ThemeMode.DARK
            new_bg = self.get_background_for_weather(self.description, self.icon_code, is_dark)
            self.weather_container.bgcolor = new_bg
            self.update_display() 
        else:
            self.weather_container.bgcolor = self.get_theme_color()

        self.page.update()

    # ------------------ UI BUILD ------------------ #

    def build_ui(self):
        """Build the user interface."""
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        self.current_unit = 'metric'

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
            text="Toggle °C / °F",
            on_click=self.toggle_units,
            icon=ft.Icons.DEVICE_THERMOSTAT,
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

        self.location_button = ft.ElevatedButton(
            "Use Current Location",
            icon=ft.Icons.MY_LOCATION,
            on_click=lambda e: self.page.run_task(self.get_location_weather),
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700
            )
        )

        self.loading = ft.ProgressRing(visible=False)

        self.history_dropdown = self.build_history_dropdown()

        # Where it all get displayed
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
                        [self.search_button, self.history_dropdown],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row([
                        self.location_button,
                    ]),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                scroll=ft.ScrollMode.ALWAYS,
            )
        )

        if self.page.platform_brightness == ft.Brightness.DARK:
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.update()
    
    # ----------------------- MISC ---------------------- #

    def convert_temp(self, temp: float, from_unit: str = "metric") -> float:
        """
        Convert a temperature between Celsius and Fahrenheit.
        
        from_unit: 'metric' (Celsius) or 'imperial' (Fahrenheit)
        """
        if from_unit == self.current_unit:
            return temp  # No conversion needed

        if from_unit == "metric" and self.current_unit == "imperial":
            # Celsius → Fahrenheit
            return (temp * 9/5) + 32
        elif from_unit == "imperial" and self.current_unit == "metric":
            # Fahrenheit → Celsius
            return (temp - 32) * 5/9

        return temp  # fallback

    def toggle_units(self, e):
        """Toggle between Celsius and Fahrenheit."""
        old_unit = self.current_unit
        self.current_unit = "imperial" if self.current_unit == "metric" else "metric"

        # Convert stored temps
        self.current_temp = self.convert_temp(self.current_temp, from_unit=old_unit)
        self.feels_like = self.convert_temp(self.feels_like, from_unit=old_unit)
        self.temp_min = self.convert_temp(self.temp_min, from_unit=old_unit)
        self.temp_max = self.convert_temp(self.temp_max, from_unit=old_unit)

        self.update_display()

    async def _auto_fetch_location(self):
        await self.get_location_weather(auto_fetch=True)

    async def get_location_weather(self, auto_fetch: bool = False):
        """Get weather for current location (IP-based)."""
        if not auto_fetch:
            self.weather_container.visible = False
            self.error_message.value = "Getting your location..."
            self.error_message.color = ft.Colors.BLUE_700
            self.error_message.visible = True
            self.page.update()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://ipapi.co/json/")
                data = response.json()
                city = data.get("city")
                country = data.get("country_name")

                if not city:
                    if not auto_fetch:
                        self.show_error("Could not determine your location")
                    return

                self.city_input.value = f"{city}, {country}" if country else city
                self.page.update()

                weather_data = await self.weather_service.get_weather(city)
                forecast_data = await self.weather_service.get_forecast(city)

                await self.display_weather(weather_data)
                self.forecast_data = forecast_data
                self.update_display()

                if not auto_fetch:
                    self.error_message.visible = False
                    self.page.update()

        except Exception as e:
            if not auto_fetch:
                self.show_error(f"Could not get your location: {str(e)}")

    # ------------------ WEATHER LOGIC ------------------ #

    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)

    async def get_weather(self):
        """Fetch weather and forecast, then display."""
        city = self.city_input.value.strip()
        if not city:
            self.show_error("Please enter a city name")
            return

        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()

        try:
            # Fetch current weather + forecast
            weather_data = await self.weather_service.get_weather(city)
            forecast_data = await self.weather_service.get_forecast(city)

            self.forecast_data = forecast_data  # store for update_display
            await self.display_weather(weather_data)

            # Add to search history
            self.add_to_history(city)
            self.update_history_dropdown()

        except Exception as e:
            self.show_error(str(e))
        finally:
            self.loading.visible = False
            self.page.update()


    async def display_weather(self, data: dict):
        """Display weather information with dynamic theming."""
        self.last_weather_data = data
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK

        # --- Extract weather data ---
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = self.convert_temp(data.get("main", {}).get("temp", 0))
        temp_max = self.convert_temp(data.get("main", {}).get("temp_max", 0))
        temp_min = self.convert_temp(data.get("main", {}).get("temp_min", 0))
        feels_like = self.convert_temp(data.get("main", {}).get("feels_like", 0))
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        pressure = data.get('main', {}).get('pressure', 0)
        cloudiness = data.get('clouds', {}).get('all', 0)

        # # --- Unit conversion ---
        # if self.current_unit == "imperial":
        #     temp = (temp * 9 / 5) + 32
        #     feels_like = (feels_like * 9 / 5) + 32
        # elif self.current_unit == "metric":
        #     if temp > 200:  # Kelvin fallback
        #         temp -= 273.15
        #         feels_like -= 273.15

        # --- Assign to self ---
        self.current_temp = temp
        self.feels_like = feels_like
        self.city_name = city_name
        self.country = country
        self.humidity = humidity
        self.description = description
        self.icon_code = icon_code
        self.wind_speed = wind_speed
        self.pressure = pressure
        self.cloudiness = cloudiness
        self.temp_max = temp_max
        self.temp_min = temp_min

        # --- Select icon based on theme ---
        icon_folder = "assets/icons_dark" if is_dark else "assets/icons"
        icon_file = CUSTOM_ICONS.get(icon_code, "01d.png")
        self.icon_path = f"{icon_folder}/{icon_file}"

        # --- Animate weather container ---
        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.page.update()

        # --- Build the display ---
        self.update_display()

        # Fade in
        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        self.page.update()

    def update_display(self):
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        text_color = ft.Colors.WHITE if is_dark else ft.Colors.BLACK
        sub_text_color = ft.Colors.GREY_400 if is_dark else ft.Colors.GREY_700
        container_color = self.get_background_for_weather(self.description, self.icon_code, is_dark)
        divider_color = ft.Colors.GREY_700 if is_dark else ft.Colors.GREY_300
        card_color = self.get_background_for_weather(self.description, self.icon_code, is_dark)
        unit_symbol = ' °C' if self.current_unit == 'metric' else ' °F'

        # --- Recompute main icon path for current theme ---
        icon_folder = "assets/icons_dark" if is_dark else "assets/icons"
        icon_file = CUSTOM_ICONS.get(self.icon_code, "01d.png")
        self.icon_path = f"{icon_folder}/{icon_file}"

        # --- Build weather column (main) ---
        weather_column = [
            self.unit_button,
            ft.Text(
                f"{self.city_name}, {self.country}",
                size=20,  # slightly smaller
                weight=ft.FontWeight.BOLD,
                color=text_color,
            ),
            ft.Row(
                [
                    ft.Image(src=self.icon_path, width=80, height=80),  # smaller icon
                    ft.Text(
                        self.description,
                        size=16,  # smaller
                        italic=True,
                        color=text_color,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,  # less space between image and text
            ),
            ft.Text(
                f"{self.current_temp:.1f}{unit_symbol}",
                size=40,
                weight=ft.FontWeight.BOLD,
                color=text_color,
            ),
            ft.Text(
                f"Feels like {self.feels_like:.1f}{unit_symbol}",
                size=14,
                color=sub_text_color,
            ),
            ft.Divider(color=divider_color, thickness=1),
            ft.Row(
                [
                    ft.Text(f"↑ {self.temp_max:.1f}{unit_symbol}", color=text_color),
                    ft.Text(f"↓ {self.temp_min:.1f}{unit_symbol}", color=text_color),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            ft.Row(
                [
                    self.create_info_card(ft.Icons.WATER_DROP, "Humidity", f"{self.humidity}%", is_dark=is_dark, widthint=100, paddingint=5),
                    self.create_info_card(ft.Icons.AIR, "Wind Speed", f"{self.wind_speed} m/s", is_dark=is_dark, widthint=100, paddingint=5),
                    self.create_info_card(ft.Icons.SPEED, "Pressure", f"{self.pressure} hPa", is_dark=is_dark, widthint=100, paddingint=5),
                    self.create_info_card(ft.Icons.CLOUD, "Cloudiness", f"{self.cloudiness}%", is_dark=is_dark, widthint=100, paddingint=5),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
            ),
        ]

        # --- Forecast icons compacted ---
        if hasattr(self, "forecast_data") and self.forecast_data:
            from datetime import datetime
            forecasts = [e for e in self.forecast_data.get("list", []) if "12:00:00" in e["dt_txt"]][:5]
            forecast_cards = []

            for entry in forecasts:
                date = entry["dt_txt"].split(" ")[0]
                day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%a")
                temp = self.convert_temp(entry["main"]["temp"])
                description = entry["weather"][0]["description"].title()
                icon_code = entry["weather"][0]["icon"]
                icon_file = CUSTOM_ICONS.get(icon_code, "01d.png")
                icon_path = f"{icon_folder}/{icon_file}"

                forecast_cards.append(
                    ft.Container(
                        bgcolor=card_color,
                        border_radius=8,
                        padding=5,
                        width=80,
                        content=ft.Column(
                            [
                                ft.Text(day_name, size=14, weight=ft.FontWeight.BOLD, color=text_color),
                                ft.Image(src=icon_path, width=50, height=50),
                                ft.Text(f"{temp:.0f}{unit_symbol}", size=14, color=text_color),
                                ft.Text(description, size=10, color=sub_text_color, text_align=ft.TextAlign.CENTER),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=3,
                        ),
                    )
                )

            weather_column.extend([
                ft.Divider(color=divider_color, thickness=1),
                ft.Text("5-Day Forecast", size=16, weight=ft.FontWeight.BOLD, color=text_color),
                ft.Row(
                    controls=forecast_cards,
                    alignment=ft.MainAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.ALWAYS,
                    spacing=5,
                ),
            ])


        # --- Final container update ---
        self.weather_container.content = ft.Column(
            weather_column,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        self.weather_container.bgcolor = container_color
        self.weather_container.visible = True
        self.error_message.visible = False
        self.page.update()

        # --- High Temp Alert ---
        if (self.current_unit == "metric" and self.current_temp > 35) or \
        (self.current_unit == "imperial" and self.current_temp > 95):
            alert = ft.Banner(
                bgcolor=ft.Colors.AMBER_100 if not is_dark else ft.Colors.AMBER_900,
                leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.AMBER, size=40),
                content=ft.Text("⚠️ High temperature alert!", color=text_color),
                actions=[ft.TextButton("Dismiss", on_click=lambda e: self.page.close(alert))],
            )
            self.page.open(alert)

    def get_background_for_weather(self, description: str, icon_code: str, is_dark: bool) -> str:
        """
        Return container background based on weather, day/night (via icon_code), and theme.
        icon_code examples: '01d' (clear day), '01n' (clear night), '10d' (rain day), etc.
        """
        desc = description.lower()
        is_night = icon_code.endswith("n")

        if "clear" in desc:
            if is_night:
                # Clear night: deep space blue / starry
                return ft.Colors.INDIGO_100 if not is_dark else ft.Colors.INDIGO_900
            else:
                # Sunny day: warm amber/orange
                return ft.Colors.AMBER_100 if not is_dark else ft.Colors.DEEP_ORANGE_900

        elif "cloud" in desc:
            return ft.Colors.GREY_200 if not is_dark else ft.Colors.GREY_800
        elif "rain" in desc or "drizzle" in desc:
            return ft.Colors.LIGHT_BLUE_100 if not is_dark else ft.Colors.BLUE_GREY_900
        elif "thunderstorm" in desc:
            return ft.Colors.GREY_300 if not is_dark else ft.Colors.GREY_900
        elif "snow" in desc:
            return ft.Colors.BLUE_50 if not is_dark else ft.Colors.BLUE_GREY_900
        elif "mist" in desc or "fog" in desc or "haze" in desc:
            return ft.Colors.GREY_100 if not is_dark else ft.Colors.GREY_800
        else:
            return ft.Colors.BLUE_50 if not is_dark else ft.Colors.BLUE_GREY_900

    # ------------------ HELPERS ------------------ #
    async def get_weather_for_city(self, city: str):
        """Fetch and display weather for a given city string."""
        try:
            weather_data = await self.weather_service.get_weather(city)
            forecast_data = await self.weather_service.get_forecast(city)
            await self.display_weather(weather_data)
            self.forecast_data = forecast_data
            self.update_display()
        except Exception as e:
            self.show_error(str(e))

    def create_info_card(self, icon, label, value, is_dark=False, widthint = 100, paddingint = 10):
        """Create a small info card with icon, label, and value that adapts to theme."""
        text_color = ft.Colors.WHITE if is_dark else ft.Colors.BLACK
        sub_color = ft.Colors.GREY_400 if is_dark else ft.Colors.GREY_700
        card_bg = self.get_background_for_weather(self.description, self.icon_code, is_dark)

        return ft.Container(
            width=widthint,
            padding = paddingint,
            bgcolor=card_bg,
            border_radius=10,
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
