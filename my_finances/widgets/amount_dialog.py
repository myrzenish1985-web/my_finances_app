from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivy.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp

class AmountDialog:
    """Диалог ввода суммы с калькулятором"""
    
    def __init__(self, on_confirm, initial_amount=None):
        self.on_confirm = on_confirm
        self.initial_amount = initial_amount
    
    def show(self):
        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=dp(200))
        
        self.amount_field = MDTextField(
            hint_text="Введите сумму",
            input_filter="float",
            text=str(self.initial_amount) if self.initial_amount else ""
        )
        
        # Простые кнопки для быстрого ввода
        buttons = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(50))
        
        for value in ["100", "500", "1000", "5000"]:
            btn = MDRaisedButton(
                text=value,
                size_hint=(0.25, 1),
                on_release=lambda x, v=value: self.set_amount(v)
            )
            buttons.add_widget(btn)
        
        content.add_widget(self.amount_field)
        content.add_widget(buttons)
        
        self.dialog = MDDialog(
            title="Введите сумму",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="OK", on_release=lambda x: self.confirm())
            ]
        )
        self.dialog.open()
    
    def set_amount(self, value):
        self.amount_field.text = value
    
    def confirm(self):
        amount = self.amount_field.text.strip()
        if not amount:
            amount = "0"
        self.dialog.dismiss()
        if self.on_confirm:
            self.on_confirm(amount)