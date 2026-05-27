from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.progressbar import MDProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock
from services.budget_service import BudgetService
from services.expense_service import ExpenseService
from models import Budget
from utils.validators import validate_required, validate_positive_amount
from utils.formatting import format_money
from datetime import datetime

class BudgetsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        from kivymd.uix.toolbar import MDTopAppBar
        toolbar = MDTopAppBar(
            title="Бюджеты",
            elevation=10,
            left_action_items=[['arrow-left', lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        self.list_view = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        scroll = ScrollView()
        scroll.add_widget(self.list_view)
        layout.add_widget(scroll)
        
        add_btn = MDRaisedButton(
            text="+ Создать бюджет",
            size_hint=(1, None),
            height=dp(50),
            on_release=lambda x: self.show_budget_dialog()
        )
        layout.add_widget(add_btn)
        
        self.add_widget(layout)
        Clock.schedule_once(lambda dt: self.load_budgets(), 0.5)
    
    def go_back(self):
        self.manager.current = 'home'
    
    def load_budgets(self):
        self.list_view.clear_widgets()
        budgets = BudgetService.get_all_budgets(include_archived=True)
        
        if not budgets:
            empty_label = MDLabel(text="Нет бюджетов\nНажмите '+' чтобы создать", 
                                 halign="center", size_hint_y=None, height=dp(100))
            self.list_view.add_widget(empty_label)
            return
        
        for budget in budgets:
            budget_card = MDCard(padding=10, spacing=8, orientation='vertical', size_hint_y=None)
            budget_card.height = dp(160)
            
            # Заголовок и статус
            header = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
            header.add_widget(MDLabel(text=budget['name'], font_style="H6"))
            
            status_icon = "checkbox-marked-circle" if budget['is_active'] else "close-circle"
            status_color = (0, 1, 0, 1) if budget['is_active'] else (1, 0, 0, 1)
            status_btn = MDIconButton(icon=status_icon, icon_color=status_color, 
                                     on_release=lambda x, b=budget: self.toggle_budget_status(b))
            header.add_widget(status_btn)
            budget_card.add_widget(header)
            
            # Информация о периоде
            period_text = f"Период: {budget['period_name']}"
            if budget['start_date'] and budget['end_date']:
                period_text += f" ({budget['start_date']} - {budget['end_date']})"
            period_label = MDLabel(text=period_text, font_style="Caption", size_hint_y=None, height=dp(25))
            budget_card.add_widget(period_label)
            
            # Суммы
            amounts = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
            amounts.add_widget(MDLabel(text=f"Бюджет: {format_money(budget['amount'])} ₽"))
            amounts.add_widget(MDLabel(text=f"Остаток: {format_money(budget['remaining'])} ₽", 
                                      halign="right", 
                                      color=(0, 1, 0, 1) if budget['remaining_obj'].value >= 0 else (1, 0, 0, 1)))
            budget_card.add_widget(amounts)
            
            # Прогресс
            progress = MDProgressBar(value=budget['progress'], size_hint_y=None, height=dp(10))
            budget_card.add_widget(progress)
            
            # Расходы
            spent_label = MDLabel(text=f"Потрачено: {budget['spent']} ₽", 
                                 size_hint_y=None, height=dp(25), font_style="Caption")
            budget_card.add_widget(spent_label)
            
            if budget['comment']:
                comment_label = MDLabel(text=f"📝 {budget['comment'][:50]}", 
                                       size_hint_y=None, height=dp(25), font_style="Caption")
                budget_card.add_widget(comment_label)
            
            # Кнопки действий
            actions = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(40))
            
            edit_btn = MDRaisedButton(text="Редактировать", size_hint=(0.5, 1), 
                                     on_release=lambda x, b=budget: self.edit_budget(b))
            delete_btn = MDRaisedButton(text="Удалить", size_hint=(0.5, 1), 
                                       md_bg_color=(1, 0, 0, 0.8),
                                       on_release=lambda x, b=budget: self.delete_budget(b))
            
            actions.add_widget(edit_btn)
            actions.add_widget(delete_btn)
            budget_card.add_widget(actions)
            
            self.list_view.add_widget(budget_card)
    
    def toggle_budget_status(self, budget):
        new_status = not budget['is_active']
        result = BudgetService.update_budget(budget['id'], is_active=new_status)
        if result['success']:
            self.load_budgets()
            self.show_message(f"Бюджет {'активирован' if new_status else 'деактивирован'}")
        else:
            self.show_error(result['message'])
    
    def show_budget_dialog(self, budget=None):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.selectioncontrol import MDCheckbox
        
        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=dp(400))
        
        name_field = MDTextField(hint_text="Название бюджета*")
        amount_field = MDTextField(hint_text="Сумма бюджета*", input_filter="float")
        
        # Период
        period_box = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(50))
        period_label = MDLabel(text="Период:")
        period_select = MDRaisedButton(text="Месяц")
        period_box.add_widget(period_label)
        period_box.add_widget(period_select)
        
        # Даты
        start_date_btn = MDRaisedButton(text="Дата начала")
        start_date_label = MDLabel(text=datetime.now().strftime("%Y-%m-%d"), size_hint_y=None, height=dp(30))
        end_date_btn = MDRaisedButton(text="Дата окончания")
        end_date_label = MDLabel(text="", size_hint_y=None, height=dp(30))
        
        comment_field = MDTextField(hint_text="Комментарий")
        
        content.add_widget(name_field)
        content.add_widget(amount_field)
        content.add_widget(period_box)
        content.add_widget(start_date_btn)
        content.add_widget(start_date_label)
        content.add_widget(end_date_btn)
        content.add_widget(end_date_label)
        content.add_widget(comment_field)
        
        if budget:
            name_field.text = budget['name']
            amount_field.text = budget['amount']
            period_select.text = budget['period_name']
            start_date_label.text = budget['start_date'] or datetime.now().strftime("%Y-%m-%d")
            comment_field.text = budget['comment']
        
        selected_period = budget['period'] if budget else Budget.PERIOD_MONTH
        selected_start_date = budget['start_date'] if budget else datetime.now().strftime("%Y-%m-%d")
        selected_end_date = budget['end_date'] if budget else ""
        
        def change_period():
            nonlocal selected_period
            from kivymd.uix.dialog import MDDialog
            
            periods_dialog = MDDialog(title="Выберите период", type="simple")
            periods_list = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
            periods_list.height = dp(200)
            
            for period_key, period_name in Budget.PERIODS.items():
                btn = MDRaisedButton(
                    text=period_name,
                    on_release=lambda x, pk=period_key, pn=period_name: [
                        periods_dialog.dismiss(),
                        (lambda: (setattr(selected_period, pk, None),
                                 period_select.__setattr__('text', pn)))(None)
                    ][-1]
                )
                periods_list.add_widget(btn)
            
            periods_dialog.add_widget(periods_list)
            periods_dialog.open()
        
        def on_start_date(date):
            nonlocal selected_start_date
            selected_start_date = date.strftime("%Y-%m-%d")
            start_date_label.text = selected_start_date
        
        def on_end_date(date):
            nonlocal selected_end_date
            selected_end_date = date.strftime("%Y-%m-%d")
            end_date_label.text = selected_end_date
        
        period_select.on_release = change_period
        start_date_btn.on_release = lambda: MDDatePicker(callback=on_start_date).open()
        end_date_btn.on_release = lambda: MDDatePicker(callback=on_end_date).open()
        
        dialog = MDDialog(
            title="Создание бюджета" if not budget else "Редактирование бюджета",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="Сохранить", on_release=lambda x: self.save_budget(
                    dialog, name_field.text, amount_field.text, selected_period,
                    selected_start_date, selected_end_date, comment_field.text, budget
                ))
            ]
        )
        dialog.open()
    
    def save_budget(self, dialog, name, amount, period, start_date, end_date, comment, budget=None):
        if not validate_required(name):
            self.show_error("Название бюджета обязательно")
            return
        if not validate_positive_amount(amount):
            self.show_error("Введите корректную сумму бюджета")
            return
        
        if budget:
            result = BudgetService.update_budget(
                budget['id'], name=name, amount=amount, period=period,
                start_date=start_date, end_date=end_date, comment=comment
            )
        else:
            result = BudgetService.create_budget(name, amount, period, start_date, end_date, comment)
        
        dialog.dismiss()
        
        if result['success']:
            self.load_budgets()
            self.show_message(result['message'])
        else:
            self.show_error(result['message'])
    
    def edit_budget(self, budget):
        self.show_budget_dialog(budget)
    
    def delete_budget(self, budget):
        from widgets.confirm_dialog import show_confirm
        
        def on_confirm():
            result = BudgetService.delete_budget(budget['id'])
            if result['success']:
                self.load_budgets()
                self.show_message(result['message'])
            else:
                self.show_error(result['message'])
        
        show_confirm("Удаление бюджета", 
                    f"Удалить бюджет '{budget['name']}'?\nВсе расходы по этому бюджету сохранятся.",
                    on_confirm)
    
    def show_error(self, message):
        from kivymd.toast import toast
        toast(message, duration=2)
    
    def show_message(self, message):
        from kivymd.toast import toast
        toast(message)