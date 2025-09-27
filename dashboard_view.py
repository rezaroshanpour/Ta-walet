# views/dashboard_view.py

import flet as ft
from services import wallet_service, market_service, auth_service

class DashboardView(ft.Column):
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.expand = True
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.build_view()

    def build_view(self):
        self.controls.clear()
        self.controls.append(ft.ProgressRing())
        self.update()

        # --- Data Fetching ---
        user_id = self.app_state.get('id')
        decrypted_mnemonic = auth_service.decrypt_mnemonic(
            self.app_state['encrypted_mnemonic'], self.app_state['password']
        )
        eth_address = wallet_service.get_address_from_mnemonic(decrypted_mnemonic) if decrypted_mnemonic else "خطا"
        
        eth_balance = wallet_service.get_eth_balance(eth_address) if eth_address else 0
        
        db_tracked_wallets = auth_service.get_tracked_wallets(user_id)
        ton_address = next((addr for chain, addr in db_tracked_wallets if chain.upper() == 'TON'), None)
        
        ton_balance = wallet_service.get_ton_balance(ton_address) if ton_address else 0

        portfolio_prices = market_service.get_prices_for_portfolio(['ethereum', 'the-open-network'])
        eth_price_usd = portfolio_prices.get('ethereum', {}).get('usd', 0)
        ton_price_usd = portfolio_prices.get('the-open-network', {}).get('usd', 0)
        
        eth_value_usd = eth_balance * eth_price_usd
        ton_value_usd = ton_balance * ton_price_usd
        total_value_usd = eth_value_usd + ton_value_usd

        # --- UI Components ---
        
        # --- Asset Details Cards (Clickable) ---
        eth_card = ft.Card(
            content=ft.ListTile(
                leading=ft.Icon(ft.icons.CURRENCY_BITCOIN),
                title=ft.Text("Ethereum (ETH)"),
                subtitle=ft.Text(f"{float(eth_balance):.6f} ETH"),
                trailing=ft.Text(f"${eth_value_usd:,.2f}"),
            ),
            on_click=lambda e: self.show_asset_detail("Ethereum", eth_balance, eth_value_usd, eth_address)
        )
        
        ton_card = ft.Card(
            content=ft.ListTile(
                leading=ft.Icon(ft.icons.SEND_TO_MOBILE),
                title=ft.Text("Toncoin (TON)"),
                subtitle=ft.Text(f"{float(ton_balance):.4f} TON"),
                trailing=ft.Text(f"${ton_value_usd:,.2f}"),
            ),
            on_click=lambda e: self.show_asset_detail("Toncoin", ton_balance, ton_value_usd, ton_address)
        )
        
        # --- Total Value Display ---
        total_value_text = ft.Text(f"${total_value_usd:,.2f}", size=32, weight=ft.FontWeight.BOLD)
        
        self.controls.clear()
        self.controls.extend([
            ft.Text("تمام دارایی‌ها", size=24, weight=ft.FontWeight.BOLD),
            total_value_text,
            ft.Text("موجودی کل", color=ft.colors.GREY),
            ft.Divider(height=20),
            eth_card,
            ton_card,
            #
        ])
        self.update()

    def show_asset_detail(self, name, balance, value_usd, address):
        # این تابع صفحه جزئیات هر دارایی را نمایش میدهد
        self.controls.clear()
        
        def copy_address(e):
            self.page.set_clipboard(address)
            self.page.snack_bar = ft.SnackBar(ft.Text("آدرس کپی شد!"), bgcolor=ft.colors.GREEN)
            self.page.snack_bar.open = True
            self.page.update()

        self.controls.extend([
            ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.build_view()),
                ft.Text(name, size=24, weight=ft.FontWeight.BOLD)
            ]),
            ft.Text(f"${float(value_usd):,.2f}", size=28),
            ft.Text(f"{float(balance):.6f}", size=18, color=ft.colors.GREY),
            ft.Divider(height=30),
            ft.Text("آدرس کیف پول:", weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.TextField(value=address, read_only=True, border=ft.InputBorder.NONE, expand=True),
                ft.IconButton(icon=ft.icons.COPY, on_click=copy_address, tooltip="کپی کردن آدرس")
            ]),
            ft.Row([
                ft.ElevatedButton("ارسال", icon=ft.icons.ARROW_UPWARD, expand=True),
                ft.ElevatedButton("دریافت", icon=ft.icons.ARROW_DOWNWARD, expand=True),
            ], alignment=ft.MainAxisAlignment.CENTER),

        ])
        self.update()