from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.list import MDList, ThreeLineIconListItem, IconLeftWidget, IconRightWidget
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock
from services.income_service import IncomeService
from services.account_service import AccountService
from utils.validators import validate_required, validate_positive_amount
from utils.formatting import format_money

class IncomesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_sort = "date"
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Toolbar
        from kivymd.uix.toolbar import MDTopAppBar
        toolbar = MDTopAppBar(
            title="Доходы",
            elevation=10,
            left_action_items=[['arrow-left', lambda x: self.go_back()]],
            right_action_items=[['sort', lambda x: self.show_sort_dialog()]]
        )
        layout.add_widget(toolbar)
        
        # Список доходов
        self.list_view = MDList()
        scroll = ScrollView()
        scroll.add_widget(self.list_view)
        layout.add_widget(scroll)
        
        # Кнопка добавления
        add_btn = MDRaisedButton(
            text="+ Добавить доход",
            size_hint=(1, None),
            height=dp(50),
            on_release=lambda x: self.show_income_dialog()
        )
        layout.add_widget(add_btn)
        
        self.add_widget(layout)
        
        # Загрузка данных
        Clock.schedule_once(lambda dt: self.load_incomes(), 0.5)
    
    def go_back(self):
        self.manager.current = 'home'
    
    def show_sort_dialog(self):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        
        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=dp(150))
        
        sort_by_date = MDRaisedButton(text="По дате", on_release=lambda x: self.set_sort("date"))
        sort_by_account = MDRaisedButton(text="По счету", on_release=lambda x: self.set_sort("account"))
        sort_by_amount = MDRaisedButton(text="По сумме", on_release=lambda x: self.set_sort("amount"))
        
        content.add_widget(sort_by_date)
        content.add_widget(sort_by_account)
        content.add_widget(sort_by_amount)
        
        dialog = MDDialog(title="Сортировка", type="custom", content_cls=content)
        dialog.open()
        self.sort_dialog = dialog
    
    def set_sort(self, sort_by):
        self.current_sort = sort_by
        if hasattr(self, 'sort_dialog'):
            self.sort_dialog.dismiss()
        self.load_incomes()
    
    def load_incomes(self):
        self.list_view.clear_widgets()
        
        incomes = IncomeService.get_all_incomes(sort_by=self.current_sort)
        
        if not incomes:
            empty_label = MDLabel(text="Нет доходов\nНажмите '+' чтобы добавить", 
                                 halign="center", size_hint_y=None, height=dp(100))
            self.list_view.add_widget(empty_label)
            return
        
        for income in incomes:
            # Создаем карточку дохода
            item = ThreeLineIconListItem(
                text=f"{income['date']} - {income['account_name']}",
                secondary_text=f"Сумма: {format_money(income['amount'])} ₽",
                tertiary_text=f"Комментарий: {income['comment'][:30]}" if income['comment'] else "Нет комментария",
                size_hint_y=None,
                height=dp(80)
            )
            
            # Иконка
            icon = IconLeftWidget(icon="cash-plus")
            item.add_widget(icon)
            
            # Кнопки действий
            edit_btn = IconRightWidget(icon="pencil", on_release=lambda x, inc=income: self.edit_income(inc))
            delete_btn = IconRightWidget(icon="delete", on_release=lambda x, inc=income: self.delete_income(inc))
            item.add_widget(edit_btn)
            item.add_widget(delete_btn)
            
            self.list_view.add_widget(item)
    
    def show_income_dialog(self, income=None):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.picker import MDDatePicker
        
        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=dp(300))
        
        # Выбор даты
        date_btn = MDRaisedButton(text="Выбрать дату")
        date_label = MDLabel(text=income['date'] if income else "Текущая дата", size_hint_y=None, height=dp(30))
        
        # Счет
        accounts = AccountService.get_all_accounts()
        account_btn = MDRaisedButton(text="Выбрать счет")
        account_label = MDLabel(text=income['account_name'] if income else "Не выбран", size_hint_y=None, height=dp(30))
        
        # Сумма
        amount_field = MDTextField(hint_text="Сумма*", input_filter="float")
        if income:
            amount_field.text = str(income['amount'])
        
        # Комментарий
        comment_field = MDTextField(hint_text="Комментарий")
        if income:
            comment_field.text = income['comment']
        
        content.add_widget(date_btn)
        content.add_widget(date_label)
        content.add_widget(account_btn)
        content.add_widget(account_label)
        content.add_widget(amount_field)
        content.add_widget(comment_field)
        
        selected_date = income['date'] if income else None
        selected_account = income['account_id'] if income else None
        selected_account_name = income['account_name'] if income else None
        
        # Callbacks
        def on_date(date):
            nonlocal selected_date
            selected_date = date.strftime("%Y-%m-%d")
            date_label.text = selected_date
        
        def on_account():
            nonlocal selected_account, selected_account_name
            from kivymd.uix.dialog import MDDialog
            from kivymd.uix.list import MDList, OneLineListItem
            
            account_dialog = MDDialog(title="Выберите счет", type="simple")
            account_list = MDList()
            
            for acc in accounts:
                item = OneLineListItem(text=acc['name'], on_release=lambda x, a=acc: [
                    setattr(account_dialog, 'dismiss', lambda: None)(),
                    (lambda: (setattr(account_dialog, 'dismiss', account_dialog.dismiss))())(),
                    (lambda: (setattr(selected_account, a['id'], None),
                             setattr(selected_account_name, a['name'], None),
                             account_label.__setattr__('text', a['name'])))(None)
                ][-1])
                account_list.add_widget(item)
            
            account_dialog.add_widget(account_list)
            account_dialog.open()
        
        date_btn.on_release = lambda: MDDatePicker(callback=on_date).open()
        account_btn.on_release = on_account
        
        dialog = MDDialog(
            title="Добавление дохода" if not income else "Редактирование дохода",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="Сохранить", on_release=lambda x: self.save_income(
                    dialog, selected_date, selected_account, 
                    amount_field.text, comment_field.text, income
                ))
            ]
        )
        dialog.open()
    
    def save_income(self, dialog, date, account_id, amount, comment, income=None):
        if not date:
            self.show_error("Выберите дату")
            return
        if not account_id:
            self.show_error("Выберите счет")
            return
        if not validate_positive_amount(amount):
            self.show_error("Введите корректную сумму")
            return
        
        if income:
            result = IncomeService.update_income(income['id'], date, account_id, amount, comment)
        else:
            result = IncomeService.add_income(date, account_id, amount, comment)
        
        dialog.dismiss()
        
        if result['success']:
            self.load_incomes()
            self.show_message(result['message'])
        else:
            self.show_error(result['message'])
    
    def edit_income(self, income):
        self.show_income_dialog(income)
    
    def delete_income(self, income):
        from widgets.confirm_dialog import show_confirm
        
        def on_confirm():
            result = IncomeService.delete_income(income['id'])
            if result['success']:
                self.load_incomes()
                self.show_message(result['message'])
            else:
                self.show_error(result['message'])
        
        show_confirm("Удаление дохода", 
                    f"Удалить доход от {income['date']} на сумму {income['amount']} ₽?",
                    on_confirm)
    
    def show_error(self, message):
        from kivymd.toast import toast
        toast(message, duration=2)
    
    def show_message(self, message):
        from kivymd.toast import toast
        toast(message)