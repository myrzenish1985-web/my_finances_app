from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivy.metrics import dp

class CardItem(MDCard):
    """Универсальная карточка для отображения элементов"""
    
    def __init__(self, title="", subtitle="", tertiary_text="", 
                 icon_left="", icon_right="", on_edit=None, on_delete=None, **kwargs):
        super().__init__(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(5),
            size_hint_y=None,
            height=dp(100),
            **kwargs
        )
        
        # Основной контент
        content = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(60))
        
        # Левая иконка
        if icon_left:
            self.icon_left = MDIconButton(icon=icon_left, size_hint=(None, 1), width=dp(40))
            content.add_widget(self.icon_left)
        
        # Текстовые поля
        text_box = MDBoxLayout(orientation='vertical', spacing=dp(5), size_hint_x=1)
        
        self.title_label = MDLabel(text=title, font_style="H6", size_hint_y=None, height=dp(25))
        text_box.add_widget(self.title_label)
        
        if subtitle:
            self.subtitle_label = MDLabel(text=subtitle, font_style="Caption", size_hint_y=None, height=dp(20))
            text_box.add_widget(self.subtitle_label)
        
        if tertiary_text:
            self.tertiary_label = MDLabel(text=tertiary_text, font_style="Caption", 
                                          theme_text_color="Hint", size_hint_y=None, height=dp(20))
            text_box.add_widget(self.tertiary_label)
        
        content.add_widget(text_box)
        
        # Правая иконка (редактирование)
        if icon_right or on_edit:
            self.edit_btn = MDIconButton(icon=icon_right or "pencil", on_release=on_edit)
            content.add_widget(self.edit_btn)
        
        # Кнопка удаления
        if on_delete:
            self.delete_btn = MDIconButton(icon="delete", on_release=on_delete)
            content.add_widget(self.delete_btn)
        
        self.add_widget(content)
    
    def update_text(self, title=None, subtitle=None, tertiary_text=None):
        """Обновление текста в карточке"""
        if title:
            self.title_label.text = title
        if subtitle:
            self.subtitle_label.text = subtitle
        if tertiary_text:
            self.tertiary_label.text = tertiary_text


class BudgetCard(MDCard):
    """Специализированная карточка для бюджетов"""
    
    def __init__(self, budget_data, on_edit=None, on_delete=None, **kwargs):
        super().__init__(
            orientation='vertical',
            padding=dp(12),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(160),
            **kwargs
        )
        
        self.budget_data = budget_data
        
        # Заголовок и статус
        header = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        header.add_widget(MDLabel(text=budget_data['name'], font_style="H6"))
        
        status_icon = "checkbox-marked-circle" if budget_data['is_active'] else "close-circle"
        status_color = (0, 1, 0, 1) if budget_data['is_active'] else (1, 0, 0, 1)
        status_btn = MDIconButton(icon=status_icon, icon_color=status_color)
        header.add_widget(status_btn)
        self.add_widget(header)
        
        # Период
        period_text = f"Период: {budget_data['period_name']}"
        if budget_data.get('start_date') and budget_data.get('end_date'):
            period_text += f" ({budget_data['start_date']} - {budget_data['end_date']})"
        self.add_widget(MDLabel(text=period_text, font_style="Caption", size_hint_y=None, height=dp(25)))
        
        # Суммы
        amounts = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        from utils.formatting import format_money
        amounts.add_widget(MDLabel(text=f"Бюджет: {format_money(budget_data['amount'])} ₽"))
        remaining_color = (0, 1, 0, 1) if budget_data.get('remaining_obj', 0) >= 0 else (1, 0, 0, 1)
        amounts.add_widget(MDLabel(text=f"Остаток: {format_money(budget_data['remaining'])} ₽", 
                                  halign="right", color=remaining_color))
        self.add_widget(amounts)
        
        # Прогресс
        from kivymd.uix.progressbar import MDProgressBar
        progress = MDProgressBar(value=budget_data.get('progress', 0), size_hint_y=None, height=dp(10))
        self.add_widget(progress)
        
        # Кнопки действий
        actions = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        
        if on_edit:
            edit_btn = MDIconButton(icon="pencil", on_release=on_edit)
            actions.add_widget(edit_btn)
        
        if on_delete:
            delete_btn = MDIconButton(icon="delete", on_release=on_delete)
            actions.add_widget(delete_btn)
        
        self.add_widget(actions)


class TransactionCard(MDCard):
    """Специализированная карточка для транзакций (доходов/расходов)"""
    
    def __init__(self, transaction_data, transaction_type="income", on_edit=None, on_delete=None, **kwargs):
        super().__init__(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(5),
            size_hint_y=None,
            height=dp(90),
            **kwargs
        )
        
        content = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(60))
        
        # Иконка
        icon = "cash-plus" if transaction_type == "income" else "cash-minus"
        icon_color = (0, 1, 0, 1) if transaction_type == "income" else (1, 0, 0, 1)
        icon_widget = MDIconButton(icon=icon, icon_color=icon_color, size_hint=(None, 1), width=dp(40))
        content.add_widget(icon_widget)
        
        # Информация
        text_box = MDBoxLayout(orientation='vertical', spacing=dp(3), size_hint_x=1)
        
        from utils.formatting import format_money, format_date
        
        title_text = f"{format_date(transaction_data['date'])} - {transaction_data.get('account_name', transaction_data.get('budget_name', ''))}"
        text_box.add_widget(MDLabel(text=title_text, font_style="Subtitle1", size_hint_y=None, height=dp(25)))
        
        amount_text = f"Сумма: {format_money(transaction_data['amount'])} ₽"
        text_box.add_widget(MDLabel(text=amount_text, font_style="Caption", size_hint_y=None, height=dp(20)))
        
        if transaction_data.get('comment'):
            text_box.add_widget(MDLabel(text=f"📝 {transaction_data['comment'][:30]}", 
                                       font_style="Caption", theme_text_color="Hint", 
                                       size_hint_y=None, height=dp(20)))
        
        content.add_widget(text_box)
        
        # Кнопки действий
        if on_edit:
            edit_btn = MDIconButton(icon="pencil", on_release=on_edit, size_hint=(None, 1), width=dp(40))
            content.add_widget(edit_btn)
        
        if on_delete:
            delete_btn = MDIconButton(icon="delete", on_release=on_delete, size_hint=(None, 1), width=dp(40))
            content.add_widget(delete_btn)
        
        self.add_widget(content)