import flet as ft
import mysql.connector
from db_connection import connect_db

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.center()
    page.window.frameless = True
    page.title = "User Login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.height = 350
    page.window.width = 400
    page.bgcolor = ft.Colors.AMBER_ACCENT

    title = ft.Text(
        "User Login",
        size=20,
        weight=ft.FontWeight.BOLD,
        font_family="Arial",
        text_align=ft.TextAlign.CENTER,
    )

    username_field = ft.TextField(
        label="User name",
        hint_text="Enter your user name",
        helper_text="This is your unique identifier",
        width=300,
        autofocus=True,
        icon=ft.Icons.PERSON,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
    )

    password_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        helper_text="This is your secret key",
        width=300,
        password=True,
        can_reveal_password=True,
        icon=ft.Icons.PASSWORD,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT
    )


    async def login_click(e):

        success_dialog = ft.AlertDialog(
        title=ft.Text("Login Successful", text_align=ft.TextAlign.CENTER),
        content=ft.Text("", text_align=ft.TextAlign.CENTER),
        actions=[ft.TextButton("OK", on_click=lambda e: page.close(success_dialog))],
        icon=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN)
        )
        
        failure_dialog = ft.AlertDialog(
            title=ft.Text("Login Failed", text_align=ft.TextAlign.CENTER),
            content=ft.Text("Invalid username or password", text_align=ft.TextAlign.CENTER),
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(failure_dialog))],
            icon=ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED)
        )
        
        invalid_input_dialog = ft.AlertDialog(
            title=ft.Text("Input Error", text_align=ft.TextAlign.CENTER),
            content=ft.Text("Please enter username and password", text_align=ft.TextAlign.CENTER),
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(invalid_input_dialog))],
            icon=ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE)
        )
        
        database_error_dialog = ft.AlertDialog(
            title=ft.Text("Database Error"),
            content=ft.Text("An error occurred while connecting to the database", text_align=ft.TextAlign.CENTER),
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(database_error_dialog))],
        )

        if not username_field.value or not password_field.value:
            page.open(invalid_input_dialog)
            page.update()
            return

        try:
            connection = connect_db()
            if connection:
                try:
                    cursor = connection.cursor()
                    query = "SELECT * FROM users WHERE username = %s AND password = %s"
                    cursor.execute(query, (username_field.value, password_field.value))
                    result = cursor.fetchone()
                    connection.close()
                except Exception as err:
                    print(f"Cursor/Query Error: {err}")
                    result = None
                    page.open(database_error_dialog)
                    page.update()
            else:
                print("Connection failed.")
                result = None
                page.open(database_error_dialog)
                page.update()

            if result:
                success_dialog.content = ft.Text(f"Welcome, {username_field.value}!", text_align=ft.TextAlign.CENTER)
                page.open(success_dialog)
                print("Success")
                page.update()
            else:
                page.open(failure_dialog)
                print("Not log-in-ed")
                page.update()

        except Exception as err:
            print(f"Database Error: {err}")
            result = None
            page.open(database_error_dialog)
            page.update()
        
        page.update()

    login_button = ft.ElevatedButton(
        text="Login",
        icon=ft.Icons.LOGIN,
        width=100,
        on_click=login_click
    )

    page.add(
        title,
        ft.Container(
            content=ft.Column(
                [username_field, password_field],
                spacing=20
            ),
            margin=ft.margin.only(bottom=20)
        ),
        ft.Container(
            content=login_button,
            alignment=ft.alignment.top_right,
            margin=ft.margin.only(right=40)
        )
    )

ft.app(target=main)