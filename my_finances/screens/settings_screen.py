from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.dialog import MDDialog
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock
from database import get_setting, set_setting
from services.backup_service import BackupService
from utils.constants import APP_TITLE, VERSION
import os
from datetime import datetime

class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        from kivymd.uix.toolbar import MDTopAppBar
        toolbar = MDTopAppBar(
            title="Настройки",
            elevation=10,
            left_action_items=[['arrow-left', lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        scroll = ScrollView()
        content = MDBoxLayout(orientation='vertical', spacing=15, size_hint_y=None, padding=10)
        content.bind(minimum_height=content.setter('height'))
        
        # Тема
        theme_card = MDCard(padding=15, spacing=10, orientation='vertical', size_hint_y=None, height=dp(120))
        theme_card.add_widget(MDLabel(text="Внешний вид", font_style="H6"))
        
        theme_box = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(50))
        theme_box.add_widget(MDLabel(text="Темная тема"))
        theme_switch = MDSwitch(active=self.get_theme() == "Dark")
        theme_switch.bind(active=self.on_theme_change)
        theme_box.add_widget(theme_switch)
        theme_card.add_widget(theme_box)
        
        content.add_widget(theme_card)
        
        # Резервное копирование
        backup_card = MDCard(padding=15, spacing=10, orientation='vertical', size_hint_y=None)
        backup_card.add_widget(MDLabel(text="Резервное копирование", font_style="H6"))
        
        backup_btn = MDRaisedButton(text="💾 Создать резервную копию", 
                                   on_release=lambda x: self.create_backup())
        restore_btn = MDRaisedButton(text="🔄 Восстановить из копии", 
                                    on_release=lambda x: self.restore_backup())
        
        backup_card.add_widget(backup_btn)
        backup_card.add_widget(restore_btn)
        backup_card.height = dp(150)
        content.add_widget(backup_card)
        
        # Автосохранение
        auto_backup_card = MDCard(padding=15, spacing=10, orientation='vertical', size_hint_y=None, height=dp(150))
        auto_backup_card.add_widget(MDLabel(text="Автосохранение", font_style="H6"))
        
        auto_box = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(50))
        auto_box.add_widget(MDLabel(text="Автоматический бэкап"))
        auto_switch = MDSwitch(active=get_setting('auto_backup_enabled', 'false') == 'true')
        auto_switch.bind(active=self.on_auto_backup_change)
        auto_box.add_widget(auto_switch)
        auto_backup_card.add_widget(auto_box)
        
        content.add_widget(auto_backup_card)
        
        # О приложении
        about_card = MDCard(padding=15, spacing=10, orientation='vertical', size_hint_y=None, height=dp(120))
        about_card.add_widget(MDLabel(text="О приложении", font_style="H6"))
        about_card.add_widget(MDLabel(text=f"{APP_TITLE}"))
        about_card.add_widget(MDLabel(text=f"Версия {VERSION}"))
        about_card.add_widget(MDLabel(text="© 2024 Все права защищены"))
        content.add_widget(about_card)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def go_back(self):
        self.manager.current = 'home'
    
    def get_theme(self):
        return get_setting('theme', 'Light')
    
    def on_theme_change(self, switch, value):
        theme = "Dark" if value else "Light"
        set_setting('theme', theme)
        self.manager.parent.theme_cls.theme_style = theme
    
    def on_auto_backup_change(self, switch, value):
        set_setting('auto_backup_enabled', 'true' if value else 'false')
    
    def create_backup(self):
        # Определяем путь для бэкапа
        downloads_path = self.get_downloads_path()
        filename = f"finance_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(downloads_path, filename)
        
        result = BackupService.export_to_json(filepath)
        
        dialog = MDDialog(
            title="Резервное копирование",
            text=result['message'],
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
    
    def restore_backup(self):
        from kivymd.uix.filemanager import MDFileManager
        from kivy.core.window import Window
        
        self.file_manager = MDFileManager(
            select_path=self.select_backup_file,
            preview=True,
            ext=['.json']
        )
        self.file_manager.show(self.get_downloads_path())
    
    def select_backup_file(self, path):
        self.file_manager.close()
        
        def confirm_restore():
            result = BackupService.import_from_json(path)
            dialog = MDDialog(
                title="Восстановление данных",
                text=result['message'],
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
        
        from widgets.confirm_dialog import show_confirm
        show_confirm("Восстановление", 
                    "Восстановление заменит все текущие данные. Продолжить?",
                    confirm_restore)
    
    def get_downloads_path(self):
        # Android путь к Downloads
        paths = [
            "/storage/emulated/0/Download",
            "/sdcard/Download",
            "./downloads"
        ]
        
        for path in paths:
            if os.path.exists(path) or path == "./downloads":
                if path == "./downloads" and not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                return path
        
        return "."