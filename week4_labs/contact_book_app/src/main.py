import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact
def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.width = 500
    page.window.height = 880

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        theme_icon_button.icon = ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE
       
        new_color = ft.Colors.WHITE if page.theme_mode == ft.ThemeMode.DARK else ft.Colors.BLACK
        name_input.border_color = new_color
        phone_input.border_color = new_color
        email_input.border_color = new_color
        search_field.border_color = new_color
        
        page.update()

    page.theme_mode = ft.ThemeMode.DARK

    theme_icon_button = ft.IconButton(
        icon = ft.Icons.LIGHT_MODE,
        tooltip = "Toggle Theme",
        on_click = toggle_theme,
    )

    db_conn = init_db()

    name_input = ft.TextField(label="Name", width=550, border_color=ft.Colors.WHITE, icon=ft.Icons.PERSON)
    phone_input = ft.TextField(label="Phone", width=550,  border_color=ft.Colors.WHITE, icon=ft.Icons.PHONE)
    email_input = ft.TextField(label="Email", width=550,  border_color=ft.Colors.WHITE, icon=ft.Icons.EMAIL)

    inputs = (name_input, phone_input, email_input)

    filter_by = "all"

    search_field = ft.TextField(
        label="Search",     
        width=500, 
        border_color=ft.Colors.WHITE,
        icon=ft.Icons.SEARCH,
        hint_text="Search contacts...",
        on_change=lambda e: display_contacts(page, contacts_list_view, db_conn, e.control.value, filter_by),
    )

    def set_filter(e, field):
        nonlocal filter_by
        filter_by = field
        display_contacts(page, contacts_list_view, db_conn, search_field.value, filter_by)

    filter_function = ft.PopupMenuButton(
        icon=ft.Icons.FILTER_LIST,
        items=[
            ft.PopupMenuItem(text="All", on_click=lambda e: set_filter(e, "all")),
            ft.PopupMenuItem(text="Name", on_click=lambda e: set_filter(e, "name")),
            ft.PopupMenuItem(text="Phone Number", on_click=lambda e: set_filter(e, "phone")),
            ft.PopupMenuItem(text="Email", on_click=lambda e: set_filter(e, "email")),
        ]
    )

    contacts_list_view = ft.ListView(expand=1, height=500, spacing=10, auto_scroll=True)

    add_button = ft.ElevatedButton(
        text="Add Contact",
        icon=ft.Icons.ADD,
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn),
        tooltip="Adds a contact.. obviously"
    )

    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Enter Contact Details:",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            expand=True,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        theme_icon_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                name_input,
                phone_input,
                email_input,
                add_button,
                ft.Divider(),
                ft.Row(
                    [
                        ft.TextField(
                            label="Search",
                            hint_text="Search contacts...",
                            icon=ft.Icons.SEARCH,
                            border_color=ft.Colors.WHITE,
                            on_change=lambda e: display_contacts(
                                page, contacts_list_view, db_conn, e.control.value, filter_by
                            )
                        ),
                        filter_function 
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Divider(),
                ft.Text(f"Contacts: ", size=20, weight=ft.FontWeight.BOLD),
                contacts_list_view,
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    display_contacts(page, contacts_list_view, db_conn)

ft.app(target=main, view=ft.WEB_BROWSER, port=8550, host="0.0.0.0")

