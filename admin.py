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
import cv2
from pyzbar.pyzbar import decode
from datetime import datetime
import numpy as np
import threading
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
        # HEADER - Título e Botões de Navegação
        # =====================================================
        BoxLayout:
            size_hint_y: 0.15
            padding: [20, 10, 20, 0]
            spacing: 10

            # Título Principal
            Label:
                text: 'Painel do Administrador'
                font_size: '26sp'
                bold: True
                size_hint_x: 0.7
                halign: 'left'
                valign: 'middle'
                text_size: self.size
                color: 0.2, 0.2, 0.2, 1

            # Botões de Navegação
            BoxLayout:
                size_hint_x: 0.3
                spacing: 10

                Widget:

                # Botão Definições
                Button:
                    text: 'Definições'
                    size_hint: None, None
                    size: 145, 35
                    bold: True
                    color: 0.2, 0.2, 0.2, 1
                    background_color: 0, 0, 0, 0
                    on_release: root.go_to_definitions()
                    canvas.before:
                        Color:
                            rgba: 0.2, 0.2, 0.2, 1
                        Line:
                            rounded_rectangle: (*self.pos, *self.size, 10)
                            width: 1.2

                # Botão Sair
                Button:
                    text: '<-- SAIR --'
                    size_hint: None, None
                    size: 150, 40
                    bold: True
                    color: 0.9, 0.3, 0.3, 1
                    background_color: 0, 0, 0, 0
                    on_release: root.logout()
                    canvas.before:
                        Color:
                            rgba: 0.9, 0.3, 0.3, 1
                        Line:
                            rounded_rectangle: (*self.pos, *self.size, 10)
                            width: 1.2

        # =====================================================
        # BARRA DE PESQUISA E FILTROS
        # =====================================================
        BoxLayout:
            size_hint_y: 0.1
            padding: [20, 5, 20, 5]
            spacing: 10

            # Área de Pesquisa e Filtros
            BoxLayout:
                size_hint_x: 0.7
                spacing: 10

                # Campo de Pesquisa
                TextInput:
                    id: search_input
                    hint_text: 'Pesquisar por descrição, ID ou código de barras'
                    multiline: False
                    padding: [10, 5]
                    background_color: 0, 0, 0, 0
                    foreground_color: 0.2, 0.2, 0.2, 1
                    cursor_color: 0.2, 0.2, 0.2, 1
                    on_text: root.filter_products(self.text)
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]
                        Color:
                            rgba: 0, 0, 0, 1
                        Line:
                            rounded_rectangle: (*self.pos, *self.size, 10)
                            width: 1.2

                # Filtro de Categorias
                Spinner:
                    id: category_spinner
                    text: 'Categorias'
                    values: ['Todas', 'Eletrônicos', 'Alimentos', 'Vestuário', 'Outros']
                    size_hint_x: 0.4
                    color: 0.2, 0.2, 0.2, 1
                    background_color: 0, 0, 0, 0
                    on_text: root.filter_products(search_input.text)
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [8]
                        Color:
                            rgba: 0.2, 0.2, 0.2, 1
                        Line:
                            rounded_rectangle: (*self.pos, *self.size, 8)
                            width: 1.2

            Widget:
                size_hint_x: 0.05

            # Botões de Ação
            BoxLayout:
                size_hint_x: 0.3
                spacing: 10

                # Botão Produtos em KG
                Button:
                    text: 'Produtos/KG'
                    bold: True
                    color: 0.8, 0.4, 0.0, 1
                    background_color: 0, 0, 0, 0
                    on_release: root.toggle_kg_products()
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]
                        Color:
                            rgba: 0.8, 0.4, 0.0, 1
                        Line:
                            rounded_rectangle: (*self.pos, *self.size, 10)
                            width: 1.5

                # Botão Adicionar Produto
                Button:
                    text: 'Adicionar'
                    bold: True
                    color: 0.1, 0.6, 0.2, 1
                    background_color: 0, 0, 0, 0
                    on_release: root.add_product()
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]
                        Color:
                            rgba: 0.1, 0.6, 0.2, 1
                        Line:
                            rounded_rectangle: (*self.pos, *self.size, 10)
                            width: 1.5

                # Botão Gerar Relatório
                Button:
                    text: 'Relatório'
                    bold: True
                    color: 0.2, 0.2, 0.2, 1
                    background_color: 0, 0, 0, 0
                    on_release: root.generate_report()
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [10]
                        Color:
                            rgba: 0.2, 0.2, 0.2, 1
                        Line:
                            rounded_rectangle: (*self.pos, *self.size, 10)
                            width: 1.2

        # =====================================================
        # TÍTULO DA SEÇÃO DE PRODUTOS
        # =====================================================
        BoxLayout:
            size_hint_y: 0.05
            padding: [20, 0, 20, 0]

            Label:
                text: 'Lista de Produtos'
                font_size: '20sp'
                bold: True
                halign: 'left'
                valign: 'middle'
                text_size: self.size
                color: 0.2, 0.2, 0.2, 1

        # =====================================================
        # TABELA DE PRODUTOS
        # =====================================================
        BoxLayout:
            size_hint_y: 0.7
            padding: [20, 0, 20, 20]

            BoxLayout:
                orientation: 'vertical'
                spacing: 2

                # Header da Tabela (9 colunas agora)
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
                        row_default_height: 50
                        row_force_default: True
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
    def __init__(self, admin_screen, product=None, **kwargs):
        super(ProductForm, self).__init__(**kwargs)

        self.admin_screen = admin_screen
        self.product = product
        self.title = "Adicionar Produto" if not product else "Editar Produto"
        
        # Controle do scanner
        self.scanning = False
        self.scanner_thread = None
        
        # Importar CheckBox aqui se necessário
        from kivy.uix.checkbox import CheckBox

        window_width, window_height = Window.size
        popup_width = min(dp(700), window_width * 0.9)
        popup_height = min(dp(750), window_height * 0.9)

        self.size = (popup_width, popup_height)
        self.size_hint = (None, None)
        self.auto_dismiss = True
        self.background_color = (1, 1, 1, 1)

        Window.bind(on_resize=self.on_window_resize)

        container = ScrollView()
        main_layout = BoxLayout(
            orientation='vertical',
            spacing=15,
            padding=[20, 20],
            size_hint_y=None
        )
        main_layout.bind(minimum_height=main_layout.setter('height'))

        # ================= CAMPOS =================

        # Código de barras
        self.barcode_input = TextInput(
            multiline=False,
            readonly=False,
            height=dp(40),
            size_hint_y=None,
            background_color=(1, 1, 1, 1),
            padding=[10, 10, 0, 0],
            font_size=sp(16),
            hint_text="Digite ou escaneie o código de barras"
        )

        scan_btn = Button(
            text="SCANNER",
            size_hint_x=0.35,
            background_color=(0.2, 0.5, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        scan_btn.bind(on_release=self.scan_barcode)

        barcode_layout = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=5
        )
        barcode_layout.add_widget(self.barcode_input)
        barcode_layout.add_widget(scan_btn)

        # Data de validade
        self.expiry_date = TextInput(
            hint_text="DD/MM/AAAA",
            multiline=False,
            height=dp(40),
            size_hint_y=None,
            background_color=(1, 1, 1, 1),
            padding=[10, 10, 0, 0],
            font_size=sp(16)
        )

        self.description = TextInput(
            multiline=False,
            height=dp(40),
            size_hint_y=None,
            background_color=(1, 1, 1, 1),
            padding=[10, 10, 0, 0],
            font_size=sp(16)
        )

        category_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=5
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
            font_size=sp(16)
        )

        add_category_btn = Button(
            text="+",
            size_hint_x=0.2,
            background_color=(0.3, 0.7, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        add_category_btn.bind(on_release=self.show_category_form)

        category_layout.add_widget(self.category_spinner)
        category_layout.add_widget(add_category_btn)

        self.existing_stock = TextInput(
            multiline=False,
            input_filter='int',
            height=dp(40),
            size_hint_y=None,
            background_color=(1, 1, 1, 1),
            font_size=sp(16)
        )

        self.sold_stock = TextInput(
            multiline=False,
            input_filter='int',
            height=dp(40),
            size_hint_y=None,
            readonly=True,
            background_color=(0.95, 0.95, 0.95, 1),
            font_size=sp(16),
            text="0"
        )

        # NOVO: Switch para definir se é vendido por KG
        self.is_sold_by_weight_switch = CheckBox(
            size_hint_x=0.2,
            active=False
        )
        
        switch_layout = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=10
        )
        switch_layout.add_widget(Label(
            text="Vendido por KG",
            size_hint_x=0.6,
            halign='left',
            valign='middle',
            text_size=(None, None),
            color=[0, 0, 0, 1]
        ))
        switch_layout.add_widget(self.is_sold_by_weight_switch)
        switch_layout.add_widget(Label(size_hint_x=0.2))  # Spacer

        self.sale_price = TextInput(
            multiline=False,
            input_filter='float',
            height=dp(40),
            size_hint_y=None,
            background_color=(1, 1, 1, 1),
            font_size=sp(16)
        )

        self.total_purchase_price = TextInput(
            multiline=False,
            input_filter='float',
            height=dp(40),
            size_hint_y=None,
            background_color=(1, 1, 1, 1),
            font_size=sp(16)
        )

        self.unit_purchase_price = TextInput(
            multiline=False,
            input_filter='float',
            height=dp(40),
            size_hint_y=None,
            background_color=(1, 1, 1, 1),
            font_size=sp(16)
        )

        # Preencher dados ao editar
        if product:
            self.description.text = product[1]
            self.category_spinner.text = product[11] if len(product) > 11 else "Selecionar"
            self.existing_stock.text = str(product[2])
            self.sold_stock.text = str(product[3])
            self.sale_price.text = str(product[4])
            self.total_purchase_price.text = str(product[5])
            self.unit_purchase_price.text = str(product[6])
            
            # Código de Barras (índice 12)
            if len(product) > 12 and product[12]:
                self.barcode_input.text = str(product[12])
            
            # Data de Validade (índice 13)
            if len(product) > 13 and product[13]:
                try:
                    dt = datetime.strptime(str(product[13]), "%Y-%m-%d")
                    self.expiry_date.text = dt.strftime("%d/%m/%Y")
                except:
                    self.expiry_date.text = str(product[13])
            
            # Vendido por KG (índice 15)
            if len(product) > 15:
                self.is_sold_by_weight_switch.active = bool(product[15])

        form_layout = GridLayout(cols=2, spacing=[10, 15], size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))

        fields = [
            ("Código de Barras", barcode_layout),
            ("Data de Validade", self.expiry_date),
            ("Descrição*", self.description),
            ("Categoria*", category_layout),
            ("Estoque Existente*", self.existing_stock),
            ("Estoque Vendido", self.sold_stock),
            ("", switch_layout),  # SWITCH VENDIDO POR KG
            ("Preço Final de Venda*", self.sale_price),
            ("Preço de Compra Total*", self.total_purchase_price),
            ("Preço de Compra Unitário*", self.unit_purchase_price)
        ]

        for label_text, widget in fields:
            label = Label(
                text=label_text,
                size_hint_y=None,
                height=dp(40),
                halign='left',
                valign='middle',
                text_size=(popup_width * 0.4, None),
                bold='*' in label_text,
                font_size=sp(16)
            )
            form_layout.add_widget(label)
            form_layout.add_widget(widget)

        main_layout.add_widget(form_layout)

        button_layout = BoxLayout(
            spacing=15,
            size_hint_y=None,
            height=dp(50)
        )

        cancel_btn = Button(
            text="Cancelar",
            background_color=(0.7, 0.7, 0.7, 1)
        )
        cancel_btn.bind(on_release=self.dismiss)

        save_btn = Button(
            text="Salvar",
            background_color=(0.1, 0.6, 0.2, 1)
        )
        save_btn.bind(on_release=self.save_product)

        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(save_btn)

        main_layout.add_widget(button_layout)
        container.add_widget(main_layout)
        self.content = container

    def show_category_form(self, instance):
        """Mostrar formulário para adicionar nova categoria"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(
            text='Digite o nome da nova categoria:',
            size_hint_y=0.3
        ))
        
        category_input = TextInput(
            multiline=False,
            size_hint_y=0.3,
            hint_text='Ex: Eletrônicos, Alimentos, etc.'
        )
        content.add_widget(category_input)
        
        button_layout = BoxLayout(size_hint_y=0.4, spacing=10)
        
        popup = Popup(
            title='Adicionar Categoria',
            content=content,
            size_hint=(None, None),
            size=(400, 250),
            auto_dismiss=False
        )
        
        cancel_btn = Button(
            text='Cancelar',
            background_color=(0.7, 0.7, 0.7, 1)
        )
        cancel_btn.bind(on_release=popup.dismiss)
        
        add_btn = Button(
            text='Adicionar',
            background_color=(0.1, 0.6, 0.2, 1)
        )
        
        def add_category(instance):
            new_category = category_input.text.strip()
            if new_category:
                current_values = list(self.category_spinner.values)
                if new_category not in current_values:
                    current_values.append(new_category)
                    self.category_spinner.values = sorted(current_values)
                    self.category_spinner.text = new_category
                    
                    admin_values = list(self.admin_screen.category_spinner.values)
                    if new_category not in admin_values:
                        admin_values.append(new_category)
                        self.admin_screen.category_spinner.values = sorted(admin_values)
                    
                    popup.dismiss()
                    self.admin_screen.show_popup("Sucesso", f"Categoria '{new_category}' adicionada!")
                else:
                    self.admin_screen.show_popup("Aviso", "Esta categoria já existe!")
            else:
                self.admin_screen.show_popup("Erro", "Digite um nome para a categoria!")
        
        add_btn.bind(on_release=add_category)
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(add_btn)
        content.add_widget(button_layout)
        
        popup.open()

    # ================= SCAN BARCODE (CORRIGIDO COM THREADING) =================
    def scan_barcode(self, instance):
        """Iniciar scanner em thread separada"""
        if self.scanning:
            self.admin_screen.show_popup("Aviso", "Scanner já está ativo!")
            return
        
        self.scanning = True
        self.scanner_thread = threading.Thread(target=self._scan_barcode_thread, daemon=True)
        self.scanner_thread.start()
    
    def _scan_barcode_thread(self):
        """Scanner de código de barras rodando em thread - SEM acesso ao banco aqui"""
        current_camera = 0
        cap = cv2.VideoCapture(current_camera)
        barcode_value = None
        scan_attempts = 0
        
        if not cap.isOpened():
            Clock.schedule_once(lambda dt: self.admin_screen.show_popup(
                "Erro", "Não foi possível abrir a câmera!"))
            self.scanning = False
            return
        
        window_name = "Scanner de Codigo de Barras"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1000, 600)
        
        try:
            while self.scanning:
                ret, frame = cap.read()
                if not ret:
                    break
                
                scan_attempts += 1
                
                # Criar canvas
                canvas = np.ones((600, 1000, 3), dtype=np.uint8) * 240
                
                # Área da câmera
                camera_width = 275
                camera_height = 200
                camera_x = 680
                camera_y = 20
                
                small_frame = cv2.resize(frame, (camera_width, camera_height))
                canvas[camera_y:camera_y+camera_height, camera_x:camera_x+camera_width] = small_frame
                
                cv2.rectangle(canvas, (camera_x-2, camera_y-2), 
                             (camera_x+camera_width+2, camera_y+camera_height+2), 
                             (0, 120, 255), 2)
                
                # Informações
                info_x = 30
                info_y = 50
                
                cv2.putText(canvas, "SCANNER DE CODIGO DE BARRAS", 
                           (info_x, info_y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (50, 50, 50), 3)
                
                cv2.line(canvas, (info_x, info_y+15), (650, info_y+15), (100, 100, 100), 2)
                
                info_y += 70
                camera_name = "PC (Camera 0)" if current_camera == 0 else "Celular (Camera 1)"
                cv2.putText(canvas, f"Camera Ativa: {camera_name}", 
                           (info_x, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 50, 50), 2)
                
                info_y += 50
                cv2.putText(canvas, f"Tentativas de Scan: {scan_attempts}", 
                           (info_x, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 80, 80), 1)
                
                # Decodificar código de barras
                decoded_objects = decode(frame)
                
                if decoded_objects:
                    for obj in decoded_objects:
                        # ✅ LIMPAR O CÓDIGO
                        barcode_raw = obj.data.decode('utf-8')
                        barcode_value = ''.join(c for c in barcode_raw if c.isprintable()).strip()
                        barcode_type = obj.type
                        
                        print(f"\n{'='*70}")
                        print(f"📷 CÓDIGO ESCANEADO NO FORMULÁRIO")
                        print(f"{'='*70}")
                        print(f"Código bruto: '{barcode_raw}' (tamanho: {len(barcode_raw)})")
                        print(f"Código limpo: '{barcode_value}' (tamanho: {len(barcode_value)})")
                        print(f"Tipo: {barcode_type}")
                        print(f"{'='*70}\n")
                        
                        # Mostrar código encontrado
                        info_y += 60
                        cv2.rectangle(canvas, (info_x-10, info_y-35), 
                                     (650, info_y+20), (50, 200, 50), -1)
                        cv2.putText(canvas, "CODIGO DETECTADO!", 
                                   (info_x, info_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                        
                        info_y += 50
                        cv2.putText(canvas, f"Tipo: {barcode_type}", 
                                   (info_x, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 50, 50), 1)
                        
                        info_y += 40
                        cv2.putText(canvas, f"Codigo: {barcode_value}", 
                                   (info_x, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (50, 50, 50), 2)
                        
                        # Desenhar retângulo
                        points = obj.polygon
                        if len(points) == 4:
                            pts = [(int(p.x * camera_width / frame.shape[1]), 
                                   int(p.y * camera_height / frame.shape[0])) for p in points]
                            for i in range(4):
                                cv2.line(small_frame, pts[i], pts[(i+1)%4], (0, 255, 0), 3)
                            canvas[camera_y:camera_y+camera_height, camera_x:camera_x+camera_width] = small_frame
                        
                        break
                else:
                    info_y += 60
                    cv2.rectangle(canvas, (info_x-10, info_y-35), 
                                 (650, info_y+20), (200, 200, 50), -1)
                    cv2.putText(canvas, "Aguardando codigo...", 
                               (info_x, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (50, 50, 50), 2)
                
                # Instruções
                info_y = 400
                cv2.putText(canvas, "INSTRUCOES:", 
                           (info_x, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 50, 50), 2)
                
                instructions = [
                    "• Posicione o codigo de barras na frente da camera",
                    "• Pressione 'C' para alternar entre cameras",
                    "• Pressione 'Q' ou 'ESC' para sair",
                    "• O codigo sera detectado automaticamente"
                ]
                
                for i, instruction in enumerate(instructions):
                    info_y += 35
                    cv2.putText(canvas, instruction, 
                               (info_x, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 80, 80), 1)
                
                # Botões
                button_y = 520
                
                cv2.rectangle(canvas, (info_x, button_y), (info_x+280, button_y+50), (0, 120, 255), -1)
                cv2.rectangle(canvas, (info_x, button_y), (info_x+280, button_y+50), (0, 80, 200), 2)
                cv2.putText(canvas, "[C] Alternar Camera", 
                           (info_x+20, button_y+32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.rectangle(canvas, (info_x+300, button_y), (info_x+500, button_y+50), (200, 50, 50), -1)
                cv2.rectangle(canvas, (info_x+300, button_y), (info_x+500, button_y+50), (150, 30, 30), 2)
                cv2.putText(canvas, "[Q] Sair", 
                           (info_x+340, button_y+32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow(window_name, canvas)
                
                # Capturar teclas
                key = cv2.waitKey(1) & 0xFF
                
                if barcode_value or key == ord('q') or key == 27:
                    break
                elif key == ord('c') or key == ord('C'):
                    cap.release()
                    current_camera = 1 if current_camera == 0 else 0
                    cap = cv2.VideoCapture(current_camera)
                    scan_attempts = 0
                    
                    if not cap.isOpened():
                        Clock.schedule_once(lambda dt: self.admin_screen.show_popup(
                            "Erro", f"Não foi possível abrir a câmera {current_camera}!"))
                        current_camera = 1 if current_camera == 0 else 0
                        cap = cv2.VideoCapture(current_camera)
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.scanning = False
            
            # ✅ ATUALIZAR UI NA THREAD PRINCIPAL usando Clock
            if barcode_value:
                Clock.schedule_once(lambda dt: self._handle_barcode_success(barcode_value))

    def _handle_barcode_success(self, barcode_value):
        """Tratar sucesso do scan na thread principal (sem threading issues)"""
        self.barcode_input.text = barcode_value
        self.admin_screen.show_popup("Sucesso", f"Código detectado: {barcode_value}")

    # ================= SAVE =================
    def save_product(self, instance):
        try:
            # Validações
            if not self.description.text.strip():
                self.admin_screen.show_popup("Erro", "A descrição é obrigatória!")
                return
            
            if self.category_spinner.text == "Selecionar":
                self.admin_screen.show_popup("Erro", "Selecione uma categoria!")
                return
            
            if not self.existing_stock.text.strip():
                self.admin_screen.show_popup("Erro", "O estoque existente é obrigatório!")
                return
            
            if not self.sale_price.text.strip():
                self.admin_screen.show_popup("Erro", "O preço de venda é obrigatório!")
                return
            
            if not self.total_purchase_price.text.strip():
                self.admin_screen.show_popup("Erro", "O preço de compra total é obrigatório!")
                return
            
            if not self.unit_purchase_price.text.strip():
                self.admin_screen.show_popup("Erro", "O preço de compra unitário é obrigatório!")
                return

            # Data de validade
            expiry = None
            if self.expiry_date.text.strip():
                try:
                    expiry_dt = datetime.strptime(self.expiry_date.text.strip(), "%d/%m/%Y")
                    expiry = expiry_dt.strftime("%Y-%m-%d")
                except ValueError:
                    self.admin_screen.show_popup(
                        "Erro",
                        "Data de validade inválida! Use o formato DD/MM/AAAA"
                    )
                    return

            # Código de barras (limpar)
            barcode_text = self.barcode_input.text.strip()
            barcode = ''.join(c for c in barcode_text if c.isprintable()).strip() if barcode_text else None

            # Vendido por KG
            is_sold_by_weight = self.is_sold_by_weight_switch.active

            # ✅ CRIAR CONEXÃO NOVA NA THREAD PRINCIPAL
            db = Database()

            if self.product:
                db.update_product(
                    self.product[0],
                    self.description.text.strip(),
                    self.category_spinner.text,
                    float(self.existing_stock.text),  # Agora aceita decimal
                    float(self.sold_stock.text),      # Agora aceita decimal
                    float(self.sale_price.text),
                    float(self.total_purchase_price.text),
                    float(self.unit_purchase_price.text),
                    barcode,
                    expiry,
                    is_sold_by_weight  # NOVO PARÂMETRO
                )
                self.admin_screen.show_popup("Sucesso", "Produto atualizado com sucesso!")
            else:
                db.add_product(
                    self.description.text.strip(),
                    self.category_spinner.text,
                    float(self.existing_stock.text),  # Agora aceita decimal
                    float(self.sold_stock.text),      # Agora aceita decimal
                    float(self.sale_price.text),
                    float(self.total_purchase_price.text),
                    float(self.unit_purchase_price.text),
                    barcode,
                    expiry,
                    is_sold_by_weight  # NOVO PARÂMETRO
                )
                self.admin_screen.show_popup("Sucesso", "Produto adicionado com sucesso!")

            db.close()
            self.dismiss()
            self.admin_screen.load_products()

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

    def on_window_resize(self, instance, width, height):
        self.size = (
            min(dp(700), width * 0.9),
            min(dp(750), height * 0.9)
        )
    
    def on_dismiss(self):
        """Parar scanner ao fechar popup"""
        self.scanning = False
        if self.scanner_thread and self.scanner_thread.is_alive():
            self.scanner_thread.join(timeout=1)



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

        for product in products_to_display:
            # ID - 0.07
            id_label = Label(
                text=str(product[0]), 
                size_hint_x=0.07, 
                color=[0, 0, 0, 1],
                halign='center',
                valign='middle'
            )
            
            # Descrição - 0.18
            desc_label = Label(
                text=product[1], 
                size_hint_x=0.18, 
                color=[0, 0, 0, 1],
                text_size=(None, None), 
                shorten=True, 
                halign='center',
                valign='middle'
            )
            
            # Verificar se é vendido por peso (índice 15)
            is_sold_by_weight = product[15] if len(product) > 15 else 0
            unit_label = "kg" if is_sold_by_weight else "un"
            
            # Estoque - 0.09
            stock_value = product[2]
            stock_text = f"{stock_value:.2f} {unit_label}" if is_sold_by_weight else f"{int(stock_value)} {unit_label}"
            stock_label = Label(
                text=stock_text, 
                size_hint_x=0.09, 
                color=[0, 0, 0, 1],
                halign='center',
                valign='middle'
            )
            
            # Vendido - 0.09
            sold_value = product[3]
            sold_text = f"{sold_value:.2f} {unit_label}" if is_sold_by_weight else f"{int(sold_value)} {unit_label}"
            sold_stock_label = Label(
                text=sold_text, 
                size_hint_x=0.09, 
                color=[0, 0, 0, 1],
                halign='center',
                valign='middle'
            )
            
            # Tipo de Venda - 0.09 - ATUALIZADO
            tipo_venda_label = Label(
                text="Por KG" if is_sold_by_weight else "Por Unidade", 
                size_hint_x=0.09, 
                color=[0.8, 0.4, 0.0, 1] if is_sold_by_weight else [0.1, 0.5, 0.8, 1],
                halign='center',
                valign='middle',
                bold=True
            )
            
            # Preço - 0.11
            price_label = Label(
                text=f"MZN {product[4]:.2f}", 
                size_hint_x=0.11, 
                color=[0, 0, 0, 1],
                halign='center',
                valign='middle'
            )
            
            # Lucro - 0.11
            total_profit_label = Label(
                text=f"MZN {product[8]:.2f}", 
                size_hint_x=0.11, 
                color=[0, 0, 0, 1],
                halign='center',
                valign='middle'
            )
            
            # Data de Adição - 0.12
            date_added = str(product[14]) if len(product) > 14 and product[14] else "N/A"
            date_label = Label(
                text=self.format_datetime(date_added), 
                size_hint_x=0.12, 
                color=[0, 0, 0, 1],
                halign='center',
                valign='middle',
                font_size='11sp'
            )
            
            # Ações - 0.14
            action_layout = BoxLayout(spacing=5, size_hint_x=0.14)
            
            # Criar botões com bordas coloridas
            detail_btn = self.create_detail_button(product[0])
            edit_btn = self.create_edit_button(product)
            delete_btn = self.create_delete_button(product[0])
            
            # Adicionar botões ao layout de ações
            action_layout.add_widget(detail_btn)
            action_layout.add_widget(edit_btn)
            action_layout.add_widget(delete_btn)
            
            # Adicionar todos os widgets à tabela (9 colunas)
            self.product_table.add_widget(id_label)
            self.product_table.add_widget(desc_label)
            self.product_table.add_widget(stock_label)
            self.product_table.add_widget(sold_stock_label)
            self.product_table.add_widget(tipo_venda_label)  # TIPO DE VENDA
            self.product_table.add_widget(price_label)
            self.product_table.add_widget(total_profit_label)
            self.product_table.add_widget(date_label)
            self.product_table.add_widget(action_layout)
    
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
        """Alternar entre mostrar todos os produtos e apenas produtos com peso"""
        if not hasattr(self, 'showing_kg_only'):
            self.showing_kg_only = False
        
        self.showing_kg_only = not self.showing_kg_only
        
        if self.showing_kg_only:
            # Mostrar apenas produtos com peso > 0
            kg_products = self.db.get_products_by_weight()
            if kg_products:
                self.update_product_table(kg_products)
                self.show_popup("Filtro Ativo", f"Mostrando {len(kg_products)} produto(s) com peso cadastrado.")
            else:
                self.show_popup("Aviso", "Nenhum produto com peso cadastrado encontrado.")
                self.showing_kg_only = False
                self.update_product_table(self.products)
        else:
            # Mostrar todos os produtos
            self.update_product_table(self.products)
            self.show_popup("Filtro Removido", "Mostrando todos os produtos.")
    
    def logout(self):
        self.manager.current = "login"