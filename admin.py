from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner  # Novo import para o Spinner
from database import Database
from datetime import datetime
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.graphics import Color, Line
from kivy.uix.widget import Widget
import cv2
from kivy.uix.checkbox import CheckBox
from pyzbar.pyzbar import decode
from datetime import datetime
import numpy as np
import threading
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.metrics import dp, sp
from datetime import datetime
import cv2
from pyzbar.pyzbar import decode
from database import Database

from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from kivy.uix.screenmanager import ScreenManager
from settings import AdminSettingsScreen
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
# from forms import ProductForm
# from popups import DetailPopup

# Importações para Excel
import pandas as pd
import xlsxwriter
import os
import threading
import time
from datetime import datetime

import cv2
from pyzbar.pyzbar import decode

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput



Builder.load_string('''

<AdminScreen>:
    product_table: product_table
    search_input: search_input
    category_spinner: category_spinner

    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: 0
        spacing: 0

        # =====================================================
        # HEADER - Navegação Principal
        # =====================================================
        BoxLayout:
            size_hint_y: 0.08
            padding: [20, 0]
            spacing: 0
            canvas.before:
                Color:
                    rgba: 0.2, 0.3, 0.5, 1  # Azul escuro profissional
                Rectangle:
                    pos: self.pos
                    size: self.size

            # Logo/Título à Esquerda
            BoxLayout:
                size_hint_x: 0.25
                padding: [0, 5]

                Label:
                    text: 'Sistema de Inventário'
                    font_size: '20sp'
                    bold: True
                    color: 1, 1, 1, 1
                    halign: 'left'
                    valign: 'middle'
                    text_size: self.size

            # Botões de Navegação no Centro
            BoxLayout:
                size_hint_x: 0.5
                spacing: 15
                padding: [20, 8]

                Button:
                    text: 'Relatórios'
                    size_hint_x: 1
                    bold: True
                    color: 1, 1, 1, 1
                    background_color: 0, 0, 0, 0
                    on_release: root.generate_report()
                    canvas.before:
                        Color:
                            rgba: 0.3, 0.4, 0.6, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [8]

                Button:
                    text: 'Definições'
                    size_hint_x: 1
                    bold: True
                    color: 1, 1, 1, 1
                    background_color: 0, 0, 0, 0
                    on_release: root.go_to_definitions()
                    canvas.before:
                        Color:
                            rgba: 0.3, 0.4, 0.6, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [8]

            # Botão Sair à Direita
            BoxLayout:
                size_hint_x: 0.25
                padding: [0, 8]

                Widget:

                Button:
                    text: '← Sair'
                    size_hint: None, None
                    size: 120, 40
                    bold: True
                    color: 1, 1, 1, 1
                    background_color: 0, 0, 0, 0
                    on_release: root.logout()
                    canvas.before:
                        Color:
                            rgba: 0.9, 0.3, 0.3, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [8]

        # =====================================================
        # BARRA DE TÍTULO E FERRAMENTAS
        # =====================================================
        BoxLayout:
            size_hint_y: 0.08
            padding: [20, 10]
            spacing: 10

            # Título da Seção
            Label:
                text: 'Gestão de Produtos'
                font_size: '22sp'
                bold: True
                size_hint_x: 0.3
                halign: 'left'
                valign: 'middle'
                text_size: self.size
                color: 0.2, 0.2, 0.2, 1

            Widget:
                size_hint_x: 0.1

            # Botões de Ação
            BoxLayout:
                size_hint_x: 0.6
                spacing: 10

                Button:
                    text: 'Filtrar Tipo'
                    bold: True
                    color: 1, 1, 1, 1
                    background_color: 0, 0, 0, 0
                    on_release: root.toggle_kg_products()
                    canvas.before:
                        Color:
                            rgba: 0.8, 0.4, 0.0, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]

                Button:
                    text: '+ Adicionar Produto'
                    bold: True
                    color: 1, 1, 1, 1
                    background_color: 0, 0, 0, 0
                    on_release: root.add_product()
                    canvas.before:
                        Color:
                            rgba: 0.1, 0.7, 0.2, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]

        # =====================================================
        # BARRA DE PESQUISA E FILTROS
        # =====================================================
        BoxLayout:
            size_hint_y: 0.08
            padding: [20, 5, 20, 10]
            spacing: 15

            # Campo de Pesquisa
            TextInput:
                id: search_input
                hint_text: '🔍 Pesquisar por descrição, ID ou código de barras...'
                multiline: False
                padding: [15, 10]
                size_hint_x: 0.65
                background_color: 0, 0, 0, 0
                foreground_color: 0.2, 0.2, 0.2, 1
                cursor_color: 0.2, 0.2, 0.2, 1
                font_size: '15sp'
                on_text: root.filter_products(self.text)
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [10]
                    Color:
                        rgba: 0.7, 0.7, 0.7, 1
                    Line:
                        rounded_rectangle: (*self.pos, *self.size, 10)
                        width: 1.5

            # Filtro de Categorias
            Spinner:
                id: category_spinner
                text: '📁 Todas as Categorias'
                values: ['Todas', 'Eletrônicos', 'Alimentos', 'Vestuário', 'Outros']
                size_hint_x: 0.35
                color: 0.2, 0.2, 0.2, 1
                background_color: 0, 0, 0, 0
                font_size: '15sp'
                on_text: root.filter_products(search_input.text)
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [10]
                    Color:
                        rgba: 0.7, 0.7, 0.7, 1
                    Line:
                        rounded_rectangle: (*self.pos, *self.size, 10)
                        width: 1.5

        # =====================================================
        # TABELA DE PRODUTOS
        # =====================================================
        BoxLayout:
            size_hint_y: 0.76
            padding: [20, 0, 20, 20]

            BoxLayout:
                orientation: 'vertical'
                spacing: 2

                # Header da Tabela (9 colunas)
                GridLayout:
                    cols: 9
                    size_hint_y: None
                    height: 50
                    spacing: 0
                    canvas.before:
                        Color:
                            rgba: 0.2, 0.3, 0.5, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size

                    # Colunas do Header
                    Label:
                        text: 'ID'
                        bold: True
                        size_hint_x: 0.07
                        color: 1, 1, 1, 1

                    Label:
                        text: 'Descrição'
                        bold: True
                        size_hint_x: 0.18
                        color: 1, 1, 1, 1

                    Label:
                        text: 'Estoque'
                        bold: True
                        size_hint_x: 0.09
                        color: 1, 1, 1, 1

                    Label:
                        text: 'Vendido'
                        bold: True
                        size_hint_x: 0.09
                        color: 1, 1, 1, 1

                    Label:
                        text: 'Tipo Venda'
                        bold: True
                        size_hint_x: 0.09
                        color: 1, 1, 1, 1

                    Label:
                        text: 'Preço'
                        bold: True
                        size_hint_x: 0.11
                        color: 1, 1, 1, 1

                    Label:
                        text: 'Lucro'
                        bold: True
                        size_hint_x: 0.11
                        color: 1, 1, 1, 1

                    Label:
                        text: 'Data'
                        bold: True
                        size_hint_x: 0.12
                        color: 1, 1, 1, 1

                    Label:
                        text: 'Ações'
                        bold: True
                        size_hint_x: 0.14
                        color: 1, 1, 1, 1

                # ScrollView com Dados dos Produtos
                ScrollView:
                    do_scroll_x: False
                    do_scroll_y: True
                    bar_width: 10
                    bar_color: 0.2, 0.3, 0.5, 0.8
                    bar_inactive_color: 0.2, 0.3, 0.5, 0.4

                    GridLayout:
                        id: product_table
                        cols: 9
                        size_hint_y: None
                        height: self.minimum_height
                        row_default_height: 40
                        
                        spacing: 0
                        padding: 0
                    ''')
class DetailPopup(Popup):
    def __init__(self, product_data, **kwargs):
        super(DetailPopup, self).__init__(**kwargs)
        self.title = "Detalhes do Produto"
        self.size_hint = (None, None)
        self.background = 'atlas://data/images/defaulttheme/button'
        self.title_color = [0, 0, 0, 1]
        self.title_size = '18sp'
        self.separator_color = [0.5, 0.5, 0.5, 1]
        
        # Definir dimensões iniciais do popup
        self.initial_width = Window.width * 0.75
        self.initial_height = Window.height * 0.80
        self.width = self.initial_width
        self.height = self.initial_height
        
        # Definir dimensões mínimas para o popup
        self.min_width = min(500, Window.width * 0.5)
        self.min_height = min(400, Window.height * 0.5)
        
        # Vincular ao evento de redimensionamento da janela
        Window.bind(on_resize=self.on_window_resize)
        
        # Create a BoxLayout as the main container
        main_layout = BoxLayout(orientation='vertical', padding=[20, 20], spacing=15)
        
        # Adicionar cor de fundo ao main_layout usando canvas
        with main_layout.canvas.before:
            Color(1, 1, 1, 1)  # Branco
            self.main_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        
        # Atualizar o retângulo quando o tamanho ou posição mudar
        main_layout.bind(pos=self._update_rect, size=self._update_rect)
        
        # Criar um ScrollView para conter a tabela
        scroll_view = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        
        # Create table layout
        table_layout = GridLayout(cols=2, spacing=[0, 0], size_hint_y=None)
        table_layout.bind(minimum_height=table_layout.setter('height'))

        # Calculate the remaining stock
        remaining_stock = product_data[2]  # Estoque existente JÁ é o remanescente

        # Calculate profit based on actual sales
        profit_per_unit = product_data[4] - product_data[6]
        total_profit = profit_per_unit * product_data[3]  # Total profit based on units sold

        # Calculate profit percentage (0-100%)
        profit_percentage = 0
        if product_data[6] > 0:  # Avoid division by zero
            profit_percentage = (profit_per_unit / product_data[6]) * 100

        # Peso em KG (índice 15)
        is_sold_by_weight = product_data[15] if len(product_data) > 15 else 0
        
        # Formatação de unidades
        unit = "kg" if is_sold_by_weight else "un"
        stock_text = f"{product_data[2]:.2f} {unit}" if is_sold_by_weight else f"{int(product_data[2])} {unit}"
        sold_text = f"{product_data[3]:.2f} {unit}" if is_sold_by_weight else f"{int(product_data[3])} {unit}"
        remaining_text = f"{remaining_stock:.2f} {unit}" if is_sold_by_weight else f"{int(remaining_stock)} {unit}"

        # Define all fields in a single table
        fields = [
            ("ID", str(product_data[0])),
            ("Descrição", product_data[1]),
            ("Categoria", product_data[11] if len(product_data) > 11 else "N/A"),
            ("Código de Barras", product_data[12] if len(product_data) > 12 and product_data[12] else "N/A"),
            ("Data de Validade", self.format_date(product_data[13]) if len(product_data) > 13 and product_data[13] else "N/A"),
            ("Tipo de Venda", "Por KG" if is_sold_by_weight else "Por Unidade"),  # NOVO CAMPO
            ("Estoque Existente", stock_text),
            ("Estoque Vendido", sold_text),
            ("Estoque Remanescente", remaining_text),
            ("Preço Final de Venda", f"MZN {product_data[4]:.2f}/{unit}"),
            ("Preço de Compra Total", f"MZN {product_data[5]:.2f}"),
            ("Preço de Compra (unitário)", f"MZN {product_data[6]:.2f}/{unit}"),
            ("Lucro por Unidade Vendida", f"MZN {profit_per_unit:.2f}/{unit}"),
            ("Total de Lucro", f"MZN {total_profit:.2f}"),
            ("% de Lucro", f"{profit_percentage:.2f}%"),
            ("Data de Adição", self.format_datetime(str(product_data[14])) if len(product_data) > 14 else "N/A")
        ]

        # Definir quais campos colorir e suas cores (fundo, texto)
        highlight_fields = {
            "Descrição": ([0.2, 0.8, 0.2, 1], [1, 1, 1, 1]),
            "Código de Barras": ([0.3, 0.5, 0.7, 1], [1, 1, 1, 1]),
            "Data de Validade": ([0.9, 0.7, 0.2, 1], [1, 1, 1, 1]),
            "Tipo de Venda": ([0.8, 0.4, 0.0, 1] if is_sold_by_weight else [0.1, 0.5, 0.8, 1], [1, 1, 1, 1]),  # Laranja se KG, Azul se Unidade
            "Estoque Remanescente": ([0.9, 0.6, 0.1, 1], [1, 1, 1, 1]),
            "Total de Lucro": ([0.0, 0.5, 0.8, 1], [1, 1, 1, 1]),
            "% de Lucro": ([0.7, 0.1, 0.7, 1], [1, 1, 1, 1])
        }
        
        # Verificar estoque baixo para destacar em vermelho
        if remaining_stock < 5:
            highlight_fields["Estoque Remanescente"] = ([0.9, 0.1, 0.1, 1], [1, 1, 1, 1])
        
        # Verificar validade próxima (se houver)
        if len(product_data) > 13 and product_data[13]:
            try:
                expiry_date = datetime.strptime(str(product_data[13]), "%Y-%m-%d").date()
                days_until_expiry = (expiry_date - datetime.now().date()).days
                
                if days_until_expiry < 0:
                    # Produto vencido - vermelho
                    highlight_fields["Data de Validade"] = ([0.9, 0.1, 0.1, 1], [1, 1, 1, 1])
                elif days_until_expiry <= 30:
                    # Vence em menos de 30 dias - laranja
                    highlight_fields["Data de Validade"] = ([0.9, 0.5, 0.1, 1], [1, 1, 1, 1])
            except:
                pass
            
        # Verificar lucro baixo para destacar
        if profit_percentage < 15:
            highlight_fields["% de Lucro"] = ([0.9, 0.1, 0.1, 1], [1, 1, 1, 1])
        elif profit_percentage > 50:
            highlight_fields["% de Lucro"] = ([0.1, 0.6, 0.1, 1], [1, 1, 1, 1])

        # Add header row
        header_left = BoxLayout(size_hint_y=None, height=40)
        with header_left.canvas.before:
            Color(0.2, 0.2, 0.4, 1)  # Azul escuro para cabeçalho
            self.header_left_rect = Rectangle(pos=header_left.pos, size=header_left.size)
            Color(0, 0, 0, 1)  # Black border
            self.header_left_line = Line(rectangle=(header_left.x, header_left.y, header_left.width, header_left.height), width=1)
        
        header_left.bind(pos=self._update_header_left, size=self._update_header_left)
        
        header_left.add_widget(Label(
            text="Campo",
            bold=True,
            color=[1, 1, 1, 1],
            size_hint_x=1
        ))
        
        header_right = BoxLayout(size_hint_y=None, height=40)
        with header_right.canvas.before:
            Color(0.2, 0.2, 0.4, 1)
            self.header_right_rect = Rectangle(pos=header_right.pos, size=header_right.size)
            Color(0, 0, 0, 1)
            self.header_right_line = Line(rectangle=(header_right.x, header_right.y, header_right.width, header_right.height), width=1)
        
        header_right.bind(pos=self._update_header_right, size=self._update_header_right)
        
        header_right.add_widget(Label(
            text="Valor",
            bold=True,
            color=[1, 1, 1, 1],
            size_hint_x=1
        ))
        
        table_layout.add_widget(header_left)
        table_layout.add_widget(header_right)
        
        # Lista para armazenar referências aos retângulos e linhas
        self.field_rects = []
        self.field_lines = []
        self.value_rects = []
        self.value_lines = []
        
        # Add all fields to the table
        for i, (field, value) in enumerate(fields):
            # Alternate row colors para campos não destacados
            bg_color = [0.95, 0.95, 0.95, 1] if i % 2 == 0 else [1, 1, 1, 1]
            
            # Field name (left column)
            field_layout = BoxLayout(size_hint_y=None, height=35)
            with field_layout.canvas.before:
                Color(*bg_color)
                rect = Rectangle(pos=field_layout.pos, size=field_layout.size)
                self.field_rects.append(rect)
                Color(0, 0, 0, 1)
                line = Line(rectangle=(field_layout.x, field_layout.y, field_layout.width, field_layout.height), width=1)
                self.field_lines.append(line)
            
            field_layout.rect = rect
            field_layout.line = line
            field_layout.bind(pos=self._update_field_layout, size=self._update_field_layout)
            
            field_layout.add_widget(Label(
                text=field,
                halign='left',
                valign='middle',
                text_size=(200, None),
                bold=True,
                color=[0, 0, 0, 1],
                padding_x=10
            ))
            
            # Field value (right column)
            value_layout = BoxLayout(size_hint_y=None, height=35)
            
            # Determinar se este campo deve ser destacado
            if field in highlight_fields:
                bg_color = highlight_fields[field][0]
                text_color = highlight_fields[field][1]
            else:
                text_color = [0, 0, 0, 1]
            
            with value_layout.canvas.before:
                Color(*bg_color)
                rect = Rectangle(pos=value_layout.pos, size=value_layout.size)
                self.value_rects.append(rect)
                Color(0, 0, 0, 1)
                line = Line(rectangle=(value_layout.x, value_layout.y, value_layout.width, value_layout.height), width=1)
                self.value_lines.append(line)
            
            value_layout.rect = rect
            value_layout.line = line
            value_layout.bind(pos=self._update_value_layout, size=self._update_value_layout)
            
            value_layout.add_widget(Label(
                text=value,
                halign='left',
                valign='middle',
                text_size=(300, None),
                padding_x=10,
                bold=field in highlight_fields,
                color=text_color,
                shorten=True,
                shorten_from='right'
            ))
            
            table_layout.add_widget(field_layout)
            table_layout.add_widget(value_layout)

        # Adicionar a tabela ao ScrollView
        scroll_view.add_widget(table_layout)
        
        # Adicionar o ScrollView ao layout principal
        main_layout.add_widget(scroll_view)
        
        # Create a button layout at the bottom
        button_layout = BoxLayout(
            size_hint_y=None, 
            height=50, 
            spacing=10,
            padding=[0, 10, 0, 0]
        )
        
        # Create close button with styling
        close_btn = Button(
            text="Fechar",
            size_hint=(None, None),
            size=(150, 40),
            background_color=[0.2, 0.2, 0.2, 1],
            color=[1, 1, 1, 1]
        )
        close_btn.bind(on_release=self.dismiss)
        
        # Add close button to button layout
        button_layout.add_widget(BoxLayout())  # Spacer to push button to right
        button_layout.add_widget(close_btn)
        
        # Add button layout to main layout
        main_layout.add_widget(button_layout)
        
        # Set the content of the popup
        self.content = main_layout
        
        # Centralizar o popup na tela
        self.center()

    def on_window_resize(self, instance, width, height):
        """Ajustar o tamanho do popup quando a janela for redimensionada"""
        new_width = width * 0.75
        new_height = height * 0.80
        
        self.width = max(self.min_width, new_width)
        self.height = max(self.min_height, new_height)
        
        self.center()
        
    def center(self):
        """Centralizar o popup na tela"""
        self.pos = ((Window.width - self.width) / 2, (Window.height - self.height) / 2)

    def _update_rect(self, instance, value):
        """Atualizar o retângulo do main_layout quando o tamanho ou posição mudar"""
        self.main_rect.pos = instance.pos
        self.main_rect.size = instance.size
    
    def _update_header_left(self, instance, value):
        """Atualizar o retângulo e linha do header_left"""
        self.header_left_rect.pos = instance.pos
        self.header_left_rect.size = instance.size
        self.header_left_line.rectangle = (instance.x, instance.y, instance.width, instance.height)
    
    def _update_header_right(self, instance, value):
        """Atualizar o retângulo e linha do header_right"""
        self.header_right_rect.pos = instance.pos
        self.header_right_rect.size = instance.size
        self.header_right_line.rectangle = (instance.x, instance.y, instance.width, instance.height)
    
    def _update_field_layout(self, instance, value):
        """Atualizar o retângulo e linha do field_layout"""
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
        instance.line.rectangle = (instance.x, instance.y, instance.width, instance.height)
    
    def _update_value_layout(self, instance, value):
        """Atualizar o retângulo e linha do value_layout"""
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
        instance.line.rectangle = (instance.x, instance.y, instance.width, instance.height)

    def format_datetime(self, datetime_str):
        """Format the date and time to DD/MM/YYYY HH:MM"""
        try:
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d/%m/%Y %H:%M")
        except ValueError:
            return "Data Inválida"
    
    def format_date(self, date_str):
        """Format the expiry date to DD/MM/YYYY"""
        try:
            # Try to parse as full datetime first
            dt = datetime.strptime(str(date_str), "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            try:
                # Try to parse as date only
                dt = datetime.strptime(str(date_str), "%Y-%m-%d")
                return dt.strftime("%d/%m/%Y")
            except ValueError:
                return str(date_str)
            
    def on_dismiss(self):
        """Desvincula os eventos quando o popup é fechado"""
        Window.unbind(on_resize=self.on_window_resize)
        return super(DetailPopup, self).on_dismiss()
                



class ProductForm(Popup):
    """
    Formulário para adicionar/editar produtos com scanner de código de barras integrado.
    
    Features:
    - Scanner de código de barras em tempo real usando OpenCV e pyzbar
    - Suporte para múltiplas câmeras
    - Sistema de detecção otimizado (mesmo do ModernSalesScreen)
    - Validação de dados completa
    - Interface responsiva e profissional
    """
    
    def __init__(self, admin_screen, product=None, **kwargs):
        super(ProductForm, self).__init__(**kwargs)
        
        # Referências
        self.admin_screen = admin_screen
        self.product = product
        
        # Controle da câmera e scanner (igual ao ModernSalesScreen)
        self.scanning = False
        self.camera_capture = None
        self.current_camera = 0
        self.last_barcode = None
        self.last_barcode_time = 0
        
        # Configuração do popup
        self._setup_popup()
        
        # Construir interface
        self._build_ui()
        
        # Preencher dados se estiver editando
        if self.product:
            self._populate_fields()
        
        # Bind de eventos
        Window.bind(on_resize=self._on_window_resize)
    
    # ==================== CONFIGURAÇÃO ====================
    
    def _setup_popup(self):
        """Configurar propriedades básicas do popup"""
        self.title = "Adicionar Produto" if not self.product else "Editar Produto"
        
        window_width, window_height = Window.size
        popup_width = min(dp(1100), window_width * 0.95)
        popup_height = min(dp(800), window_height * 0.9)
        
        self.size = (popup_width, popup_height)
        self.size_hint = (None, None)
        self.auto_dismiss = False
        self.background_color = (1, 1, 1, 1)
    
    # ==================== CONSTRUÇÃO DA UI ====================
    
    def _build_ui(self):
        """Construir interface completa"""
        main_container = BoxLayout(
            orientation='horizontal',
            spacing=dp(15),
            padding=[dp(15), dp(15)]
        )
        
        # Seção da câmera (esquerda)
        camera_section = self._build_camera_section()
        main_container.add_widget(camera_section)
        
        # Seção do formulário (direita)
        form_section = self._build_form_section()
        main_container.add_widget(form_section)
        
        self.content = main_container
    
    def _build_camera_section(self):
        """Construir seção da câmera"""
        section = BoxLayout(
            orientation='vertical',
            size_hint_x=0.4,
            spacing=dp(10)
        )
        
        # Título
        title = Label(
            text='📷 Scanner de Código de Barras',
            size_hint_y=None,
            height=dp(40),
            color=[0.1, 0.1, 0.1, 1],
            font_size=sp(16),
            bold=True,
            halign='center',
            valign='middle'
        )
        section.add_widget(title)
        
        # Container da câmera com fundo
        camera_container = BoxLayout(
            size_hint_y=0.65,
            padding=dp(2)
        )
        
        with camera_container.canvas.before:
            Color(0.89, 0.89, 0.89, 1)
            self.camera_outer_border = RoundedRectangle(
                pos=camera_container.pos,
                size=camera_container.size,
                radius=[dp(6)]
            )
        
        camera_container.bind(
            pos=self._update_camera_outer,
            size=self._update_camera_outer
        )
        
        camera_inner = BoxLayout(padding=0)
        with camera_inner.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.camera_bg = RoundedRectangle(
                pos=camera_inner.pos,
                size=camera_inner.size,
                radius=[dp(5)]
            )
        camera_inner.bind(
            pos=self._update_camera_bg,
            size=self._update_camera_bg
        )
        
        # Widget de imagem para exibir frames da câmera
        self.camera_image = Image(
            allow_stretch=True,
            keep_ratio=True
        )
        
        camera_inner.add_widget(self.camera_image)
        camera_container.add_widget(camera_inner)
        section.add_widget(camera_container)
        
        # Status do scanner
        self.scanner_status = Label(
            text='⚫ Câmera Inativa',
            size_hint_y=None,
            height=dp(35),
            color=[0.5, 0.5, 0.5, 1],
            font_size=sp(14),
            bold=True,
            halign='center',
            valign='middle'
        )
        section.add_widget(self.scanner_status)
        
        # Botões de controle
        buttons_layout = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        self.scan_btn = Button(
            text='▶️ INICIAR',
            background_color=(0.16, 0.66, 0.26, 1),
            color=(1, 1, 1, 1),
            bold=True,
            background_normal='',
            font_size=sp(15)
        )
        self.scan_btn.bind(on_release=self._toggle_scanner)
        
        self.switch_camera_btn = Button(
            text='🔄 TROCAR CÂMERA',
            background_color=(0.26, 0.46, 0.66, 1),
            color=(1, 1, 1, 1),
            bold=True,
            background_normal='',
            font_size=sp(15)
        )
        self.switch_camera_btn.bind(on_release=self._switch_camera)
        
        buttons_layout.add_widget(self.scan_btn)
        buttons_layout.add_widget(self.switch_camera_btn)
        section.add_widget(buttons_layout)
        
        # Instruções
        instructions = Label(
            text='💡 Ligue a câmera e posicione\no código de barras na frente',
            size_hint_y=None,
            height=dp(50),
            color=[0.4, 0.4, 0.4, 1],
            font_size=sp(12),
            halign='center',
            valign='middle'
        )
        section.add_widget(instructions)
        
        return section
    
    def _update_camera_outer(self, instance, value):
        """Atualizar borda externa da câmera"""
        self.camera_outer_border.pos = instance.pos
        self.camera_outer_border.size = instance.size
    
    def _update_camera_bg(self, instance, value):
        """Atualizar fundo da câmera"""
        self.camera_bg.pos = instance.pos
        self.camera_bg.size = instance.size
    
    def _build_form_section(self):
        """Construir seção do formulário"""
        section = BoxLayout(
            orientation='vertical',
            size_hint_x=0.6,
            spacing=dp(10)
        )
        
        # Título
        title = Label(
            text='📝 Dados do Produto',
            size_hint_y=None,
            height=dp(40),
            color=[0.1, 0.1, 0.1, 1],
            font_size=sp(16),
            bold=True,
            halign='left',
            valign='middle',
            text_size=(None, None),
            padding=[dp(10), 0]
        )
        section.add_widget(title)
        
        # ScrollView com campos
        scroll = ScrollView()
        form_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            padding=[dp(10), dp(5)],
            size_hint_y=None
        )
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Criar campos
        self._create_form_fields()
        
        # Grid de campos
        fields_grid = self._build_fields_grid()
        form_layout.add_widget(fields_grid)
        
        # Botões de ação
        buttons = self._build_action_buttons()
        form_layout.add_widget(buttons)
        
        scroll.add_widget(form_layout)
        section.add_widget(scroll)
        
        return section
    
    def _create_form_fields(self):
        """Criar todos os campos do formulário"""
        # Código de barras (readonly)
        self.barcode_input = TextInput(
            multiline=False,
            readonly=True,
            height=dp(40),
            size_hint_y=None,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            padding=[dp(10), dp(10), 0, 0],
            font_size=sp(15),
            hint_text="Será detectado automaticamente"
        )
        
        # Data de validade
        self.expiry_date = TextInput(
            hint_text="DD/MM/AAAA",
            multiline=False,
            height=dp(40),
            size_hint_y=None,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            padding=[dp(10), dp(10), 0, 0],
            font_size=sp(15)
        )
        
        # Descrição
        self.description = TextInput(
            hint_text="Nome do produto",
            multiline=False,
            height=dp(40),
            size_hint_y=None,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            padding=[dp(10), dp(10), 0, 0],
            font_size=sp(15)
        )
        
        # Categoria com botão adicionar
        self.category_layout = self._build_category_field()
        
        # Estoque existente
        self.existing_stock = TextInput(
            hint_text="Quantidade",
            multiline=False,
            input_filter='float',
            height=dp(40),
            size_hint_y=None,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            font_size=sp(15)
        )
        
        # Estoque vendido (readonly)
        self.sold_stock = TextInput(
            multiline=False,
            input_filter='float',
            height=dp(40),
            size_hint_y=None,
            readonly=True,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.3, 0.3, 0.3, 1),
            font_size=sp(15),
            text="0"
        )
        
        # Switch vendido por peso
        self.weight_switch_layout = self._build_weight_switch()
        
        # Preços
        self.sale_price = TextInput(
            hint_text="Preço de venda",
            multiline=False,
            input_filter='float',
            height=dp(40),
            size_hint_y=None,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            font_size=sp(15)
        )
        
        self.total_purchase_price = TextInput(
            hint_text="Preço compra total",
            multiline=False,
            input_filter='float',
            height=dp(40),
            size_hint_y=None,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            font_size=sp(15)
        )
        
        self.unit_purchase_price = TextInput(
            hint_text="Preço unitário",
            multiline=False,
            input_filter='float',
            height=dp(40),
            size_hint_y=None,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            font_size=sp(15)
        )
    
    def _build_category_field(self):
        """Construir campo de categoria com botão adicionar"""
        layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(5)
        )
        
        categories = [
            c for c in self.admin_screen.category_spinner.values
            if c != 'Todas'
        ]
        
        self.category_spinner = Spinner(
            text='Selecionar',
            values=categories,
            size_hint_x=0.8,
            background_color=(1, 1, 1, 1),
            color=(0.1, 0.1, 0.1, 1),
            font_size=sp(15),
            background_normal=''
        )
        
        add_category_btn = Button(
            text="+",
            size_hint_x=0.2,
            background_color=(0.3, 0.7, 0.3, 1),
            color=(1, 1, 1, 1),
            bold=True,
            background_normal=''
        )
        add_category_btn.bind(on_release=self._show_category_form)
        
        layout.add_widget(self.category_spinner)
        layout.add_widget(add_category_btn)
        
        return layout
    
    def _build_weight_switch(self):
        """Construir switch de vendido por peso"""
        layout = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        
        layout.add_widget(Label(
            text="⚖️ Vendido por KG",
            size_hint_x=0.6,
            halign='left',
            valign='middle',
            text_size=(None, None),
            color=[0.1, 0.1, 0.1, 1],
            font_size=sp(15)
        ))
        
        self.is_sold_by_weight_switch = CheckBox(
            size_hint_x=0.2,
            active=False
        )
        layout.add_widget(self.is_sold_by_weight_switch)
        layout.add_widget(Label(size_hint_x=0.2))
        
        return layout
    
    def _build_fields_grid(self):
        """Construir grid com todos os campos"""
        grid = GridLayout(
            cols=2,
            spacing=[dp(10), dp(12)],
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter('height'))
        
        fields = [
            ("Código de Barras", self.barcode_input),
            ("Data de Validade", self.expiry_date),
            ("Descrição*", self.description),
            ("Categoria*", self.category_layout),
            ("Estoque Existente*", self.existing_stock),
            ("Estoque Vendido", self.sold_stock),
            ("", self.weight_switch_layout),
            ("Preço de Venda*", self.sale_price),
            ("Preço Compra Total*", self.total_purchase_price),
            ("Preço Compra Unit.*", self.unit_purchase_price)
        ]
        
        for label_text, widget in fields:
            label = Label(
                text=label_text,
                size_hint_y=None,
                height=dp(40),
                halign='left',
                valign='middle',
                text_size=(dp(150), None),
                bold='*' in label_text,
                font_size=sp(14),
                color=[0.1, 0.1, 0.1, 1]
            )
            grid.add_widget(label)
            grid.add_widget(widget)
        
        return grid
    
    def _build_action_buttons(self):
        """Construir botões de ação"""
        layout = BoxLayout(
            spacing=dp(12),
            size_hint_y=None,
            height=dp(50),
            padding=[0, dp(15), 0, 0]
        )
        
        cancel_btn = Button(
            text="❌ Cancelar",
            background_color=(0.7, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            bold=True,
            background_normal=''
        )
        cancel_btn.bind(on_release=self.dismiss)
        
        save_btn = Button(
            text="✅ Salvar",
            background_color=(0.2, 0.7, 0.3, 1),
            color=(1, 1, 1, 1),
            bold=True,
            background_normal=''
        )
        save_btn.bind(on_release=self._save_product)
        
        layout.add_widget(cancel_btn)
        layout.add_widget(save_btn)
        
        return layout
    
    # ==================== CONTROLE DA CÂMERA (MESMO SISTEMA DO MODERNSALESSCREEN) ====================
    
    def _toggle_scanner(self, instance):
        """Ligar/desligar scanner (igual ao ModernSalesScreen)"""
        if not self.scanning:
            self.scanning = True
            self.scan_btn.text = '⏹️ PARAR'
            self.scan_btn.background_color = (0.88, 0.26, 0.26, 1)
            self.scanner_status.text = '🟢 Scanner Ativo'
            self.scanner_status.color = (0.16, 0.72, 0.22, 1)
            Clock.schedule_interval(self._update_camera, 1.0/15.0)
        else:
            self.scanning = False
            self.scan_btn.text = '▶️ INICIAR'
            self.scan_btn.background_color = (0.16, 0.66, 0.26, 1)
            self.scanner_status.text = '⚫ Scanner Inativo'
            self.scanner_status.color = (0.5, 0.5, 0.5, 1)
            Clock.unschedule(self._update_camera)
            if self.camera_capture:
                self.camera_capture.release()
                self.camera_capture = None
            self.camera_image.texture = None
    
    def _update_camera(self, dt):
        """Atualizar câmera e detectar códigos (IDÊNTICO ao ModernSalesScreen)"""
        if not self.scanning:
            return
        
        # Inicializar câmera se necessário
        if self.camera_capture is None:
            try:
                self.camera_capture = cv2.VideoCapture(self.current_camera)
                self.camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                if not self.camera_capture.isOpened():
                    self.scanner_status.text = '❌ Erro na Câmera'
                    self.scanner_status.color = [0.9, 0.2, 0.2, 1]
                    self.scanning = False
                    self.scan_btn.text = '▶️ INICIAR'
                    self.scan_btn.background_color = (0.16, 0.66, 0.26, 1)
                    return
                
                self.last_barcode = None
                self.last_barcode_time = 0
                
            except Exception as e:
                print(f"❌ Erro ao inicializar câmera: {e}")
                return
        
        # Capturar frame
        ret, frame = self.camera_capture.read()
        
        if not ret:
            return
        
        try:
            current_time = time.time()
            
            # Melhorar qualidade do frame
            frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
            
            # Decodificar códigos de barras
            codes = decode(frame)
            
            if codes:
                for code in codes:
                    try:
                        # Extrair código
                        barcode_raw = code.data.decode('utf-8')
                        barcode_value = ''.join(
                            c for c in barcode_raw if c.isprintable()
                        ).strip()
                        
                        # Evitar detecções duplicadas (cooldown de 2 segundos)
                        if (barcode_value == self.last_barcode and 
                            (current_time - self.last_barcode_time) < 2):
                            continue
                        
                        self.last_barcode = barcode_value
                        self.last_barcode_time = current_time
                        
                        print(f"\n{'='*70}")
                        print(f"📷 CÓDIGO DETECTADO: '{barcode_value}'")
                        print(f"{'='*70}\n")
                        
                        # Atualizar status
                        self.scanner_status.text = '✅ Código Detectado'
                        self.scanner_status.color = [0.16, 0.72, 0.22, 1]
                        
                        # Atualizar campo de código de barras
                        self.barcode_input.text = barcode_value
                        
                        # Mostrar mensagem de sucesso
                        self.admin_screen.show_popup(
                            "Sucesso",
                            f"Código detectado: {barcode_value}"
                        )
                        
                        # Desenhar retângulo verde no código
                        pts = code.polygon
                        if len(pts) == 4:
                            pts = [(int(p.x), int(p.y)) for p in pts]
                            cv2.polylines(
                                frame,
                                [np.array(pts, dtype=np.int32)],
                                True,
                                (0, 255, 0),
                                3
                            )
                        
                        # Desenhar texto com o código
                        x, y, w, h = code.rect
                        cv2.putText(
                            frame,
                            barcode_value,
                            (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2
                        )
                        
                    except Exception as e:
                        print(f"❌ Erro ao processar código: {e}")
                        continue
            
            else:
                # Resetar status após 2.5 segundos sem detecção
                if (current_time - self.last_barcode_time) > 2.5:
                    self.scanner_status.text = '🟢 Scanner Ativo'
                    self.scanner_status.color = [0.16, 0.72, 0.22, 1]
            
            # Converter frame para textura Kivy
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]),
                colorfmt='bgr'
            )
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.camera_image.texture = texture
            
        except Exception as e:
            print(f"❌ Erro no update_camera: {e}")
    
    def _switch_camera(self, instance):
        """Trocar câmera (igual ao ModernSalesScreen)"""
        was_scanning = self.scanning
        
        # Parar scanner temporariamente
        if self.scanning:
            self.scanning = False
            Clock.unschedule(self._update_camera)
            if self.camera_capture:
                self.camera_capture.release()
                self.camera_capture = None
        
        # Alternar ID da câmera (0, 1, 2)
        self.current_camera = (self.current_camera + 1) % 3
        
        # Mostrar mensagem
        self.admin_screen.show_popup(
            "Info",
            f'📷 Trocado para Câmera {self.current_camera}'
        )
        
        # Reiniciar se estava rodando
        if was_scanning:
            Clock.schedule_once(lambda dt: self._restart_scanner(), 0.3)
    
    def _restart_scanner(self):
        """Reiniciar scanner após trocar câmera"""
        self.scanning = True
        self.scan_btn.text = '⏹️ PARAR'
        self.scan_btn.background_color = (0.88, 0.26, 0.26, 1)
        self.scanner_status.text = '🟢 Scanner Ativo'
        self.scanner_status.color = (0.16, 0.72, 0.22, 1)
        Clock.schedule_interval(self._update_camera, 1.0/15.0)
    
    # ==================== GERENCIAMENTO DE CATEGORIA ====================
    
    def _show_category_form(self, instance):
        """Exibir formulário para adicionar categoria"""
        content = BoxLayout(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(15)
        )
        
        content.add_widget(Label(
            text='Digite o nome da nova categoria:',
            size_hint_y=0.3,
            color=(0.2, 0.2, 0.2, 1),
            font_size=sp(15)
        ))
        
        category_input = TextInput(
            multiline=False,
            size_hint_y=0.3,
            hint_text='Ex: Eletrônicos, Alimentos, etc.',
            font_size=sp(15),
            padding=[dp(10), dp(10)]
        )
        content.add_widget(category_input)
        
        button_layout = BoxLayout(size_hint_y=0.4, spacing=dp(10))
        
        popup = Popup(
            title='➕ Adicionar Categoria',
            content=content,
            size_hint=(None, None),
            size=(dp(450), dp(280)),
            auto_dismiss=False,
            separator_color=(0.2, 0.7, 0.3, 1)
        )
        
        cancel_btn = Button(
            text='❌ Cancelar',
            background_color=(0.7, 0.3, 0.3, 1),
            font_size=sp(14),
            bold=True,
            background_normal=''
        )
        cancel_btn.bind(on_release=popup.dismiss)
        
        add_btn = Button(
            text='✅ Adicionar',
            background_color=(0.2, 0.7, 0.3, 1),
            font_size=sp(14),
            bold=True,
            background_normal=''
        )
        
        def add_category(instance):
            new_category = category_input.text.strip()
            
            if not new_category:
                self.admin_screen.show_popup(
                    "Erro",
                    "Digite um nome para a categoria!"
                )
                return
            
            # Verificar se já existe
            current_values = list(self.category_spinner.values)
            
            if new_category in current_values:
                self.admin_screen.show_popup(
                    "Aviso",
                    "Esta categoria já existe!"
                )
                return
            
            # Adicionar nova categoria
            current_values.append(new_category)
            self.category_spinner.values = sorted(current_values)
            self.category_spinner.text = new_category
            
            # Atualizar também no admin screen
            admin_values = list(self.admin_screen.category_spinner.values)
            if new_category not in admin_values:
                admin_values.append(new_category)
                self.admin_screen.category_spinner.values = sorted(admin_values)
            
            popup.dismiss()
            self.admin_screen.show_popup(
                "Sucesso",
                f"Categoria '{new_category}' adicionada!"
            )
        
        add_btn.bind(on_release=add_category)
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(add_btn)
        content.add_widget(button_layout)
        
        popup.open()
    
    # ==================== SALVAR PRODUTO ====================
    
    def _save_product(self, instance):
        """Salvar ou atualizar produto no banco de dados"""
        try:
            # Validar campos obrigatórios
            if not self._validate_fields():
                return
            
            # Processar data de validade
            expiry = self._process_expiry_date()
            if expiry is False:
                return
            
            # Processar código de barras
            barcode_text = self.barcode_input.text.strip()
            barcode = ''.join(
                c for c in barcode_text if c.isprintable()
            ).strip() if barcode_text else None
            
            # Vendido por peso
            is_sold_by_weight = self.is_sold_by_weight_switch.active
            
            # Salvar no banco
            self._save_to_database(barcode, expiry, is_sold_by_weight)
        
        except ValueError as e:
            self.admin_screen.show_popup(
                "Erro",
                f"Verifique os campos numéricos: {str(e)}"
            )
        except Exception as e:
            self.admin_screen.show_popup(
                "Erro",
                f"Erro ao salvar produto: {str(e)}"
            )
    
    def _validate_fields(self):
        """Validar campos obrigatórios"""
        validations = [
            (
                self.description.text.strip(),
                "A descrição é obrigatória!"
            ),
            (
                self.category_spinner.text != "Selecionar",
                "Selecione uma categoria!"
            ),
            (
                self.existing_stock.text.strip(),
                "O estoque existente é obrigatório!"
            ),
            (
                self.sale_price.text.strip(),
                "O preço de venda é obrigatório!"
            ),
            (
                self.total_purchase_price.text.strip(),
                "O preço de compra total é obrigatório!"
            ),
            (
                self.unit_purchase_price.text.strip(),
                "O preço de compra unitário é obrigatório!"
            )
        ]
        
        for condition, message in validations:
            if not condition:
                self.admin_screen.show_popup("Erro", message)
                return False
        
        return True
    
    def _process_expiry_date(self):
        """Processar e validar data de validade"""
        expiry = None
        
        if self.expiry_date.text.strip():
            try:
                expiry_dt = datetime.strptime(
                    self.expiry_date.text.strip(),
                    "%d/%m/%Y"
                )
                expiry = expiry_dt.strftime("%Y-%m-%d")
            except ValueError:
                self.admin_screen.show_popup(
                    "Erro",
                    "Data de validade inválida! Use o formato DD/MM/AAAA"
                )
                return False
        
        return expiry
    
    def _save_to_database(self, barcode, expiry, is_sold_by_weight):
        """Salvar produto no banco de dados"""
        from database import Database
        
        db = Database()
        
        try:
            if self.product:
                # Atualizar produto existente
                db.update_product(
                    self.product[0],
                    self.description.text.strip(),
                    self.category_spinner.text,
                    float(self.existing_stock.text),
                    float(self.sold_stock.text),
                    float(self.sale_price.text),
                    float(self.total_purchase_price.text),
                    float(self.unit_purchase_price.text),
                    barcode,
                    expiry,
                    is_sold_by_weight
                )
                self.admin_screen.show_popup(
                    "Sucesso",
                    "Produto atualizado com sucesso!"
                )
            else:
                # Adicionar novo produto
                db.add_product(
                    self.description.text.strip(),
                    self.category_spinner.text,
                    float(self.existing_stock.text),
                    float(self.sold_stock.text),
                    float(self.sale_price.text),
                    float(self.total_purchase_price.text),
                    float(self.unit_purchase_price.text),
                    barcode,
                    expiry,
                    is_sold_by_weight
                )
                self.admin_screen.show_popup(
                    "Sucesso",
                    "Produto adicionado com sucesso!"
                )
            
            self.dismiss()
            self.admin_screen.load_products()
        
        finally:
            db.close()
    
    # ==================== PREENCHER CAMPOS ====================
    
    def _populate_fields(self):
        """Preencher campos ao editar produto"""
        product = self.product
        
        # Campos básicos
        self.description.text = product[1]
        self.category_spinner.text = product[11] if len(product) > 11 else "Selecionar"
        self.existing_stock.text = str(product[2])
        self.sold_stock.text = str(product[3])
        self.sale_price.text = str(product[4])
        self.total_purchase_price.text = str(product[5])
        self.unit_purchase_price.text = str(product[6])
        
        # Código de barras
        if len(product) > 12 and product[12]:
            self.barcode_input.text = str(product[12])
        
        # Data de validade
        if len(product) > 13 and product[13]:
            try:
                dt = datetime.strptime(str(product[13]), "%Y-%m-%d")
                self.expiry_date.text = dt.strftime("%d/%m/%Y")
            except:
                self.expiry_date.text = str(product[13])
        
        # Vendido por peso
        if len(product) > 15:
            self.is_sold_by_weight_switch.active = bool(product[15])
    
    # ==================== EVENTOS ====================
    
    def _on_window_resize(self, instance, width, height):
        """Ajustar tamanho ao redimensionar janela"""
        self.size = (
            min(dp(1100), width * 0.95),
            min(dp(800), height * 0.9)
        )
    
    def on_dismiss(self):
        """Limpar recursos ao fechar popup"""
        # Parar scanner
        if self.scanning:
            self.scanning = False
            Clock.unschedule(self._update_camera)
            if self.camera_capture:
                self.camera_capture.release()
                self.camera_capture = None
        
        # Unbind eventos
        Window.unbind(on_resize=self._on_window_resize)


class AdminScreen(Screen):
    product_table = ObjectProperty(None)
    search_input = ObjectProperty(None)
    category_spinner = ObjectProperty(None)
    products = ListProperty([])
    
    def __init__(self, **kwargs):
        super(AdminScreen, self).__init__(**kwargs)
        self.db = Database()
    
    def on_enter(self):
        self.load_products()
        
    def go_to_definitions(self):
        self.manager.current = 'settings'
    
    def filter_products(self, search_text):
        category = self.category_spinner.text
        filtered_products = []
        
        for product in self.products:
            # Buscar por ID, descrição, categoria ou código de barras
            search_match = (
                search_text.lower() in str(product[0]).lower() or
                search_text.lower() in product[1].lower() or
                (len(product) > 11 and search_text.lower() in str(product[11]).lower()) or
                (len(product) > 12 and product[12] and search_text.lower() in str(product[12]).lower())
            )
            
            category_match = (
                category == 'Todas' or 
                (len(product) > 11 and category == product[11])
            )
            
            if search_match and category_match:
                filtered_products.append(product)
        
        self.update_product_table(filtered_products)
    
    def load_products(self):
        self.products = self.db.get_all_products()
        self.update_product_table(self.products)
        
        categories = set(['Todas'])
        for product in self.products:
            if len(product) > 11 and product[11]:
                categories.add(product[11])
        
        self.category_spinner.values = sorted(list(categories))
    
    def format_datetime(self, datetime_str):
        """Formatar data e hora para DD/MM/YYYY HH:MM"""
        try:
            if datetime_str and datetime_str != "N/A":
                dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                return dt.strftime("%d/%m/%Y\n%H:%M")
        except Exception as e:
            print(f"Erro ao formatar data: {e}")
        return datetime_str
    
    def format_date(self, date_str):
        """Formatar apenas data para DD/MM/YYYY"""
        try:
            if date_str and date_str != "N/A":
                # Tentar formato com hora primeiro
                try:
                    dt = datetime.strptime(str(date_str), "%Y-%m-%d %H:%M:%S")
                    return dt.strftime("%d/%m/%Y")
                except:
                    # Tentar formato apenas data
                    dt = datetime.strptime(str(date_str), "%Y-%m-%d")
                    return dt.strftime("%d/%m/%Y")
        except Exception as e:
            print(f"Erro ao formatar data: {e}")
        return str(date_str)
    
    def update_product_table(self, products_to_display=None):
        """Atualizar a tabela de produtos"""
        self.product_table.clear_widgets()

        if products_to_display is None:
            products_to_display = self.products

        for idx, product in enumerate(products_to_display):
            # Cor de fundo alternada para as linhas
            row_bg_color = [0.98, 0.99, 1, 1] if idx % 2 == 0 else [1, 1, 1, 1]
            # ID - 0.07
            id_container = BoxLayout(size_hint_x=0.07)
            id_container.canvas.before.clear()
            with id_container.canvas.before:
                Color(*row_bg_color)
                Rectangle(pos=id_container.pos, size=id_container.size)
                Color(0, 0, 0, 1)  # Cor preta
                Line(points=[id_container.x, id_container.y, id_container.x, id_container.top], width=1)  # Linha vertical esquerda
                Line(points=[id_container.right, id_container.y, id_container.right, id_container.top], width=1)  # Linha vertical direita
                Line(points=[id_container.x, id_container.top, id_container.right, id_container.top], width=1)  # Linha horizontal topo
                Line(points=[id_container.x, id_container.y, id_container.right, id_container.y], width=1)  # Linha horizontal baixo
            
            id_label = Label(
                text=str(product[0]), 
                color=[0.3, 0.35, 0.45, 1],
                halign='center',
                valign='middle',
                bold=True
            )
            id_container.add_widget(id_label)
            id_container.bind(pos=lambda w, v: self.update_cell_bg(w, row_bg_color, True, True), 
                            size=lambda w, v: self.update_cell_bg(w, row_bg_color, True, True))
            
            # Descrição - 0.18
            desc_container = BoxLayout(size_hint_x=0.18, padding=[10, 0])
            desc_container.canvas.before.clear()
            with desc_container.canvas.before:
                Color(*row_bg_color)
                Rectangle(pos=desc_container.pos, size=desc_container.size)
                Color(0, 0, 0, 1)  # Cor preta
                Line(points=[desc_container.right, desc_container.y, desc_container.right, desc_container.top], width=1)
                Line(points=[desc_container.x, desc_container.top, desc_container.right, desc_container.top], width=1)
                Line(points=[desc_container.x, desc_container.y, desc_container.right, desc_container.y], width=1)
            
            desc_label = Label(
                text=product[1], 
                color=[0.2, 0.25, 0.35, 1],
                text_size=(None, None), 
                shorten=True, 
                halign='left',
                valign='middle'
            )
            desc_container.add_widget(desc_label)
            desc_container.bind(pos=lambda w, v: self.update_cell_bg(w, row_bg_color, True, False), 
                            size=lambda w, v: self.update_cell_bg(w, row_bg_color, True, False))
            
            # Verificar se é vendido por peso (índice 15)
            is_sold_by_weight = product[15] if len(product) > 15 else 0
            unit_label = "kg" if is_sold_by_weight else "un"
            
            # Estoque - 0.09
            stock_container = BoxLayout(size_hint_x=0.09)
            stock_container.canvas.before.clear()
            with stock_container.canvas.before:
                Color(*row_bg_color)
                Rectangle(pos=stock_container.pos, size=stock_container.size)
                Color(0, 0, 0, 1)  # Cor preta
                Line(points=[stock_container.right, stock_container.y, stock_container.right, stock_container.top], width=1)
                Line(points=[stock_container.x, stock_container.top, stock_container.right, stock_container.top], width=1)
                Line(points=[stock_container.x, stock_container.y, stock_container.right, stock_container.y], width=1)
            
            stock_value = product[2]
            stock_text = f"{stock_value:.2f} {unit_label}" if is_sold_by_weight else f"{int(stock_value)} {unit_label}"
            stock_label = Label(
                text=stock_text, 
                color=[0.2, 0.25, 0.35, 1],
                halign='center',
                valign='middle'
            )
            stock_container.add_widget(stock_label)
            stock_container.bind(pos=lambda w, v: self.update_cell_bg(w, row_bg_color, True, False), 
                            size=lambda w, v: self.update_cell_bg(w, row_bg_color, True, False))
            
            # Vendido - 0.09
            sold_container = BoxLayout(size_hint_x=0.09)
            sold_container.canvas.before.clear()
            with sold_container.canvas.before:
                Color(*row_bg_color)
                Rectangle(pos=sold_container.pos, size=sold_container.size)
                Color(0, 0, 0, 1)  # Cor preta
                Line(points=[sold_container.right, sold_container.y, sold_container.right, sold_container.top], width=1)
                Line(points=[sold_container.x, sold_container.top, sold_container.right, sold_container.top], width=1)
                Line(points=[sold_container.x, sold_container.y, sold_container.right, sold_container.y], width=1)
            
            sold_value = product[3]
            sold_text = f"{sold_value:.2f} {unit_label}" if is_sold_by_weight else f"{int(sold_value)} {unit_label}"
            sold_stock_label = Label(
                text=sold_text,
                color=[0.2, 0.25, 0.35, 1],
                halign='center',
                valign='middle'
            )
            sold_container.add_widget(sold_stock_label)
            sold_container.bind(pos=lambda w, v: self.update_cell_bg(w, row_bg_color, True, False), 
                            size=lambda w, v: self.update_cell_bg(w, row_bg_color, True, False))
            
            # Tipo de Venda - 0.09
            tipo_container = BoxLayout(size_hint_x=0.09)
            tipo_container.canvas.before.clear()
            with tipo_container.canvas.before:
                Color(*row_bg_color)
                Rectangle(pos=tipo_container.pos, size=tipo_container.size)
                Color(0, 0, 0, 1)  # Cor preta
                Line(points=[tipo_container.right, tipo_container.y, tipo_container.right, tipo_container.top], width=1)
                Line(points=[tipo_container.x, tipo_container.top, tipo_container.right, tipo_container.top], width=1)
                Line(points=[tipo_container.x, tipo_container.y, tipo_container.right, tipo_container.y], width=1)
            
            tipo_venda_label = Label(
                text="Por KG" if is_sold_by_weight else "Por Unid.", 
                color=[0.8, 0.4, 0.0, 1] if is_sold_by_weight else [0.1, 0.5, 0.8, 1],
                halign='center',
                valign='middle',
                bold=True,
                font_size='12sp'
            )
            tipo_container.add_widget(tipo_venda_label)
            tipo_container.bind(pos=lambda w, v: self.update_cell_bg(w, row_bg_color, True, False), 
                            size=lambda w, v: self.update_cell_bg(w, row_bg_color, True, False))
            
            # Preço - 0.11
            price_container = BoxLayout(size_hint_x=0.11)
            price_container.canvas.before.clear()
            with price_container.canvas.before:
                Color(*row_bg_color)
                Rectangle(pos=price_container.pos, size=price_container.size)
                Color(0, 0, 0, 1)  # Cor preta
                Line(points=[price_container.right, price_container.y, price_container.right, price_container.top], width=1)
                Line(points=[price_container.x, price_container.top, price_container.right, price_container.top], width=1)
                Line(points=[price_container.x, price_container.y, price_container.right, price_container.y], width=1)
            
            price_label = Label(
                text=f"MZN {product[4]:.2f}",
                color=[0.1, 0.5, 0.2, 1],
                halign='center',
                valign='middle',
                bold=True
            )
            price_container.add_widget(price_label)
            price_container.bind(pos=lambda w, v: self.update_cell_bg(w, row_bg_color, True, False), 
                            size=lambda w, v: self.update_cell_bg(w, row_bg_color, True, False))
            
            # Lucro - 0.11
            profit_container = BoxLayout(size_hint_x=0.11)
            profit_container.canvas.before.clear()
            with profit_container.canvas.before:
                Color(*row_bg_color)
                Rectangle(pos=profit_container.pos, size=profit_container.size)
                Color(0, 0, 0, 1)  # Cor preta
                Line(points=[profit_container.right, profit_container.y, profit_container.right, profit_container.top], width=1)
                Line(points=[profit_container.x, profit_container.top, profit_container.right, profit_container.top], width=1)
                Line(points=[profit_container.x, profit_container.y, profit_container.right, profit_container.y], width=1)
            
            total_profit_label = Label(
                text=f"MZN {product[8]:.2f}",
                color=[0.0, 0.4, 0.7, 1],
                halign='center',
                valign='middle',
                bold=True
            )
            profit_container.add_widget(total_profit_label)
            profit_container.bind(pos=lambda w, v: self.update_cell_bg(w, row_bg_color, True, False), 
                                size=lambda w, v: self.update_cell_bg(w, row_bg_color, True, False))
            
            # Data de Adição - 0.12
            date_container = BoxLayout(size_hint_x=0.12)
            date_container.canvas.before.clear()
            with date_container.canvas.before:
                Color(*row_bg_color)
                Rectangle(pos=date_container.pos, size=date_container.size)
                Color(0, 0, 0, 1)  # Cor preta
                Line(points=[date_container.right, date_container.y, date_container.right, date_container.top], width=1)
                Line(points=[date_container.x, date_container.top, date_container.right, date_container.top], width=1)
                Line(points=[date_container.x, date_container.y, date_container.right, date_container.y], width=1)
            
            date_added = str(product[14]) if len(product) > 14 and product[14] else "N/A"
            date_label = Label(
                text=self.format_datetime(date_added),
                color=[0.4, 0.45, 0.5, 1],
                halign='center',
                valign='middle',
                font_size='11sp'
            )
            date_container.add_widget(date_label)
            date_container.bind(pos=lambda w, v: self.update_cell_bg(w, row_bg_color, True, False), 
                            size=lambda w, v: self.update_cell_bg(w, row_bg_color, True, False))
            
            # Ações - 0.14
            action_container = BoxLayout(size_hint_x=0.14)
            action_container.canvas.before.clear()
            with action_container.canvas.before:
                Color(*row_bg_color)
                Rectangle(pos=action_container.pos, size=action_container.size)
                Color(0, 0, 0, 1)  # Cor preta
                Line(points=[action_container.right, action_container.y, action_container.right, action_container.top], width=1)
                Line(points=[action_container.x, action_container.top, action_container.right, action_container.top], width=1)
                Line(points=[action_container.x, action_container.y, action_container.right, action_container.y], width=1)
            
            action_layout = BoxLayout(spacing=5, padding=[5, 0])
            
            # Criar botões com bordas coloridas
            detail_btn = self.create_detail_button(product[0])
            edit_btn = self.create_edit_button(product)
            delete_btn = self.create_delete_button(product[0])
            
            # Adicionar botões ao layout de ações
            action_layout.add_widget(detail_btn)
            action_layout.add_widget(edit_btn)
            action_layout.add_widget(delete_btn)
            
            action_container.add_widget(action_layout)
            action_container.bind(pos=lambda w, v: self.update_cell_bg(w, row_bg_color, False, False), 
                                size=lambda w, v: self.update_cell_bg(w, row_bg_color, False, False))
            
            # Adicionar todos os widgets à tabela (9 colunas)
            self.product_table.add_widget(id_container)
            self.product_table.add_widget(desc_container)
            self.product_table.add_widget(stock_container)
            self.product_table.add_widget(sold_container)
            self.product_table.add_widget(tipo_container)
            self.product_table.add_widget(price_container)
            self.product_table.add_widget(profit_container)
            self.product_table.add_widget(date_container)
            self.product_table.add_widget(action_container)
            
            # Adicionar linha horizontal divisória no final da linha (exceto última)
            if idx < len(products_to_display) - 1:
                for i in range(9):
                    separator = Widget(size_hint_y=None, height=0.1, size_hint_x=[0.07, 0.18, 0.09, 0.09, 0.09, 0.11, 0.11, 0.12, 0.14][i])
                    with separator.canvas:
                        Color(0, 0, 0, 1)  # Cor preta
                        Rectangle(pos=separator.pos, size=separator.size)
                    separator.bind(pos=lambda w, v: self.update_separator(w), size=lambda w, v: self.update_separator(w))
                    self.product_table.add_widget(separator)
    
    def update_separator(self, widget):
        """Atualizar linha separadora"""
        widget.canvas.clear()
        with widget.canvas:
            Color(0, 0, 0, 1)  # Cor preta
            Rectangle(pos=widget.pos, size=widget.size)
    
    def update_cell_bg(self, widget, bg_color, add_line=True, add_left_line=False):
        """Atualizar o fundo e linha da célula"""
        widget.canvas.before.clear()
        with widget.canvas.before:
            Color(*bg_color)
            Rectangle(pos=widget.pos, size=widget.size)
            Color(0, 0, 0, 1)  # Cor preta
            if add_left_line:
                Line(points=[widget.x, widget.y, widget.x, widget.top], width=1)  # Linha vertical esquerda
            if add_line:
                Line(points=[widget.right, widget.y, widget.right, widget.top], width=1)  # Linha vertical direita
                Line(points=[widget.x, widget.top, widget.right, widget.top], width=1)  # Linha horizontal topo
                Line(points=[widget.x, widget.y, widget.right, widget.y], width=1)  # Linha horizontal baixo
    
    # Métodos para criar botões com bordas
    def create_detail_button(self, product_id):
        detail_btn = Button(
            text="i", 
            background_color=[0, 0, 0, 0], 
            color=[0, 0, 1, 1], 
            size_hint=(1, 1),
            bold=True
        )
        detail_btn.product_id = product_id
        detail_btn.bind(on_release=self.show_product_details)
        
        with detail_btn.canvas.before:
            Color(0, 0, 1, 1)
            self.detail_line = Line(width=1.2)
        
        detail_btn.bind(pos=self.update_detail_rect, size=self.update_detail_rect)
        return detail_btn
    
    def create_edit_button(self, product):
        edit_btn = Button(
            text="E", 
            background_color=[0, 0, 0, 0], 
            color=[0, 0.7, 0, 1], 
            size_hint=(1, 1),
            bold=True
        )
        edit_btn.product_id = product
        edit_btn.bind(on_release=self.edit_product)
        
        with edit_btn.canvas.before:
            Color(0, 0.7, 0, 1)
            self.edit_line = Line(width=1.2)
        
        edit_btn.bind(pos=self.update_edit_rect, size=self.update_edit_rect)
        return edit_btn
    
    def create_delete_button(self, product_id):
        delete_btn = Button(
            text="x", 
            background_color=[0, 0, 0, 0], 
            color=[1, 0, 0, 1], 
            size_hint=(1, 1),
            bold=True
        )
        delete_btn.product_id = product_id
        delete_btn.bind(on_release=self.delete_product)
        
        with delete_btn.canvas.before:
            Color(1, 0, 0, 1)
            self.delete_line = Line(width=1.2)
        
        delete_btn.bind(pos=self.update_delete_rect, size=self.update_delete_rect)
        return delete_btn
    
    # Funções para atualizar as bordas dos botões
    def update_detail_rect(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0, 0, 1, 1)
            Line(width=1.2, rectangle=(instance.x, instance.y, instance.width, instance.height))

    def update_edit_rect(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0, 0.7, 0, 1)
            Line(width=1.2, rectangle=(instance.x, instance.y, instance.width, instance.height))

    def update_delete_rect(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(1, 0, 0, 1)
            Line(width=1.2, rectangle=(instance.x, instance.y, instance.width, instance.height))
    
    # Métodos para manipulação de produtos
    def show_product_details(self, instance):
        product_id = instance.product_id
        product = self.db.get_product(product_id)
        
        if product:
            detail_popup = DetailPopup(product)
            detail_popup.open()
    
    def add_product(self):
        product_form = ProductForm(self)
        product_form.open()
    
    def edit_product(self, instance):
        product = instance.product_id
        product_form = ProductForm(self, product)
        product_form.open()
    
    def delete_product(self, instance):
        product_id = instance.product_id
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        message_label = Label(
            text="Tem certeza que deseja excluir este produto?",
            size_hint_y=0.6
        )
        content.add_widget(message_label)
        
        buttons = BoxLayout(size_hint_y=0.4, spacing=10)
        
        popup = Popup(
            title="Confirmar Exclusão", 
            content=content, 
            size_hint=(None, None), 
            size=(400, 200),
            auto_dismiss=False
        )
        
        confirm_btn = Button(
            text="Sim",
            background_color=[0.9, 0.3, 0.3, 1]
        )
        cancel_btn = Button(
            text="Não",
            background_color=[0.3, 0.3, 0.3, 1]
        )
        
        confirm_btn.bind(on_release=lambda x: self.confirm_delete(product_id, popup))
        cancel_btn.bind(on_release=lambda x: popup.dismiss())
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        content.add_widget(buttons)
        
        popup.open()
    
    def confirm_delete(self, product_id, popup):
        self.db.delete_product(product_id)
        popup.dismiss()
        self.load_products()
        self.show_popup("Sucesso", "Produto excluído com sucesso!")
    
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        
        popup = Popup(
            title=title, 
            content=content,
            size_hint=(None, None), 
            size=(400, 200),
            auto_dismiss=True
        )
        popup.open()
    
    def generate_report(self):
        self.manager.current = 'reports'
        if 'reports' in self.manager.screen_names:
            reports_screen = self.manager.get_screen('reports')
            Clock.schedule_once(lambda dt: reports_screen.select_date_range(), 0.1)
    
    def toggle_kg_products(self):
        """Alternar entre 3 estados: Todos → Por KG → Por Unidade → Todos"""
        if not hasattr(self, 'filter_mode'):
            self.filter_mode = 0  # 0 = Todos, 1 = Por KG, 2 = Por Unidade
        
        # Avançar para o próximo modo
        self.filter_mode = (self.filter_mode + 1) % 3
        
        if self.filter_mode == 1:
            # Filtrar apenas produtos vendidos POR KG
            kg_products = self.db.get_products_by_weight()
            if kg_products:
                self.update_product_table(kg_products)
            else:
                # Se não houver produtos por KG, pula para o próximo filtro
                self.filter_mode = 2
                unit_products = [p for p in self.products if not (len(p) > 15 and p[15])]
                if unit_products:
                    self.update_product_table(unit_products)
                else:
                    # Se também não houver produtos por unidade, volta para todos
                    self.filter_mode = 0
                    self.update_product_table(self.products)
        
        elif self.filter_mode == 2:
            # Filtrar apenas produtos vendidos POR UNIDADE
            unit_products = [p for p in self.products if not (len(p) > 15 and p[15])]
            if unit_products:
                self.update_product_table(unit_products)
            else:
                # Se não houver produtos por unidade, volta para todos
                self.filter_mode = 0
                self.update_product_table(self.products)
        
        else:
            # Mostrar TODOS os produtos
            self.update_product_table(self.products)
    
    def logout(self):
        self.manager.current = "login"