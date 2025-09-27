# views/auth_view.py

import flet as ft
from services import auth_service, wallet_service

class AuthView(ft.Column):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.CENTER
        self.spacing = 20
        self.email_field = ft.TextField(label="ایمیل", width=300, text_align=ft.TextAlign.CENTER)
        self.build_email_entry()

    def build_email_entry(self):
        self.controls.clear()
        self.controls.extend([
            ft.Text("Taram Wallet", size=40),
            ft.Text("ورود یا ثبت نام"),
            self.email_field,
            ft.ElevatedButton("ادامه", on_click=self.handle_continue, width=300)
        ])
        self.update()

    def handle_continue(self, e):
        email = self.email_field.value.strip()
        if not email:
            self.page.snack_bar = ft.SnackBar(ft.Text("لطفا ایمیل را وارد کنید."))
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        user_data = auth_service.get_user_by_email(email)
        if user_data:
            self.show_password_login_view(user_data)
        else:
            verification_code = auth_service.send_verification_code(email)
            self.show_verify_code_view(email, verification_code)

    def show_password_login_view(self, user_data):
        password_field = ft.TextField(label="رمز عبور", password=True, can_reveal_password=True, width=300)
        error_text = ft.Text(color=ft.colors.RED)

        def handle_login(e):
            password = password_field.value
            if auth_service.check_password(password, user_data['password_hash']):
                app_state = {**user_data, 'password': password}
                self.on_login_success(app_state)
            else:
                error_text.value = "رمز عبور اشتباه است!"
                self.update()

        self.controls.clear()
        self.controls.extend([
            ft.Text(f"خوش آمدید {user_data['email']}", size=24),
            password_field,
            error_text,
            ft.ElevatedButton("ورود", on_click=handle_login, width=300),
        ])
        self.update()

    def show_verify_code_view(self, email, verification_code):
        code_field = ft.TextField(label="کد ۶ رقمی", width=300, text_align=ft.TextAlign.CENTER)
        error_text = ft.Text(color=ft.colors.RED)

        def handle_verify(e):
            if code_field.value == verification_code:
                self.show_create_password_view(email)
            else:
                error_text.value = "کد وارد شده صحیح نیست!"
                self.update()

        self.controls.clear()
        self.controls.extend([
             ft.Text("تایید کد", size=24),
             ft.Text(f"کد ارسال شده به {email} را وارد کنید"),
             code_field, error_text,
             ft.ElevatedButton("تایید کد", on_click=handle_verify, width=300)
        ])
        self.update()
        
    def show_create_password_view(self, email):
        password_field = ft.TextField(label="یک رمز عبور قوی انتخاب کنید", password=True, can_reveal_password=True, width=300)
        error_text = ft.Text(color=ft.colors.RED)

        def handle_set_password(e):
            password = password_field.value
            if len(password) < 8:
                error_text.value = "رمز عبور باید حداقل ۸ کاراکتر باشد!"
                self.update()
                return
            self.show_seed_phrase_view(email, password)

        self.controls.clear()
        self.controls.extend([
            ft.Text("تنظیم رمز عبور", size=24),
            password_field, error_text,
            ft.ElevatedButton("ادامه", on_click=handle_set_password, width=300)
        ])
        self.update()

    def show_seed_phrase_view(self, email, password):
        _, mnemonic = wallet_service.create_new_wallet()
        password_h = auth_service.hash_password(password)
        encrypted_m = auth_service.encrypt_mnemonic(mnemonic, password)
        auth_service.add_new_user(email, password_h, encrypted_m)
        
        user_data = auth_service.get_user_by_email(email)
        app_state = {**user_data, 'password': password}

        self.controls.clear()
        self.controls.extend([
            ft.Text("عبارت بازیابی", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("این ۱۲ کلمه کلید اصلی کیف پول شماست. آن را در جایی امن یادداشت کنید.", text_align=ft.TextAlign.CENTER),
            ft.Card(content=ft.Container(padding=15, content=ft.Text(mnemonic, size=16, text_align=ft.TextAlign.CENTER))),
            ft.ElevatedButton("ذخیره کردم، ورود به کیف پول", on_click=lambda e: self.on_login_success(app_state), width=300)
        ])
        self.update()