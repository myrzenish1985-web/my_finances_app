from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen  # ✅ этот импорт уже есть
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from screens.home_screen import HomeScreen
from screens.accounts_screen import AccountsScreen
from screens.incomes_screen import IncomesScreen
from screens.budgets_screen import BudgetsScreen
from screens.expenses_screen import ExpensesScreen
from screens.transfers_screen import TransfersScreen
from screens.reports_screen import ReportsScreen
from screens.settings_screen import SettingsScreen
from utils.constants import APP_TITLE

class BaseScreen(MDScreen):
    """Базовый экран с toolbar и кнопкой назад"""
    def __init__(self, title, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')
        
        self.toolbar = MDTopAppBar(
            title=self.title,
            elevation=10,
            left_action_items=[['arrow-left', lambda x: self.go_back()]],
            right_action_items=[['home', lambda x: self.go_home()]]
        )
        
        self.content = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(self.toolbar)
        layout.add_widget(self.content)
        self.add_widget(layout)
    
    def go_back(self):
        self.manager.current = 'home'
    
    def go_home(self):
        self.manager.current = 'home'

class MyFinanceApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = APP_TITLE
        
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        
        self.sm = ScreenManager()
        
        screens = {
            'home': HomeScreen(name='home'),
            'accounts': AccountsScreen(name='accounts'),
            'incomes': IncomesScreen(name='incomes'),
            'budgets': BudgetsScreen(name='budgets'),
            'expenses': ExpensesScreen(name='expenses'),
            'transfers': TransfersScreen(name='transfers'),
            'reports': ReportsScreen(name='reports'),
            'settings': SettingsScreen(name='settings'),
        }
        
        for name, screen in screens.items():
            self.sm.add_widget(screen)
        
        return self.sm
    
    def on_start(self):
        from database import init_db
        init_db()
        self.load_settings()
    
    def load_settings(self):
        from database import get_setting
        theme = get_setting('theme', 'Light')
        self.theme_cls.theme_style = theme

if __name__ == '__main__':
    MyFinanceApp().run()