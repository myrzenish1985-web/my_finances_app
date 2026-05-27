from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.list import MDList, ThreeLineIconListItem, IconLeftWidget, IconRightWidget
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock
from services.transfer_service import TransferService
from services.account_service import AccountService
from utils.validators import validate_positive_amount
from utils.formatting import format_money

class TransfersScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        from kivymd.uix.toolbar import MDTopAppBar
        toolbar = MDTopAppBar(
            title="Переводы",
            elevation=10,
            left_action_items=[['arrow-left', lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        self.list_view = MDList()
        scroll = ScrollView()
        scroll.add_widget(self.list_view)
        layout.add_widget(scroll)
        
        add_btn = MDRaisedButton(
            text="+ Сделать перевод",
            size_hint=(1, None),
            height=dp(50),
            on_release=lambda x: self.show_transfer_dialog()
        )
        layout.add_widget(add_btn)
        
        self.add_widget(layout)
        Clock.schedule_once(lambda dt: self.load_transfers(), 0.5)
    
    def go_back(self):
        self.manager.current = 'home'
    
    def load_transfers(self):
        self.list_view.clear_widgets()
        transfers = TransferService.get_all_transfers()
        
        if not transfers:
            empty_label = MDLabel(text="Нет переводов\nНажмите '+' чтобы сделать перевод", 
                                 halign="center", size_hint_y=None, height=dp(100))
            self.list_view.add_widget(empty_label)
            return
        
        for transfer in transfers:
            item = ThreeLineIconListItem(
                text=f"{transfer['date']} - {transfer['from_name']} → {transfer['to_name']}",
                secondary_text=f"Сумма: {format_money(transfer['amount'])} ₽",
                tertiary_text=f"Комментарий: {transfer['comment'][:30]}" if transfer['comment'] else "Без комментария",
                size_hint_y=None,
                height=dp(80)
            )
            
            icon = IconLeftWidget(icon="swap-horizontal")
            item.add_widget(icon)
            
            delete_btn = IconRightWidget(icon="delete", on_release=lambda x, t=transfer: self.delete_transfer(t))
            item.add_widget(delete_btn)
            
            self.list_view.add_widget(item)
    
    def show_transfer_dialog(self):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.picker import MDDatePicker
        
        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=dp(350))
        
        date_btn = MDRaisedButton(text="Выбрать дату")
        date_label = MDLabel(text="Текущая дата", size_hint_y=None, height=dp(30))
        
        accounts = AccountService.get_all_accounts()
        
        from_btn = MDRaisedButton(text="Откуда")
        from_label = MDLabel(text="Не выбран", size_hint_y=None, height=dp(30))
        
        to_btn = MDRaisedButton(text="Куда")
        to_label = MDLabel(text="Не выбран", size_hint_y=None, height=dp(30))
        
        amount_field = MDTextField(hint_text="Сумма перевода*", input_filter="float")
        comment_field = MDTextField(hint_text="Комментарий")
        
        content.add_widget(date_btn)
        content.add_widget(date_label)
        content.add_widget(from_btn)
        content.add_widget(from_label)
        content.add_widget(to_btn)
        content.add_widget(to_label)
        content.add_widget(amount_field)
        content.add_widget(comment_field)
        
        selected_date = None
        selected_from = None
        selected_from_name = None
        selected_to = None
        selected_to_name = None
        
        def on_date(date):
            nonlocal selected_date
            selected_date = date.strftime("%Y-%m-%d")
            date_label.text = selected_date
        
        def select_account(account_type):
            nonlocal selected_from, selected_from_name, selected_to, selected_to_name
            from kivymd.uix.dialog import MDDialog
            from kivymd.uix.list import MDList, OneLineListItem
            
            account_dialog = MDDialog(title=f"Выберите счет", type="simple")
            account_list = MDList()
            
            for acc in accounts:
                item = OneLineListItem(
                    text=acc['name'],
                    on_release=lambda x, a=acc, at=account_type: [
                        account_dialog.dismiss(),
                        (lambda: (
                            setattr(selected_from, a['id'] if at == 'from' else selected_from, None),
                            setattr(selected_from_name, a['name'] if at == 'from' else selected_from_name, None),
                            setattr(selected_to, a['id'] if at == 'to' else selected_to, None),
                            setattr(selected_to_name, a['name'] if at == 'to' else selected_to_name, None),
                            from_label.__setattr__('text', a['name'] if at == 'from' else from_label.text),
                            to_label.__setattr__('text', a['name'] if at == 'to' else to_label.text)
                        ))(None)
                    ][-1]
                )
                account_list.add_widget(item)
            
            account_dialog.add_widget(account_list)
            account_dialog.open()
        
        date_btn.on_release = lambda: MDDatePicker(callback=on_date).open()
        from_btn.on_release = lambda: select_account('from')
        to_btn.on_release = lambda: select_account('to')
        
        dialog = MDDialog(
            title="Новый перевод",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="Сделать перевод", on_release=lambda x: self.save_transfer(
                    dialog, selected_date, selected_from, selected_to, 
                    amount_field.text, comment_field.text
                ))
            ]
        )
        dialog.open()
    
    def save_transfer(self, dialog, date, from_account, to_account, amount, comment):
        if not date:
            self.show_error("Выберите дату")
            return
        if not from_account or not to_account:
            self.show_error("Выберите счета для перевода")
            return
        if from_account == to_account:
            self.show_error("Счета должны быть разными")
            return
        if not validate_positive_amount(amount):
            self.show_error("Введите корректную сумму")
            return
        
        result = TransferService.add_transfer(date, from_account, to_account, amount, "income", comment)
        
        dialog.dismiss()
        
        if result['success']:
            self.load_transfers()
            self.show_message(result['message'])
        else:
            self.show_error(result['message'])
    
    def delete_transfer(self, transfer):
        from widgets.confirm_dialog import show_confirm
        
        def on_confirm():
            result = TransferService.delete_transfer(transfer['id'])
            if result['success']:
                self.load_transfers()
                self.show_message(result['message'])
            else:
                self.show_error(result['message'])
        
        show_confirm("Удаление перевода", 
                    f"Удалить перевод от {transfer['date']} на сумму {transfer['amount']} ₽?",
                    on_confirm)
    
    def show_error(self, message):
        from kivymd.toast import toast
        toast(message, duration=2)
    
    def show_message(self, message):
        from kivymd.toast import toast
        toast(message)