from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import datetime, timedelta
from services.report_service import ReportService
from utils.formatting import format_money
from models import Money

class SimpleBarChart(Widget):
    """Простой столбчатый график"""
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.size_hint_y = None
        self.height = dp(300)
        Clock.schedule_once(lambda dt: self.draw())
    
    def draw(self):
        self.canvas.clear()
        if not self.data:
            return
        
        with self.canvas:
            # Фон
            Color(0.95, 0.95, 0.95, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # График
            if len(self.data) == 0:
                return
            
            max_value = max([abs(d['value']) for d in self.data]) if self.data else 1
            if max_value == 0:
                max_value = 1
            
            bar_width = self.width / len(self.data) * 0.7
            spacing = (self.width / len(self.data)) * 0.3
            
            for i, item in enumerate(self.data):
                x = self.x + i * (bar_width + spacing) + spacing/2
                height = (abs(item['value']) / max_value) * (self.height - 40)
                y = self.y + 20
                
                # Цвет: зеленый для положительных, красный для отрицательных
                if item['value'] >= 0:
                    Color(0.2, 0.8, 0.2, 0.8)
                else:
                    Color(0.9, 0.2, 0.2, 0.8)
                
                Rectangle(pos=(x, y), size=(bar_width, height))
                
                # Подпись
                Color(0, 0, 0, 1)
                # Здесь можно добавить текст, но для простоты опустим

class ReportsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        from kivymd.uix.toolbar import MDTopAppBar
        toolbar = MDTopAppBar(
            title="Отчеты",
            elevation=10,
            left_action_items=[['arrow-left', lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        # Выбор периода
        period_card = MDCard(padding=10, spacing=10, orientation='vertical', size_hint_y=None, height=dp(150))
        
        period_buttons = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
        periods = [
            ("Неделя", 7), ("Месяц", 30), ("Квартал", 90), ("Год", 365)
        ]
        
        for text, days in periods:
            btn = MDRaisedButton(
                text=text,
                size_hint=(0.25, 1),
                on_release=lambda x, d=days: self.set_period(d)
            )
            period_buttons.add_widget(btn)
        
        custom_btn = MDRaisedButton(
            text="Произвольно",
            size_hint=(0.25, 1),
            on_release=lambda x: self.show_custom_period()
        )
        period_buttons.add_widget(custom_btn)
        
        period_card.add_widget(period_buttons)
        
        self.period_info = MDLabel(text="", halign="center", size_hint_y=None, height=dp(40))
        period_card.add_widget(self.period_info)
        
        layout.add_widget(period_card)
        
        # Scrollable content
        scroll = ScrollView()
        self.content = MDBoxLayout(orientation='vertical', spacing=15, size_hint_y=None, padding=10)
        self.content.bind(minimum_height=self.content.setter('height'))
        scroll.add_widget(self.content)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
        # Загрузка данных
        self.current_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        self.current_end = datetime.now().strftime("%Y-%m-%d")
        Clock.schedule_once(lambda dt: self.load_report(), 0.5)
    
    def go_back(self):
        self.manager.current = 'home'
    
    def set_period(self, days):
        self.current_end = datetime.now().strftime("%Y-%m-%d")
        self.current_start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        self.load_report()
    
    def show_custom_period(self):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.picker import MDDatePicker
        
        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=dp(120))
        
        start_btn = MDRaisedButton(text="Дата начала")
        start_label = MDLabel(text=self.current_start)
        end_btn = MDRaisedButton(text="Дата окончания")
        end_label = MDLabel(text=self.current_end)
        
        content.add_widget(start_btn)
        content.add_widget(start_label)
        content.add_widget(end_btn)
        content.add_widget(end_label)
        
        selected_start = self.current_start
        selected_end = self.current_end
        
        def on_start(date):
            nonlocal selected_start
            selected_start = date.strftime("%Y-%m-%d")
            start_label.text = selected_start
        
        def on_end(date):
            nonlocal selected_end
            selected_end = date.strftime("%Y-%m-%d")
            end_label.text = selected_end
        
        start_btn.on_release = lambda: MDDatePicker(callback=on_start).open()
        end_btn.on_release = lambda: MDDatePicker(callback=on_end).open()
        
        dialog = MDDialog(
            title="Выберите период",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="Показать", on_release=lambda x: [
                    dialog.dismiss(),
                    (lambda: (setattr(self, 'current_start', selected_start),
                             setattr(self, 'current_end', selected_end),
                             self.load_report()))()
                ][-1])
            ]
        )
        dialog.open()
    
    def load_report(self):
        self.content.clear_widgets()
        
        # Сводка
        summary = ReportService.get_summary(self.current_start, self.current_end)
        if summary:
            summary_card = MDCard(padding=15, spacing=10, orientation='vertical', size_hint_y=None, height=dp(180))
            summary_card.add_widget(MDLabel(text="Сводка за период", font_style="H6"))
            summary_card.add_widget(MDLabel(text=f"Период: {summary['start_date']} - {summary['end_date']}"))
            summary_card.add_widget(MDLabel(text=f"💰 Доходы: {format_money(summary['income'])} ₽", 
                                           color=(0, 1, 0, 1)))
            summary_card.add_widget(MDLabel(text=f"💸 Расходы: {format_money(summary['expense'])} ₽", 
                                           color=(1, 0, 0, 1)))
            summary_card.add_widget(MDLabel(text=f"📊 Баланс: {format_money(summary['balance'])} ₽",
                                           font_style="H6"))
            self.content.add_widget(summary_card)
        
        # Доходы по счетам
        income_by_account = ReportService.get_income_by_account(self.current_start, self.current_end)
        if income_by_account:
            income_card = MDCard(padding=15, spacing=10, orientation='vertical', size_hint_y=None)
            income_card.add_widget(MDLabel(text="Доходы по счетам", font_style="H6"))
            
            for item in income_by_account:
                item_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
                item_box.add_widget(MDLabel(text=item['name']))
                item_box.add_widget(MDLabel(text=f"{format_money(item['total'])} ₽", halign="right"))
                income_card.add_widget(item_box)
            
            income_card.height = dp(50 + len(income_by_account) * 30)
            self.content.add_widget(income_card)
        
        # Расходы по бюджетам
        expenses_by_budget = ReportService.get_expenses_by_budget(self.current_start, self.current_end)
        if expenses_by_budget:
            expense_card = MDCard(padding=15, spacing=10, orientation='vertical', size_hint_y=None)
            expense_card.add_widget(MDLabel(text="Расходы по бюджетам", font_style="H6"))
            
            for item in expenses_by_budget:
                item_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
                item_box.add_widget(MDLabel(text=item['name']))
                item_box.add_widget(MDLabel(text=f"{format_money(item['total'])} ₽", halign="right"))
                expense_card.add_widget(item_box)
            
            expense_card.height = dp(50 + len(expenses_by_budget) * 30)
            self.content.add_widget(expense_card)
        
        # Ежедневный баланс (график)
        daily_balance = ReportService.get_daily_balance(self.current_start, self.current_end)
        if daily_balance and len(daily_balance) > 1:
            chart_card = MDCard(padding=15, spacing=10, orientation='vertical', size_hint_y=None)
            chart_card.add_widget(MDLabel(text="Динамика баланса", font_style="H6"))
            
            # Подготовка данных для графика
            chart_data = []
            for day in daily_balance:
                balance = Money(day['balance'])
                chart_data.append({
                    'label': day['date'][5:],  # MM-DD
                    'value': float(balance.value)
                })
            
            # Упрощенный график
            if len(chart_data) > 20:
                # Если много дней, показываем каждый 3-й
                chart_data = chart_data[::3]
            
            chart = SimpleBarChart(chart_data)
            chart_card.add_widget(chart)
            
            chart_card.height = dp(350)
            self.content.add_widget(chart_card)
        
        # Кнопка экспорта
        export_btn = MDRaisedButton(
            text="📁 Экспорт отчета в JSON",
            size_hint=(1, None),
            height=dp(50),
            on_release=lambda x: self.export_report()
        )
        self.content.add_widget(export_btn)
    
    def export_report(self):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        from android.storage import primary_external_storage_path
        from pathlib import Path
        import os
        
        report_json = ReportService.export_to_json(self.current_start, self.current_end)
        
        if report_json:
            # Сохраняем в Downloads
            downloads_path = str(Path.home() / "storage" / "emulated" / "0" / "Download")
            if not os.path.exists(downloads_path):
                downloads_path = "."
            
            filename = f"finance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(downloads_path, filename)
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(report_json)
                
                dialog = MDDialog(
                    title="Экспорт завершен",
                    text=f"Отчет сохранен в:\n{filepath}",
                    buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
                )
                dialog.open()
            except Exception as e:
                self.show_error(f"Ошибка сохранения: {str(e)}")
        else:
            self.show_error("Не удалось создать отчет")
    
    def show_error(self, message):
        from kivymd.toast import toast
        toast(message, duration=2)