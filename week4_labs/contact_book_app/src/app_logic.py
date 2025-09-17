# app_logic.py
import flet as ft
from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db

def display_contacts(page, contacts_list_view, db_conn):
    """Fetches and displays all contacts in the ListView."""
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn)

    for contact in contacts:
        contact_id, name, phone, email = contact

        contacts_list_view.controls.append(
            ft.ListTile(
                title=ft.Text(name),
                subtitle=ft.Text(f"Phone: {phone} | Email: {email}"),
                trailing=ft.PopupMenuButton(
                    icon=ft.Icons.MORE_VERT,
                    items=[
                        ft.PopupMenuItem(
                            text="Edit",
                            icon=ft.Icons.EDIT,
                            on_click=lambda _, c=contact: open_edit_dialog(page, c, db_conn, contacts_list_view)
                    ),
                    ft.PopupMenuItem(),
                    ft.PopupMenuItem(
                        text="Delete",
                        icon=ft.Icons.DELETE,
                        on_click=lambda _, cid=contact_id: delete_contact(page, cid, db_conn, contacts_list_view)
                    ),
                ],
            ),
        )
    )
    page.update()

def add_contact(page, inputs, contacts_list_view, db_conn):
    """Adds a new contact and refreshes the list."""
    name_input, phone_input, email_input = inputs
    
    name_input.error_text = None
    phone_input.error_text = None
    email_input.error_text = None

    if not name_input.value.strip():
        name_input.error_text = "Name cannot be empty."
        page.update()
        return
    if name_input.value.strip():
        if not phone_input.value.strip():
            phone_input.error_text = "Phone must be provided."
            page.update()
            return
        if not email_input.value.strip():
            email_input.error_text = "Email must be provided."
            page.update()
            return
    
    if phone_input.value and not phone_input.value.isdigit():
        phone_input.error_text = "Phone number must contain only digits."
        page.update()
        return
    
    add_contact_db(db_conn, name_input.value, phone_input.value, email_input.value)

    for field in inputs:
        field.value = ""

    display_contacts(page, contacts_list_view, db_conn)
    page.update()

def delete_contact(page: ft.Page, contact_id: int, db_conn: any, contacts_list_view: ft.ListView):
    """Deletes a contact and refreshes the list, handling database errors."""
    try:
        delete_contact_db(db_conn, contact_id)
        page.snack_bar = ft.SnackBar(ft.Text("Contact deleted successfully."), open=True)
        display_contacts(page, contacts_list_view, db_conn)
    except Exception as e:
        page.snack_bar = ft.SnackBar(ft.Text(f"Error deleting contact: {e}"), open=True)

def open_edit_dialog(page: ft.Page, contact: tuple, db_conn: any, contacts_list_view: ft.ListView):
    """Opens a dialog to edit a contact's details and saves changes on confirmation."""
    contact_id, name, phone, email = contact
    
    edit_name = ft.TextField(label="Name", value=name)
    edit_phone = ft.TextField(label="Phone", value=phone)
    edit_email = ft.TextField(label="Email", value=email)

    def save_and_close(e: ft.ControlEvent):
        # ... (validation and update logic)
        try:
            update_contact_db(db_conn, contact_id, edit_name.value, edit_phone.value, edit_email.value)
            page.close(dialog)
            page.update()
            display_contacts(page, contacts_list_view, db_conn)
            page.snack_bar = ft.SnackBar(ft.Text("Contact updated successfully."), open=True)
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error updating contact: {e}"), open=True)
            page.update()
            
    def close_dialog(e):
        page.close(dialog)
        page.update()

    # The delete dialog logic goes here, and it's better to define a helper function for the click
    def confirm_delete(e: ft.ControlEvent):
        delete_contact_db(db_conn, contact_id)
        page.snack_bar = ft.SnackBar(ft.Text("Contact deleted successfully."), open=True)
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)
        
    delete_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Delete Contact"),
        content=ft.Text("Are you sure you want to delete this contact?"),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.TextButton("Delete", on_click=confirm_delete),
        ],
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
        content=ft.Column([edit_name, edit_phone, edit_email]),
        actions=[
            ft.TextButton("Cancel", on_click=close_dialog),
            ft.TextButton("Save", on_click=save_and_close),
        ],
    )
    page.open(dialog)


