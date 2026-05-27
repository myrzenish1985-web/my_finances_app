from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.picker import MDDatePicker
from kivy.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp

class DatePickerDialog:
    """Диалог выбора даты"""
    
    def __init__(self, on_select, initial_date=None):
        self.on_select = on_select
        self.initial_date = initial_date
    
    def show(self):
        def on_date(date):
            if self.on_select:
                self.on_select(date.strftime("%Y-%m-%d"))
        
        date_picker = MDDatePicker(callback=on_date)
        if self.initial_date:
            from datetime import datetime
            try:
                initial = datetime.strptime(self.initial_date, "%Y-%m-%d")
                date_picker.set_date(initial)
            except:
                pass
        date_picker.open()