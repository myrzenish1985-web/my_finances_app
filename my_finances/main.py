from kivy.config import Config
Config.set('kivy', 'log_level', 'info')
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '780')

from app import MyFinanceApp

if __name__ == '__main__':
    MyFinanceApp().run()