from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

def show_confirm(title, text, on_confirm):
    """Показать диалог подтверждения"""
    dialog = MDDialog(
        title=title,
        text=text,
        buttons=[
            MDFlatButton(text="Отмена", on_release=lambda x: dialog.dismiss()),
            MDFlatButton(text="Подтвердить", on_release=lambda x: [dialog.dismiss(), on_confirm()])
        ]
    )
    dialog.open()