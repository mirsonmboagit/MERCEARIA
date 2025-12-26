from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.garden import matplotlib
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sqlite3
from kivy.metrics import dp, sp
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from num2words import num2words
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.widget import Widget
import os
from kivy.lang import Builder


Builder.load_string('''

<ReportsScreen>:
    name: 'reports'

    BoxLayout:
        orientation: 'vertical'
        spacing: 20
        padding: 20
        canvas.before:
            Color:
                rgba: 0.98, 0.98, 0.98, 1
            Rectangle:
                pos: self.pos
                size: self.size

        # Cabeçalho
        BoxLayout:
            size_hint_y: None
            height: 80
            spacing: 10

            Label:
                text: 'Relatórios de Produtos'
                font_size: '28sp'
                bold: True
                halign: 'left'
                valign: 'middle'
                color: 0.2, 0.2, 0.2, 1
                size_hint_x: 0.8

            Button:
                text: '<--Voltar---'
                size_hint: None, None
                size: 120, 50
                background_color: 0, 0, 0, 0
                color: 0.9, 0.3, 0.3, 1
                on_release: root.go_back()
                bold: True
                canvas.before:
                    Color:
                        rgba: 0.9, 0.3, 0.3, 1
                    Line:
                        width: 0.5
                        rounded_rectangle: (*self.pos, *self.size, 10)

        # Filtros de pesquisa
        BoxLayout:
            orientation: 'vertical'
            spacing: 15
            size_hint_y: None
            height: self.minimum_height
            padding: [0, 10]

            # Filtro de Período
            BoxLayout:
                size_hint_y: None
                height: 50
                spacing: 10

                Label:
                    text: 'Período:'
                    font_size: '18sp'
                    bold: True
                    halign: 'left'
                    color: 0.3, 0.3, 0.3, 1
                    size_hint_x: 0.5

                BoxLayout:
                    size_hint_x: 0.6
                    spacing: 10

                    Label:
                        id: date_label
                        text: 'Selecione um período'
                        font_size: '16sp'
                        color: 0.6, 0.6, 0.6, 1

                    Button:
                        text: 'Selecionar'
                        size_hint: None, None
                        size: 120, 45
                        bold: True
                        background_color: 0, 0, 0, 0
                        color: 0.2, 0.6, 0.8, 1
                        on_release: root.select_date_range()
                        canvas.before:
                            Color:
                                rgba: 0.2, 0.6, 0.8, 1
                            Line:
                                width: 0.5
                                rounded_rectangle: (*self.pos, *self.size, 10)

            # Filtro de Produto
            BoxLayout:
                size_hint_y: None
                height: 50
                spacing: 10

                Label:
                    text: 'Produto:'
                    font_size: '18sp'
                    bold: True
                    halign: 'left'
                    color: 0.3, 0.3, 0.3, 1
                    size_hint_x: 0.84

                Spinner:
                    id: product_spinner
                    text: 'Todos os Produtos'
                    values: ['Todos os Produtos']
                    font_size: '16sp'
                    bold: True
                    background_color: 0, 0, 0, 0
                    color: 0, 0, 0, 1
                    on_text: root.update_product_selection(self, self.text)
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 1
                        Line:
                            width: 0.5
                            rounded_rectangle: (*self.pos, *self.size, 10)

            # Filtro de Categoria
            BoxLayout:
                size_hint_y: None
                height: 50
                spacing: 10

                Label:
                    text: 'Categoria:'
                    font_size: '18sp'
                    bold: True
                    halign: 'left'
                    color: 0.3, 0.3, 0.3, 1
                    size_hint_x: 0.85

                Spinner:
                    id: category_spinner
                    text: 'Todas as Categorias'
                    values: ['Todas as Categorias']
                    font_size: '16sp'
                    bold: True
                    background_color: 0, 0, 0, 0
                    color: 0, 0, 0, 1
                    on_text: root.update_category_selection(self, self.text)
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 1
                        Line:
                            width: 0.5
                            rounded_rectangle: (*self.pos, *self.size, 10)

        # Botão para gerar relatório
        BoxLayout:
            size_hint_y: None
            height: 60
            padding: [0, 10]

            Button:
                text: 'Gerar Relatório'
                font_size: '18sp'
                bold: True
                background_color: 0, 0, 0, 0
                color: 0.1, 0.7, 0.3, 1
                on_release: root.generate_report()
                size_hint: None, None
                size: 200, 50
                pos_hint: {'center_x': 0.5}
                canvas.before:
                    Color:
                        rgba: 0.1, 0.7, 0.3, 1
                    Line:
                        width: 0.5
                        rounded_rectangle: (*self.pos, *self.size, 10)

        # Área para visualização de informações
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.3
            padding: [10, 10]
            canvas.before:
                Color:
                    rgba: 0.98, 0.98, 0.98, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Label:
                text: 'Selecione os filtros acima e clique em "Gerar Relatório"\\npara criar um relatório detalhado e personalizado.'
                color: 0, 0, 0, 1
                font_size: '16sp'
                text_size: self.width, None
                halign: 'center'
                valign: 'middle'

''')

class DateRangePopup(Popup):
    def __init__(self, callback, **kwargs):
        super(DateRangePopup, self).__init__(**kwargs)
        self.title = "Selecionar Período"
        self.size_hint = (0.5, 0.4)
        self.auto_dismiss = True
        self.callback = callback
        
        # Centralizar o popup na tela e impedir deslocamento
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=[20, 20])
        
        date_layout = BoxLayout(
            spacing=dp(10), 
            size_hint_y=None, 
            height=dp(50))
        date_layout.add_widget(Label(text="Data Inicial:"))
        self.start_date = TextInput(hint_text="DD/MM/AAAA")
        date_layout.add_widget(self.start_date)
        date_layout.add_widget(Label(text="Data Final:"))
        self.end_date = TextInput(hint_text="DD/MM/AAAA")
        date_layout.add_widget(self.end_date)
        
        # Adicionar botões predefinidos para períodos comuns
        period_layout = BoxLayout(
            spacing=dp(10), 
            size_hint_y=None, 
            height=dp(50))
        periods = [
            ("Hoje", self.set_today),
            ("7 Dias", lambda instance: self.set_days(7, instance)),
            ("30 Dias", lambda instance: self.set_days(30, instance)),
            ("Este Mês", self.set_this_month)
        ]
        
        for label, func in periods:
            btn = Button(text=label)
            btn.bind(on_release=func)
            period_layout.add_widget(btn)
        
        button_layout = BoxLayout(
            spacing=dp(10), 
            size_hint_y=None, 
            height=dp(50))
        cancel_btn = Button(text="Cancelar")
        cancel_btn.bind(on_release=self.dismiss)
        confirm_btn = Button(text="Confirmar")
        confirm_btn.bind(on_release=self.confirm)
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(confirm_btn)
        
        layout.add_widget(date_layout)
        layout.add_widget(period_layout)
        layout.add_widget(button_layout)
        
        self.content = layout
        
        # Adicionar bind para reposicionar o popup quando a janela mudar de tamanho
        Window.bind(on_resize=self.reposition)
    
    def reposition(self, instance, width, height):
        # Recalcular a posição do popup para mantê-lo centralizado
        if self.parent:
            self.center = Window.center
    
    def open(self, *args, **kwargs):
        # Sobrescrever o método open para garantir posicionamento correto
        super(DateRangePopup, self).open(*args, **kwargs)
        self.center = Window.center
    
    def set_today(self, instance):
        today = datetime.now().strftime("%d/%m/%Y")
        self.start_date.text = today
        self.end_date.text = today
    
    def set_days(self, days, instance):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        self.start_date.text = start_date.strftime("%d/%m/%Y")
        self.end_date.text = end_date.strftime("%d/%m/%Y")
    
    def set_this_month(self, instance):
        today = datetime.now()
        start_date = datetime(today.year, today.month, 1)
        self.start_date.text = start_date.strftime("%d/%m/%Y")
        self.end_date.text = today.strftime("%d/%m/%Y")
    
    def confirm(self, instance):
        try:
            start = datetime.strptime(self.start_date.text, "%d/%m/%Y")
            end = datetime.strptime(self.end_date.text, "%d/%m/%Y")
            # Ajusta o final do dia para incluir todo o dia final
            end = end.replace(hour=23, minute=59, second=59)
            
            self.callback(start, end)
            self.dismiss()
        except ValueError:
            error_popup = Popup(title='Erro', 
                               content=Label(text='Formato de data inválido. Use DD/MM/AAAA'),
                               size_hint=(0.7, 0.3))
            error_popup.open()

class ReportsScreen(Screen):
    def __init__(self, **kwargs):
        super(ReportsScreen, self).__init__(**kwargs)
        self.start_date = None
        self.end_date = None
        self.selected_product = None
        self.selected_category = None
        self.db_path = 'inventory.db'  # Ajuste conforme o caminho do seu banco de dados
    
    def on_enter(self):
        self.load_filters()
    
    def load_filters(self):
        # Carregar produtos do banco de dados para o filtro
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obter lista de produtos - CORRIGIDO
        cursor.execute("SELECT id, description FROM products ORDER BY description")
        products = cursor.fetchall()
        product_list = ["Todos os Produtos"] + [f"{prod[0]} - {prod[1]}" for prod in products]
        self.ids.product_spinner.values = product_list
        
        # Obter lista de categorias - CORRIGIDO
        cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category")
        categories = cursor.fetchall()
        category_list = ["Todas as Categorias"] + [cat[0] for cat in categories]
        self.ids.category_spinner.values = category_list
        
        conn.close()
    
    def select_date_range(self):
        popup = DateRangePopup(callback=self.set_date_range)
        popup.open()
    
    def set_date_range(self, start, end):
        self.start_date = start
        self.end_date = end
        self.ids.date_label.text = f"Período: {start.strftime('%d/%m/%Y')} a {end.strftime('%d/%m/%Y')}"
    
    def update_product_selection(self, spinner, text):
        if text == "Todos os Produtos":
            self.selected_product = None
        else:
            try:
                self.selected_product = int(text.split(" - ")[0])
            except:
                self.selected_product = None
    
    def update_category_selection(self, spinner, text):
        if text == "Todas as Categorias":
            self.selected_category = None
        else:
            self.selected_category = text
    
    def generate_report(self):
        if not self.start_date or not self.end_date:
            error_popup = Popup(title='Erro')
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(Label(text='Selecione um período para o relatório', 
                                   size_hint_y=None, height=dp(30)))
            close_btn = Button(text='Fechar', size_hint_y=None, height=dp(40))
            close_btn.bind(on_release=error_popup.dismiss)
            content.add_widget(Widget(size_hint_y=1))  # Espaçador flexível
            content.add_widget(close_btn)
            error_popup.content = content
            error_popup.size_hint = (None, None)
            error_popup.size = (min(500, Window.width * 0.8), min(300, Window.height * 0.5))
            error_popup.open()
            return
        
        # Construir a consulta SQL com base nos filtros
        query = """
        SELECT p.id, p.description, p.existing_stock, p.sold_stock, 
            p.sale_price, p.total_purchase_price, p.unit_purchase_price,
            p.category, p.date_added
        FROM products p
        WHERE 1=1
        """
        params = []
        
        # Adicionar filtro de data - CORRIGIDO: date_added em vez de data_adicao
        query += " AND p.date_added BETWEEN ? AND ?"
        params.append(self.start_date.strftime("%Y-%m-%d %H:%M:%S"))
        params.append(self.end_date.strftime("%Y-%m-%d %H:%M:%S"))
        
        # Adicionar filtro de produto
        if self.selected_product:
            query += " AND p.id = ?"
            params.append(self.selected_product)
        
        # Adicionar filtro de categoria - CORRIGIDO: category em vez de categoria
        if self.selected_category:
            query += " AND p.category = ?"
            params.append(self.selected_category)
        
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if df.empty:
            error_popup = Popup(title='Aviso')
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(Label(text='Nenhum dado encontrado para os filtros selecionados', 
                                   size_hint_y=None, height=dp(30)))
            close_btn = Button(text='Fechar', size_hint_y=None, height=dp(40))
            close_btn.bind(on_release=error_popup.dismiss)
            content.add_widget(Widget(size_hint_y=1))  # Espaçador flexível
            content.add_widget(close_btn)
            error_popup.content = content
            error_popup.size_hint = (None, None)
            error_popup.size = (min(500, Window.width * 0.8), min(300, Window.height * 0.5))
            error_popup.open()
            return
        
        # Calcular campos adicionais - CORRIGIDO: nomes de colunas alinhados com o SELECT
        df['estoque_remanescente'] = df['existing_stock'] - df['sold_stock']
        df['lucro_unitario'] = df['sale_price'] - df['unit_purchase_price']
        df['lucro_total'] = df['lucro_unitario'] * df['sold_stock']
        df['percentual_lucro'] = (df['lucro_unitario'] / df['unit_purchase_price']) * 100
        
        # Escolher o tipo de relatório para gerar
        report_popup = Popup(title='Tipo de Relatório')
        report_popup.size_hint = (None, None)
        report_popup.size = (min(600, Window.width * 0.8), min(400, Window.height * 0.6))
        
        # Vamos garantir que o popup seja centralizando quando redimensionado
        def update_popup_size(instance, value):
            report_popup.size = (min(600, Window.width * 0.8), min(400, Window.height * 0.6))
            report_popup.center = Window.center
        
        Window.bind(size=update_popup_size)
        report_popup.bind(on_dismiss=lambda instance: Window.unbind(size=update_popup_size))
        
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        layout.add_widget(Label(text='Escolha o tipo de relatório:', 
                               size_hint_y=None, height=dp(40)))
        
        # Grid para botões para melhor adaptação em diferentes tamanhos de tela
        buttons_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))
        
        # Botão para relatório de vendas
        sales_btn = Button(text='Relatório de Vendas')
        sales_btn.bind(on_release=lambda x: self.generate_sales_report(df, report_popup))
        buttons_grid.add_widget(sales_btn)
        
        # Botão para relatório de estoque
        stock_btn = Button(text='Relatório de Estoque')
        stock_btn.bind(on_release=lambda x: self.generate_stock_report(df, report_popup))
        buttons_grid.add_widget(stock_btn)
        
        # Botão para relatório de lucro
        profit_btn = Button(text='Relatório de Lucro')
        profit_btn.bind(on_release=lambda x: self.generate_profit_report(df, report_popup))
        buttons_grid.add_widget(profit_btn)
        
        # Botão para relatório completo
        complete_btn = Button(text='Relatório Completo (PDF)')
        complete_btn.bind(on_release=lambda x: self.generate_pdf_report(df, report_popup))
        buttons_grid.add_widget(complete_btn)
        
        layout.add_widget(buttons_grid)
        
        # Espaçador flexível
        layout.add_widget(Widget(size_hint_y=1))
        
        # Botão para cancelar
        cancel_btn = Button(text='Cancelar', size_hint_y=None, height=dp(40))
        cancel_btn.bind(on_release=report_popup.dismiss)
        layout.add_widget(cancel_btn)
        
        report_popup.content = layout
        report_popup.open()
    
    def generate_sales_report(self, df, parent_popup):
        parent_popup.dismiss()
        
        # Criar gráfico de vendas por produto - Gráfico de barras
        plt.figure(figsize=(10, 6))
        sales_data = df.sort_values('sold_stock', ascending=False).head(10)
        plt.bar(sales_data['description'], sales_data['sold_stock'], color='blue')
        plt.title('Top 10 Produtos com Maior Vendas')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Criar popup para mostrar o gráfico
        graph_popup = Popup(title='Relatório de Vendas')
        graph_popup.size_hint = (None, None)
        graph_popup.size = (min(800, Window.width * 0.9), min(600, Window.height * 0.9))
        
        # Vamos garantir que o popup seja centralizando quando redimensionado
        def update_graph_popup_size(instance, value):
            graph_popup.size = (min(800, Window.width * 0.9), min(600, Window.height * 0.9))
            graph_popup.center = Window.center
        
        Window.bind(size=update_graph_popup_size)
        graph_popup.bind(on_dismiss=lambda instance: Window.unbind(size=update_graph_popup_size))
        
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        
        # Adicionar o gráfico ao layout
        chart = FigureCanvasKivyAgg(plt.gcf())
        layout.add_widget(chart)
        
        # Adicionar as estatísticas de vendas
        stats_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None, height=dp(90))
        stats_layout.add_widget(Label(text=f"Total de Produtos: {len(df)}"))
        stats_layout.add_widget(Label(text=f"Total de Unidades Vendidas: {df['sold_stock'].sum()}"))
        stats_layout.add_widget(Label(text=f"Valor Total de Vendas: MZN {df['sale_price'].mul(df['sold_stock']).sum():.2f}"))
        layout.add_widget(stats_layout)
        
        # Layout para botões
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        
        # Botão para gerar relatório em CSV
        export_btn = Button(text="Exportar Relatório")
        export_btn.bind(on_release=lambda instance: self.export_sales_report(df))
        button_layout.add_widget(export_btn)

        # Botão para fechar o popup
        close_btn = Button(text="Fechar")
        close_btn.bind(on_release=graph_popup.dismiss)
        button_layout.add_widget(close_btn)
        
        layout.add_widget(button_layout)

        graph_popup.content = layout
        graph_popup.open()
        
    def export_sales_report(self, df):
        try:
            # Criar diretório "Relatório de Vendas" se não existir
            report_dir = "Relatório de Vendas"
            os.makedirs(report_dir, exist_ok=True)
            
            # Gerar timestamp único para o nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            graph_path = os.path.join(report_dir, f"sales_chart_{timestamp}.png")
            pdf_path = os.path.join(report_dir, f"relatorio_vendas_{timestamp}.pdf")
            
            # Criar gráfico de vendas
            plt.figure(figsize=(10, 6))
            sales_data = df.sort_values('sold_stock', ascending=False).head(10)
            plt.bar(sales_data['description'], sales_data['sold_stock'], color='blue')
            plt.title('Top 10 Produtos com Maior Vendas')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(graph_path)
            plt.close()
            
            # Notificar o usuário sobre o sucesso da exportação
            success_popup = Popup(title='Sucesso')
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(Label(text=f'Relatório exportado com sucesso para:\n{report_dir}', 
                                  size_hint_y=None, height=dp(60)))
            close_btn = Button(text='Fechar', size_hint_y=None, height=dp(40))
            close_btn.bind(on_release=success_popup.dismiss)
            content.add_widget(Widget(size_hint_y=1))  # Espaçador flexível
            content.add_widget(close_btn)
            success_popup.content = content
            success_popup.size_hint = (None, None)
            success_popup.size = (min(500, Window.width * 0.8), min(300, Window.height * 0.5))
            success_popup.open()
            
        except Exception as e:
            # Mostrar erro se houver problemas na exportação
            error_popup = Popup(title='Erro')
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(Label(text=f'Erro ao exportar relatório:\n{str(e)}', 
                                  size_hint_y=None, height=dp(60)))
            close_btn = Button(text='Fechar', size_hint_y=None, height=dp(40))
            close_btn.bind(on_release=error_popup.dismiss)
            content.add_widget(Widget(size_hint_y=1))  # Espaçador flexível
            content.add_widget(close_btn)
            error_popup.content = content
            error_popup.size_hint = (None, None)
            error_popup.size = (min(500, Window.width * 0.8), min(300, Window.height * 0.5))
            error_popup.open()    
            # Criar documento PDF
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Adicionar título ao PDF
            title = Paragraph("<b>Relatório de Vendas</b>", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Adicionar estatísticas
            stats_text = [
                f"Total de Produtos: {len(df)}",
                f"Total de Unidades Vendidas: {df['sold_stock'].sum()}",
                f"Valor Total de Vendas: MZN {df['sale_price'].mul(df['sold_stock']).sum():.2f}"
            ]
            for line in stats_text:
                elements.append(Paragraph(line, styles['Normal']))
            elements.append(Spacer(1, 12))
            
            # Adicionar gráfico ao PDF
            elements.append(Image(graph_path, width=400, height=250))
            elements.append(Spacer(1, 12))
            
            # Criar tabela de vendas
            table_data = [["Produto", "Unidades Vendidas", "Preço de Venda", "Valor Total"]]
            for _, row in sales_data.iterrows():
                table_data.append([
                    row['description'],
                    row['sold_stock'],
                    f"MZN {row['sale_price']:.2f}",
                    f"MZN {row['sale_price'] * row['sold_stock']:.2f}"
                ])
            
            sales_table = Table(table_data)
            sales_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(sales_table)
            
            doc.build(elements)
            print(f"Relatório de Vendas gerado com sucesso: {pdf_path}")
        except Exception as e:
            print(f"Erro ao exportar relatório: {e}")
            
    def generate_stock_report(self, df, parent_popup):
        parent_popup.dismiss()

        # Lógica simples e intuitiva:
        # ENTRADA = Estoque inicial que foi adicionado (existing_stock + sold_stock)
        # SAÍDA = Quantidade vendida (sold_stock)
        # VENDIDO = Mesmo que saída (sold_stock)
        # REMANESCENTE = O que sobrou (existing_stock)
        # TOTAL = Entrada total (ENTRADA)
        
        df['entrada'] = df['existing_stock'] + df['sold_stock']  # Total que entrou inicialmente
        df['saida'] = df['sold_stock']  # Quantidade que saiu (vendida)
        df['remanescente'] = df['existing_stock']  # Quantidade que restou
        df['total_movimentacao'] = df['entrada']  # Total movimentado = entrada inicial

        # Criar popup para mostrar a tabela
        table_popup = Popup(title='Relatório de Estoque', size_hint=(0.9, 0.9))
        main_layout = BoxLayout(orientation='vertical')

        # Adicionar as estatísticas de estoque
        stats_layout = BoxLayout(orientation='vertical', size_hint_y=0.2)
        stats_layout.add_widget(Label(text=f"Total de Produtos: {len(df)}"))
        stats_layout.add_widget(Label(text=f"Estoque Total Inicial: {df['entrada'].sum()}"))
        stats_layout.add_widget(Label(text=f"Estoque Vendido: {df['sold_stock'].sum()}"))
        stats_layout.add_widget(Label(text=f"Estoque Remanescente: {df['existing_stock'].sum()}"))

        # Criar tabela de estoque
        table_layout = BoxLayout(orientation='vertical', size_hint_y=0.6)
        
        # Criar cabeçalho da tabela
        header_layout = GridLayout(cols=6, size_hint_y=None, height=40)
        headers = ['Produto', 'Entrada', 'Saída', 'Vendido', 'Remanescente', 'Total']
        for header in headers:
            header_layout.add_widget(Label(text=header, bold=True))
        
        table_layout.add_widget(header_layout)

        # Criar scroll view para a tabela
        scroll_view = ScrollView(size_hint=(1, 1))
        grid_layout = GridLayout(cols=6, size_hint_y=None)
        grid_layout.bind(minimum_height=grid_layout.setter('height'))
        
        # Preencher tabela com dados
        for _, row in df.iterrows():
            grid_layout.add_widget(Label(text=str(row['description']), size_hint_y=None, height=30))
            grid_layout.add_widget(Label(text=str(int(row['entrada'])), size_hint_y=None, height=30))
            grid_layout.add_widget(Label(text=str(int(row['saida'])), size_hint_y=None, height=30))
            grid_layout.add_widget(Label(text=str(int(row['sold_stock'])), size_hint_y=None, height=30))
            grid_layout.add_widget(Label(text=str(int(row['remanescente'])), size_hint_y=None, height=30))
            grid_layout.add_widget(Label(text=str(int(row['total_movimentacao'])), size_hint_y=None, height=30))
        
        scroll_view.add_widget(grid_layout)
        table_layout.add_widget(scroll_view)

        # Layout para botões
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=10, padding=[10, 0, 10, 0])
        
        # Botão para gerar relatório em PDF
        export_btn = Button(text="Exportar Relatório", size_hint_x=0.5)
        export_btn.bind(on_release=lambda instance: self.export_stock_report(df, table_popup))
        
        # Botão para fechar
        close_btn = Button(text="Fechar", size_hint_x=0.5)
        close_btn.bind(on_release=table_popup.dismiss)

        buttons_layout.add_widget(export_btn)
        buttons_layout.add_widget(close_btn)

        main_layout.add_widget(stats_layout)
        main_layout.add_widget(table_layout)
        main_layout.add_widget(buttons_layout)
        
        table_popup.content = main_layout
        table_popup.open()


    def export_stock_report(self, df, parent_popup=None):
        try:
            # Criar diretório "Relatório de Stock" se não existir
            report_dir = "Relatório de Stock"
            os.makedirs(report_dir, exist_ok=True)

            # Gerar timestamp único para o nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = os.path.join(report_dir, f"relatorio_stock_{timestamp}.pdf")

            # Aplicar a mesma lógica do relatório
            df['entrada'] = df['existing_stock'] + df['sold_stock']  # Total que entrou inicialmente
            df['saida'] = df['sold_stock']  # Quantidade que saiu (vendida)
            df['remanescente'] = df['existing_stock']  # Quantidade que restou
            df['total_movimentacao'] = df['entrada']  # Total movimentado = entrada inicial

            # Criar o documento PDF
            doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter))
            styles = getSampleStyleSheet()
            elements = []

            # Adicionar título ao PDF
            title = Paragraph("<b>Relatório de Estoque</b>", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 12))

            # Adicionar data e hora
            date_text = Paragraph(f"<i>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>", styles['Normal'])
            elements.append(date_text)
            elements.append(Spacer(1, 12))

            # Adicionar estatísticas
            stats_text = [
                f"Total de Produtos: {len(df)}",
                f"Estoque Total Inicial: {int(df['entrada'].sum())}",
                f"Estoque Vendido: {int(df['sold_stock'].sum())}",
                f"Estoque Remanescente: {int(df['existing_stock'].sum())}"
            ]
            for line in stats_text:
                elements.append(Paragraph(line, styles['Normal']))
            elements.append(Spacer(1, 12))

            # Criar tabela completa com todos os produtos
            table_data = [["Produto", "Entrada", "Saída", "Vendido", "Remanescente", "Total"]]  # Cabeçalho
            for _, row in df.iterrows():
                table_data.append([
                    row['description'], 
                    int(row['entrada']), 
                    int(row['saida']), 
                    int(row['sold_stock']), 
                    int(row['remanescente']),
                    int(row['total_movimentacao'])
                ])

            # Criar e estilizar a tabela
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 12))

            # Construir PDF
            doc.build(elements) 
            print(f"Relatório de Stock gerado com sucesso: {pdf_path}")
            
            # Mostrar popup com opção para visualizar o PDF
            self.show_pdf_viewer_popup(pdf_path, parent_popup)
            
        except Exception as e:
            print(f"Erro ao exportar relatório: {e}")

    def show_pdf_viewer_popup(self, pdf_path, parent_popup=None):
        """Mostra um popup com botões para visualizar o PDF gerado"""
        
        # Criar popup de confirmação
        confirm_popup = Popup(title='Relatório Gerado', size_hint=(0.5, 0.3))
        
        # Layout para o conteúdo do popup
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Mensagem de confirmação
        layout.add_widget(Label(text=f"Relatório gerado com sucesso em:\n{pdf_path}"))
        
        # Layout para botões
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.4)
        
        # Botão para visualizar o PDF
        view_btn = Button(text="Visualizar PDF")
        view_btn.bind(on_release=lambda instance: self.open_pdf(pdf_path))
        
        # Botão para fechar o popup
        close_btn = Button(text="Fechar")
        close_btn.bind(on_release=confirm_popup.dismiss)
        
        # Adicionar botões ao layout
        buttons_layout.add_widget(view_btn)
        buttons_layout.add_widget(close_btn)
        
        # Adicionar o layout de botões ao layout principal
        layout.add_widget(buttons_layout)
        
        # Definir o conteúdo do popup
        confirm_popup.content = layout
        
        # Abrir o popup
        confirm_popup.open()    


    def open_pdf(self, pdf_path):
        """Abre o arquivo PDF com o visualizador padrão do sistema"""
        try:
            import platform
            import subprocess
            
            system = platform.system()
            
            if system == 'Windows':
                os.startfile(pdf_path)
            elif system == 'Darwin':  # macOS
                subprocess.call(['open', pdf_path])
            else:  # Linux e outros
                subprocess.call(['xdg-open', pdf_path])
                
            print(f"PDF aberto: {pdf_path}")
        except Exception as e:
            print(f"Erro ao abrir o PDF: {e}")

    
    def generate_profit_report(self, df, parent_popup):
        parent_popup.dismiss()
        
        # Criar popup para mostrar os dados em formato de tabela
        table_popup = Popup(title='Relatório de Lucro', size_hint=(0.9, 0.9))
        main_layout = BoxLayout(orientation='vertical')
        
        # Adicionar as estatísticas de lucro
        stats_layout = BoxLayout(orientation='vertical', size_hint_y=0.2)
        stats_layout.add_widget(Label(text=f"Total de Produtos: {len(df)}"))
        stats_layout.add_widget(Label(text=f"Lucro Total: MZN {df['lucro_total'].sum():.2f}"))
        stats_layout.add_widget(Label(text=f"Lucro Médio por Produto: MZN {df['lucro_total'].mean():.2f}"))
        stats_layout.add_widget(Label(text=f"Percentual Médio de Lucro: {df['percentual_lucro'].mean():.2f}%"))
        
        # Criar tabela para mostrar os produtos com maior lucro
        profit_data = df.sort_values('lucro_total', ascending=False).head(10)
        
        # Criar layout para a tabela
        table_layout = GridLayout(cols=3, size_hint_y=0.6, spacing=2)
        table_layout.padding = [10, 10, 10, 10]
        
        # Adicionar cabeçalho da tabela
        table_layout.add_widget(Label(text="Produto", bold=True, size_hint_y=None, height=40))
        table_layout.add_widget(Label(text="Lucro Total (MZN)", bold=True, size_hint_y=None, height=40))
        table_layout.add_widget(Label(text="Percentual de Lucro (%)", bold=True, size_hint_y=None, height=40))
        
        # Adicionar dados à tabela
        for _, row in profit_data.iterrows():
            table_layout.add_widget(Label(text=str(row['description']), size_hint_y=None, height=40))
            table_layout.add_widget(Label(text=f"MZN {row['lucro_total']:.2f}", size_hint_y=None, height=40))
            table_layout.add_widget(Label(text=f"{row['percentual_lucro']:.2f}%", size_hint_y=None, height=40))
        
        # Envolver a tabela em um ScrollView para permitir rolagem
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(table_layout)
        
        # Botão para exportar relatório em PDF
        export_btn = Button(text="Exportar Relatório", size_hint_y=0.1)
        export_btn.bind(on_release=lambda instance: self.export_profit_report(df))
        
        # Botão para fechar
        close_btn = Button(text="Fechar", size_hint_y=0.1)
        close_btn.bind(on_release=table_popup.dismiss)
        
        main_layout.add_widget(stats_layout)
        main_layout.add_widget(scroll_view)
        main_layout.add_widget(export_btn)
        main_layout.add_widget(close_btn)
        
        table_popup.content = main_layout
        table_popup.open()

    def export_profit_report(self, df):
        try:
            # Criar diretório "Relatório de Lucro" se não existir
            report_dir = "Relatório de Lucro"
            os.makedirs(report_dir, exist_ok=True)
            
            # Gerar timestamp único para o nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = os.path.join(report_dir, f"relatorio_lucro_{timestamp}.pdf")
            
            # Criar o documento PDF
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Adicionar título ao PDF
            title = Paragraph("<b>Relatório de Lucro</b>", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Adicionar estatísticas
            stats_text = [
                f"Total de Produtos: {len(df)}",
                f"Lucro Total: MZN {df['lucro_total'].sum():.2f}",
                f"Lucro Médio por Produto: MZN {df['lucro_total'].mean():.2f}",
                f"Percentual Médio de Lucro: {df['percentual_lucro'].mean():.2f}%"
            ]
            for line in stats_text:
                elements.append(Paragraph(line, styles['Normal']))
            elements.append(Spacer(1, 12))
            
            # Criar tabela de lucro
            profit_data = df.sort_values('lucro_total', ascending=False).head(10)
            table_data = [["Produto", "Lucro Total (MZN)", "Percentual de Lucro (%)"]]
            for _, row in profit_data.iterrows():
                table_data.append([
                    row['description'],
                    f"MZN {row['lucro_total']:.2f}",
                    f"{row['percentual_lucro']:.2f}%"
                ])
            
            profit_table = Table(table_data)
            profit_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(profit_table)
            
            # Salvar o PDF
            doc.build(elements)
            print(f"Relatório de Lucro gerado com sucesso: {pdf_path}")
        except Exception as e:
            print(f"Erro ao exportar relatório: {e}")

    
    def generate_pdf_report(self, df, parent_popup):
        parent_popup.dismiss()
        
        # Criar um nome para o arquivo baseado na data e hora atual
        filename = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(os.path.expanduser("~"), "Downloads", filename)
        
        # Criar o documento PDF
        doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
        styles = getSampleStyleSheet()
        elements = []
        
        # Título do relatório
        title = Paragraph(f"Relatório de Produtos - {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Informações dos filtros aplicados
        period_text = f"Período: {self.start_date.strftime('%d/%m/%Y')} a {self.end_date.strftime('%d/%m/%Y')}"
        product_text = f"Produto: {self.ids.product_spinner.text}"
        category_text = f"Categoria: {self.ids.category_spinner.text}"
        
        elements.append(Paragraph(period_text, styles['Normal']))
        elements.append(Paragraph(product_text, styles['Normal']))
        elements.append(Paragraph(category_text, styles['Normal']))
        elements.append(Spacer(1, 12))
        
        # Criar a tabela com os dados
        table_data = df[['id', 'description', 'category', 'existing_stock', 'sold_stock', 
                    'estoque_remanescente', 'sale_price', 'unit_purchase_price', 
                    'lucro_unitario', 'lucro_total', 'percentual_lucro']]
        
        # Formatar os valores numéricos
        for col in ['sale_price', 'unit_purchase_price', 'lucro_unitario', 'lucro_total']:
            table_data[col] = table_data[col].apply(lambda x: f"MZN {x:.2f}")
        
        table_data['percentual_lucro'] = table_data['percentual_lucro'].apply(lambda x: f"{x:.2f}%")
        
        # Renomear as colunas para o relatório
        table_data = table_data.rename(columns={
            'id': 'ID',
            'description': 'Descrição',
            'category': 'Categoria',
            'existing_stock': 'Estoque Total',
            'sold_stock': 'Vendido',
            'estoque_remanescente': 'Disponível',
            'sale_price': 'Preço Venda',
            'unit_purchase_price': 'Preço Compra',
            'lucro_unitario': 'Lucro Unit.',
            'lucro_total': 'Lucro Total',
            'percentual_lucro': '% Lucro'
        })
        
        # Adicionar cabeçalho
        header = list(table_data.columns)
        data = [header]
        
        # Adicionar dados
        for _, row in table_data.iterrows():
            data.append(list(row))
        
        # Criar tabela
        table = Table(data)
        
        # Estilo da tabela
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        
        # Adicionar estilo alternado nas linhas para facilitar a leitura
        for i in range(1, len(data), 2):
            style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
        
        table.setStyle(style)
        elements.append(table)
        
        # Adicionar resumo do relatório ao final
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Resumo do Relatório:", styles['Heading2']))
        elements.append(Spacer(1, 6))
        
        # Calcular totais
        total_produtos = len(df)
        total_estoque = df['existing_stock'].sum()
        total_vendido = df['sold_stock'].sum()
        total_disponivel = df['estoque_remanescente'].sum()
        total_valor_estoque = (df['sale_price'] * df['estoque_remanescente']).sum()
        total_valor_vendido = (df['sale_price'] * df['sold_stock']).sum()
        total_lucro = df['lucro_total'].sum()

        # Converter valores para extenso
        total_produtos_extenso = num2words(total_produtos, lang='pt')
        total_estoque_extenso = num2words(total_estoque, lang='pt')
        total_vendido_extenso = num2words(total_vendido, lang='pt')
        total_disponivel_extenso = num2words(total_disponivel, lang='pt')
        total_valor_estoque_extenso = num2words(total_valor_estoque, lang='pt')
        total_valor_vendido_extenso = num2words(total_valor_vendido, lang='pt')
        total_lucro_extenso = num2words(total_lucro, lang='pt')

        # Criar a tabela do resumo
        summary_data = [
            ['Total de Produtos', f'{total_produtos} ({total_produtos_extenso})'],
            ['Total de Estoque', f'{total_estoque} ({total_estoque_extenso})'],
            ['Total Vendido', f'{total_vendido} ({total_vendido_extenso})'],
            ['Total Disponível', f'{total_disponivel} ({total_disponivel_extenso})'],
            ['Valor do Estoque Disponível', f'MZN {total_valor_estoque:.2f} ({total_valor_estoque_extenso})'],
            ['Valor Total Vendido', f'MZN {total_valor_vendido:.2f} ({total_valor_vendido_extenso})'],
            ['Lucro Total', f'MZN {total_lucro:.2f} ({total_lucro_extenso})'],
        ]
        
        # Criar tabela de resumo
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(summary_table)
        
        # Gerar o PDF
        doc.build(elements)
        
        # Informar ao usuário que o relatório foi gerado
        success_popup = Popup(title='Sucesso', 
                            content=Label(text=f'Relatório gerado com sucesso!\nSalvo em: {filepath}'),
                            size_hint=(0.7, 0.3))
        success_popup.open()
    
    def go_back(self):
        self.manager.current = 'admin'