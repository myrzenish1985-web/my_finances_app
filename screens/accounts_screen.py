from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.list import MDList, ThreeLineIconListItem, IconLeftWidget, IconRightWidget
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock
from services.account_service import AccountService
from utils.validators import validate_required

class AccountsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Toolbar
        from kivymd.uix.toolbar import MDTopAppBar
        toolbar = MDTopAppBar(
            title="Счета доходов",
            elevation=10,
            left_action_items=[['arrow-left', lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        # Список счетов
        self.list_view = MDList()
        scroll = ScrollView()
        scroll.add_widget(self.list_view)
        layout.add_widget(scroll)
        
        # Кнопка добавления
        add_btn = MDRaisedButton(
            text="+ Добавить счет",
            size_hint=(1, None),
            height=dp(50),
            on_release=lambda x: self.show_account_dialog()
        )
        layout.add_widget(add_btn)
        
        self.add_widget(layout)
        
        # Загрузка данных
        Clock.schedule_once(lambda dt: self.load_accounts(), 0.5)
    
    def go_back(self):
        self.manager.current = 'home'
    
    def load_accounts(self):
        self.list_view.clear_widgets()
        
        accounts = AccountService.get_all_accounts(include_archived=False)
        
        if not accounts:
            empty_label = MDLabel(text="Нет счетов доходов\nНажмите '+' чтобы добавить", 
                                 halign="center", size_hint_y=None, height=dp(100))
            self.list_view.add_widget(empty_label)
            return
        
        for account in accounts:
            # Создаем карточку счета
            item = ThreeLineIconListItem(
                text=account['name'],
                secondary_text=f"Комментарий: {account['comment'] or 'нет'}",
                tertiary_text="Активен" if account['is_active'] else "Архивный",
                size_hint_y=None,
                height=dp(80)
            )
            
            # Иконка
            icon = IconLeftWidget(icon="bank")
            item.add_widget(icon)
            
            # Кнопки действий
            edit_btn = IconRightWidget(icon="pencil", on_release=lambda x, a=account: self.edit_account(a))
            delete_btn = IconRightWidget(icon="delete", on_release=lambda x, a=account: self.delete_account(a))
            item.add_widget(edit_btn)
            item.add_widget(delete_btn)
            
            self.list_view.add_widget(item)
    
    def show_account_dialog(self, account=None):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.switch import MDSwitch
        
        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=dp(250))
        
        name_field = MDTextField(hint_text="Название счета*")
        comment_field = MDTextField(hint_text="Комментарий")
        
        active_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        active_label = MDLabel(text="Активен")
        active_switch = MDSwitch(active=True)
        active_box.add_widget(active_label)
        active_box.add_widget(active_switch)
        
        content.add_widget(name_field)
        content.add_widget(comment_field)
        content.add_widget(active_box)
        
        if account:
            name_field.text = account['name']
            comment_field.text = account['comment']
            active_switch.active = account['is_active']
        
        dialog = MDDialog(
            title="Добавление счета" if not account else "Редактирование счета",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="Сохранить", on_release=lambda x: self.save_account(
                    dialog, name_field.text, comment_field.text, active_switch.active, account
                ))
            ]
        )
        dialog.open()
    
    def save_account(self, dialog, name, comment, is_active, account=None):
        if not validate_required(name):
            self.show_error("Название счета обязательно")
            return
        
        if account:
            result = AccountService.update_account(account['id'], name, comment, is_active)
        else:
            result = AccountService.add_account(name, comment, is_active)
        
        dialog.dismiss()
        
        if result['success']:
            self.load_accounts()
            self.show_message(result['message'])
        else:
            self.show_error(result['message'])
    
    def edit_account(self, account):
        self.show_account_dialog(account)
    
    def delete_account(self, account):
        from widgets.confirm_dialog import show_confirm
        
        def on_confirm():
            result = AccountService.delete_account(account['id'])
            if result['success']:
                self.load_accounts()
                self.show_message(result['message'])
            else:
                self.show_error(result['message'])
        
        show_confirm("Удаление счета", 
                    f"Удалить счет '{account['name']}'?\nВсе доходы по этому счету сохранятся, но счет станет недоступным для новых операций.",
                    on_confirm)
    
    def show_error(self, message):
        from kivymd.toast import toast
        toast(message)
    
    def show_message(self, message):
        from kivymd.toast import toast
        toast(message)