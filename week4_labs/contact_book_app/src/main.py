import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.width = 400
    page.window.height = 600

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        theme_icon_button.icon = ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE
       

        new_color = ft.Colors.WHITE if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLACK
        name_input.border_color = new_color
        phone_input.border_color = new_color
        email_input.border_color = new_color
        
        page.update()
    page.theme_mode = ft.ThemeMode.LIGHT

    theme_icon_button = ft.FloatingActionButton(
        icon=ft.Icons.DARK_MODE,
        tooltip="Toggle theme",
        on_click=toggle_theme,
    )

    db_conn = init_db()

    name_input = ft.TextField(label="Name", width=350, border_color=ft.Colors.BLACK)
    phone_input = ft.TextField(label="Phone", width=350,  border_color=ft.Colors.BLACK)
    email_input = ft.TextField(label="Email", width=350,  border_color=ft.Colors.BLACK)

    inputs = (name_input, phone_input, email_input)

    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True)

    add_button = ft.ElevatedButton(
        text="Add Contact",
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn)
    )

    page.add(
        ft.Column(
            [   
                ft.Text("Enter Contact Details:", size=20, weight=ft.FontWeight.BOLD),
                name_input,
                phone_input,
                email_input,
                add_button,
                theme_icon_button,
                ft.Divider(),
                ft.Text("Contacts:", size=20, weight=ft.FontWeight.BOLD),
                contacts_list_view,
            ]
        )
    )

    display_contacts(page, contacts_list_view, db_conn)


if __name__ == "__main__":
    ft.app(target=main)
