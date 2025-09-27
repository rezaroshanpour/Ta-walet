# main.py

import flet as ft
from services import auth_service
from views.auth_view import AuthView
from views.dashboard_view import DashboardView

def main(page: ft.Page):
    page.title = "Taram Wallet"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    app_state = {}

    def on_login_success(state):
        nonlocal app_state
        app_state = state
        page.clean()
        dashboard = DashboardView(app_state)
        page.add(dashboard)
        page.update()

    # Initialize database
    auth_service.init_db()

    # Start with the authentication view
    auth_view = AuthView(on_login_success=on_login_success)
    page.add(auth_view)
    page.update()

# To run the app in a desktop window
if __name__ == "__main__":
    ft.app(target=main)

# To make it available for Flet packaging
# ft.app(target=main, assets_dir="assets")