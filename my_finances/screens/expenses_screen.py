from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.list import MDList, ThreeLineIconListItem, IconLeftWidget, IconRightWidget
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock
from services.expense_service import ExpenseService
from services.budget_service import BudgetService
from utils.validators import validate_required, validate_positive_amount
from utils.formatting import format_money

class ExpensesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_sort = "date"
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        from kivymd.uix.toolbar import MDTopAppBar
        toolbar = MDTopAppBar(
            title="Расходы",
            elevation=10,
            left_action_items=[['arrow-left', lambda x: self.go_back()]],
            right_action_items=[['sort', lambda x: self.show_sort_dialog()]]
        )
        layout.add_widget(toolbar)
        
        self.list_view = MDList()
        scroll = ScrollView()
        scroll.add_widget(self.list_view)
        layout.add_widget(scroll)
        
        add_btn = MDRaisedButton(
            text="+ Добавить расход",
            size_hint=(1, None),
            height=dp(50),
            on_release=lambda x: self.show_expense_dialog()
        )
        layout.add_widget(add_btn)
        
        self.add_widget(layout)
        Clock.schedule_once(lambda dt: self.load_expenses(), 0.5)
    
    def go_back(self):
        self.manager.current = 'home'
    
    def show_sort_dialog(self):
        from kivymd.uix.dialog import MDDialog
        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=dp(150))
        
        sort_by_date = MDRaisedButton(text="По дате", on_release=lambda x: self.set_sort("date"))
        sort_by_budget = MDRaisedButton(text="По бюджету", on_release=lambda x: self.set_sort("budget"))
        sort_by_amount = MDRaisedButton(text="По сумме", on_release=lambda x: self.set_sort("amount"))
        
        content.add_widget(sort_by_date)
        content.add_widget(sort_by_budget)
        content.add_widget(sort_by_amount)
        
        dialog = MDDialog(title="Сортировка", type="custom", content_cls=content)
        dialog.open()
        self.sort_dialog = dialog
    
    def set_sort(self, sort_by):
        self.current_sort = sort_by
        if hasattr(self, 'sort_dialog'):
            self.sort_dialog.dismiss()
        self.load_expenses()
    
    def load_expenses(self):
        self.list_view.clear_widgets()
        expenses = ExpenseService.get_all_expenses(sort_by=self.current_sort)
        
        if not expenses:
            empty_label = MDLabel(text="Нет расходов\nНажмите '+' чтобы добавить", 
                                 halign="center", size_hint_y=None, height=dp(100))
            self.list_view.add_widget(empty_label)
            return
        
        for expense in expenses:
            item = ThreeLineIconListItem(
                text=f"{expense['date']} - {expense['budget_name']}",
                secondary_text=f"Сумма: {format_money(expense['amount'])} ₽",
                tertiary_text=f"Комментарий: {expense['comment'][:30]}" if expense['comment'] else "Нет комментария",
                size_hint_y=None,
                height=dp(80)
            )
            
            icon = IconLeftWidget(icon="cash-minus")
            item.add_widget(icon)
            
            edit_btn = IconRightWidget(icon="pencil", on_release=lambda x, exp=expense: self.edit_expense(exp))
            delete_btn = IconRightWidget(icon="delete", on_release=lambda x, exp=expense: self.delete_expense(exp))
            item.add_widget(edit_btn)
            item.add_widget(delete_btn)
            
            self.list_view.add_widget(item)
    
    def show_expense_dialog(self, expense=None):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.picker import MDDatePicker
        
        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=dp(300))
        
        date_btn = MDRaisedButton(text="Выбрать дату")
        date_label = MDLabel(text=expense['date'] if expense else "Текущая дата", size_hint_y=None, height=dp(30))
        
        budgets = BudgetService.get_all_budgets(include_archived=False)
        budget_btn = MDRaisedButton(text="Выбрать бюджет")
        budget_label = MDLabel(text=expense['budget_name'] if expense else "Не выбран", size_hint_y=None, height=dp(30))
        
        amount_field = MDTextField(hint_text="Сумма*", input_filter="float")
        if expense:
            amount_field.text = str(expense['amount'])
        
        comment_field = MDTextField(hint_text="Комментарий")
        if expense:
            comment_field.text = expense['comment']
        
        content.add_widget(date_btn)
        content.add_widget(date_label)
        content.add_widget(budget_btn)
        content.add_widget(budget_label)
        content.add_widget(amount_field)
        content.add_widget(comment_field)
        
        selected_date = expense['date'] if expense else None
        selected_budget = expense['budget_id'] if expense else None
        selected_budget_name = expense['budget_name'] if expense else None
        
        def on_date(date):
            nonlocal selected_date
            selected_date = date.strftime("%Y-%m-%d")
            date_label.text = selected_date
        
        def on_budget():
            nonlocal selected_budget, selected_budget_name
            from kivymd.uix.dialog import MDDialog
            from kivymd.uix.list import MDList, OneLineListItem
            
            budget_dialog = MDDialog(title="Выберите бюджет", type="simple")
            budget_list = MDList()
            
            for b in budgets:
                remaining = BudgetService.get_budget_remaining(b['id'])
                item = OneLineListItem(
                    text=f"{b['name']} (остаток: {format_money(remaining)} ₽)",
                    on_release=lambda x, bud=b: [
                        budget_dialog.dismiss(),
                        (lambda: (setattr(selected_budget, bud['id'], None),
                                 setattr(selected_budget_name, bud['name'], None),
                                 budget_label.__setattr__('text', bud['name'])))(None)
                    ][-1]
                )
                budget_list.add_widget(item)
            
            budget_dialog.add_widget(budget_list)
            budget_dialog.open()
        
        date_btn.on_release = lambda: MDDatePicker(callback=on_date).open()
        budget_btn.on_release = on_budget
        
        dialog = MDDialog(
            title="Добавление расхода" if not expense else "Редактирование расхода",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="Сохранить", on_release=lambda x: self.save_expense(
                    dialog, selected_date, selected_budget, 
                    amount_field.text, comment_field.text, expense
                ))
            ]
        )
        dialog.open()
    
    def save_expense(self, dialog, date, budget_id, amount, comment, expense=None):
        if not date:
            self.show_error("Выберите дату")
            return
        if not budget_id:
            self.show_error("Выберите бюджет")
            return
        if not validate_positive_amount(amount):
            self.show_error("Введите корректную сумму")
            return
        
        if expense:
            result = ExpenseService.update_expense(expense['id'], date, budget_id, amount, comment)
        else:
            result = ExpenseService.add_expense(date, budget_id, amount, comment)
        
        dialog.dismiss()
        
        if result['success']:
            self.load_expenses()
            self.show_message(result['message'])
            if 'warning' in result:
                self.show_warning(result['warning'])
        else:
            self.show_error(result['message'])
    
    def edit_expense(self, expense):
        self.show_expense_dialog(expense)
    
    def delete_expense(self, expense):
        from widgets.confirm_dialog import show_confirm
        
        def on_confirm():
            result = ExpenseService.delete_expense(expense['id'])
            if result['success']:
                self.load_expenses()
                self.show_message(result['message'])
            else:
                self.show_error(result['message'])
        
        show_confirm("Удаление расхода", 
                    f"Удалить расход от {expense['date']} на сумму {expense['amount']} ₽?",
                    on_confirm)
    
    def show_error(self, message):
        from kivymd.toast import toast
        toast(message, duration=2)
    
    def show_message(self, message):
        from kivymd.toast import toast
        toast(message)
    
    def show_warning(self, message):
        from kivymd.toast import toast
        toast(message, duration=3)