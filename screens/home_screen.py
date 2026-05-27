from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.progressbar import MDProgressBar
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import datetime, timedelta
from services.income_service import IncomeService
from services.expense_service import ExpenseService
from services.budget_service import BudgetService
from services.report_service import ReportService
from utils.constants import CURRENCY
from models import Money

class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_period = "month"  # month, quarter, year, custom
        self.custom_start = None
        self.custom_end = None
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Toolbar
        from kivymd.uix.toolbar import MDTopAppBar
        toolbar = MDTopAppBar(
            title="Мои финансы",
            elevation=10,
            right_action_items=[['refresh', lambda x: self.refresh_data()]]
        )
        layout.add_widget(toolbar)
        
        # Scrollable content
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView()
        content = MDBoxLayout(orientation='vertical', spacing=15, size_hint_y=None, padding=10)
        content.bind(minimum_height=content.setter('height'))
        
        # Период
        period_card = MDCard(padding=10, spacing=10, orientation='vertical', size_hint_y=None, height=dp(120))
        period_card.add_widget(MDLabel(text="Период отображения", font_style="H6", size_hint_y=None, height=dp(30)))
        
        period_buttons = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
        periods = [
            ("Месяц", "month"), ("Квартал", "quarter"), 
            ("Год", "year"), ("Произвольно", "custom")
        ]
        
        for text, period in periods:
            btn = MDRaisedButton(
                text=text, 
                size_hint=(0.25, 1),
                on_release=lambda x, p=period: self.change_period(p)
            )
            period_buttons.add_widget(btn)
        
        period_card.add_widget(period_buttons)
        
        # Индикатор периода
        self.period_label = MDLabel(text="", halign="center", size_hint_y=None, height=dp(30))
        period_card.add_widget(self.period_label)
        content.add_widget(period_card)
        
        # Общий баланс
        balance_card = MDCard(padding=15, spacing=5, orientation='vertical', size_hint_y=None, height=dp(120))
        balance_card.md_bg_color = (0.2, 0.6, 0.2, 0.1)
        
        balance_card.add_widget(MDLabel(text="Общий баланс", font_style="H6", halign="center", size_hint_y=None, height=dp(30)))
        self.balance_label = MDLabel(text="0.00 ₽", font_style="H4", halign="center", size_hint_y=None, height=dp(50))
        balance_card.add_widget(self.balance_label)
        
        income_expense = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(30))
        self.income_label = MDLabel(text="Доходы: 0 ₽", halign="center")
        self.expense_label = MDLabel(text="Расходы: 0 ₽", halign="center")
        income_expense.add_widget(self.income_label)
        income_expense.add_widget(self.expense_label)
        balance_card.add_widget(income_expense)
        
        content.add_widget(balance_card)
        
        # Быстрые кнопки
        quick_buttons = MDGridLayout(cols=4, spacing=10, size_hint_y=None, height=dp(120))
        quick_items = [
            ("💰", "Доходы", "incomes"),
            ("💸", "Расходы", "expenses"),
            ("📊", "Отчёты", "reports"),
            ("⚙️", "Настройки", "settings")
        ]
        
        for icon, text, screen_name in quick_items:
            btn_card = MDCard(padding=5, spacing=5, orientation='vertical', 
                             on_release=lambda x, s=screen_name: self.go_to_screen(s))
            btn_card.add_widget(MDLabel(text=icon, font_style="H4", halign="center", size_hint_y=None, height=dp(40)))
            btn_card.add_widget(MDLabel(text=text, halign="center", size_hint_y=None, height=dp(30)))
            quick_buttons.add_widget(btn_card)
        
        content.add_widget(quick_buttons)
        
        # Бюджеты
        budgets_title = MDLabel(text="Активные бюджеты", font_style="H6", size_hint_y=None, height=dp(40))
        content.add_widget(budgets_title)
        
        self.budgets_container = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.budgets_container.bind(minimum_height=self.budgets_container.setter('height'))
        content.add_widget(self.budgets_container)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
        
        # Загрузка данных
        Clock.schedule_once(lambda dt: self.refresh_data(), 0.5)
    
    def change_period(self, period):
        self.current_period = period
        if period == "custom":
            self.show_custom_period_dialog()
        else:
            self.refresh_data()
    
    def show_custom_period_dialog(self):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.picker import MDDatePicker
        from kivymd.uix.button import MDFlatButton
        
        self.custom_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        self.custom_end = datetime.now().strftime("%Y-%m-%d")
        
        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=dp(150))
        
        start_btn = MDRaisedButton(text=f"Начало: {self.custom_start}", on_release=lambda x: self.pick_date('start'))
        end_btn = MDRaisedButton(text=f"Конец: {self.custom_end}", on_release=lambda x: self.pick_date('end'))
        
        content.add_widget(start_btn)
        content.add_widget(end_btn)
        
        dialog = MDDialog(
            title="Произвольный период",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="Применить", on_release=lambda x: self.apply_custom_period(dialog))
            ]
        )
        dialog.open()
        self.period_dialog = dialog
        self.start_btn = start_btn
        self.end_btn = end_btn
    
    def pick_date(self, date_type):
        from kivymd.uix.picker import MDDatePicker
        
        def on_date(date):
            if date_type == 'start':
                self.custom_start = date.strftime("%Y-%m-%d")
                self.start_btn.text = f"Начало: {self.custom_start}"
            else:
                self.custom_end = date.strftime("%Y-%m-%d")
                self.end_btn.text = f"Конец: {self.custom_end}"
        
        date_dialog = MDDatePicker(callback=on_date)
        date_dialog.open()
    
    def apply_custom_period(self, dialog):
        dialog.dismiss()
        self.refresh_data()
    
    def get_date_range(self):
        today = datetime.now()
        
        if self.current_period == "month":
            start = today.replace(day=1).strftime("%Y-%m-%d")
            end = today.strftime("%Y-%m-%d")
            period_text = f"Текущий месяц: {start}"
        elif self.current_period == "quarter":
            quarter = (today.month - 1) // 3
            start = today.replace(month=quarter*3+1, day=1).strftime("%Y-%m-%d")
            end = today.strftime("%Y-%m-%d")
            period_text = f"Текущий квартал: {start} - {end}"
        elif self.current_period == "year":
            start = today.replace(month=1, day=1).strftime("%Y-%m-%d")
            end = today.strftime("%Y-%m-%d")
            period_text = f"Текущий год: {start}"
        else:  # custom
            start = self.custom_start or today.replace(day=1).strftime("%Y-%m-%d")
            end = self.custom_end or today.strftime("%Y-%m-%d")
            period_text = f"Период: {start} - {end}"
        
        return start, end, period_text
    
    def refresh_data(self):
        try:
            start, end, period_text = self.get_date_range()
            self.period_label.text = period_text
            
            # Получаем сводку
            summary = ReportService.get_summary(start, end)
            if summary:
                self.balance_label.text = f"{summary['balance']} {CURRENCY}"
                self.income_label.text = f"Доходы: {summary['income']} {CURRENCY}"
                self.expense_label.text = f"Расходы: {summary['expense']} {CURRENCY}"
            
            # Загружаем бюджеты
            self.load_budgets()
            
        except Exception as e:
            print(f"Ошибка обновления данных: {e}")
            self.balance_label.text = "Ошибка загрузки"
    
    def load_budgets(self):
        try:
            self.budgets_container.clear_widgets()
            budgets = BudgetService.get_all_budgets(include_archived=False)
            
            if not budgets:
                no_budgets = MDLabel(text="Нет активных бюджетов", halign="center", size_hint_y=None, height=dp(40))
                self.budgets_container.add_widget(no_budgets)
                return
            
            for budget in budgets[:5]:  # Показываем только первые 5
                budget_card = MDCard(padding=10, spacing=5, orientation='vertical', size_hint_y=None)
                budget_card.height = dp(100)
                
                # Заголовок
                title_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
                title_box.add_widget(MDLabel(text=budget['name'], font_style="H6"))
                title_box.add_widget(MDLabel(text=f"{budget['amount']} {CURRENCY}", 
                                            halign="right", font_style="H6"))
                budget_card.add_widget(title_box)
                
                # Прогресс
                progress = MDProgressBar(value=budget['progress'], size_hint_y=None, height=dp(10))
                budget_card.add_widget(progress)
                
                # Статистика
                stats_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
                stats_box.add_widget(MDLabel(text=f"Потрачено: {budget['spent']} {CURRENCY}"))
                stats_box.add_widget(MDLabel(text=f"Остаток: {budget['remaining']} {CURRENCY}", 
                                            halign="right"))
                budget_card.add_widget(stats_box)
                
                # Предупреждение о низком остатке
                if budget['remaining_obj'] < Money(budget['amount']) * 0.1 and budget['remaining_obj'].value > 0:
                    warning = MDLabel(text="⚠️ Остаток менее 10% бюджета", 
                                    color=(1, 0.5, 0, 1), size_hint_y=None, height=dp(20))
                    budget_card.add_widget(warning)
                elif budget['remaining_obj'].value <= 0:
                    warning = MDLabel(text="❌ Бюджет превышен!", 
                                    color=(1, 0, 0, 1), size_hint_y=None, height=dp(20))
                    budget_card.add_widget(warning)
                
                self.budgets_container.add_widget(budget_card)
            
            if len(budgets) > 5:
                more_label = MDLabel(text=f"... и еще {len(budgets) - 5} бюджетов", 
                                    halign="center", size_hint_y=None, height=dp(30))
                self.budgets_container.add_widget(more_label)
                
        except Exception as e:
            print(f"Ошибка загрузки бюджетов: {e}")
    
    def go_to_screen(self, screen_name):
        self.manager.current = screen_name