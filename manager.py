from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from database import Database
from datetime import datetime, timedelta
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window 
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder

Builder.load_string('''

<ManagerScreen>:
    sales_table: sales_table
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        
        # Cabeçalho
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 60
            spacing: 10
            
            Label:
                text: "Histórico de Vendas"
                font_size: 24
                bold: True
                size_hint_x: 0.4
                text_size: self.size
                halign: 'left'
                valign: 'middle'
            
            # Botões de ação
            Button:
                text: "Filtrar por Data"
                size_hint_x: 0.2
                background_color: (0.2, 0.4, 0.8, 1)
                on_press: root.show_date_filter()
            
            Button:
                text: "Atualizar"
                size_hint_x: 0.15
                background_color: (0.6, 0.6, 0.6, 1)
                on_press: root.refresh_sales()
            
            Button:
                text: "Nova Venda"
                size_hint_x: 0.2
                background_color: (0.2, 0.6, 0.2, 1)
                on_press: root.new_sale()
            
            Button:
                text: "Sair"
                size_hint_x: 0.05
                background_color: (0.8, 0.2, 0.2, 1)
                on_press: app.stop()
        
        # Tabela de vendas
        ScrollView:
            GridLayout:
                id: sales_table
                cols: 6
                size_hint_y: None
                height: self.minimum_height
                row_default_height: 40
                row_force_default: True
                spacing: 1
                
                # As vendas serão adicionadas dinamicamente pelo Python

''')

class SaleForm(Popup):
    def __init__(self, manager_screen, **kwargs):
        super(SaleForm, self).__init__(**kwargs)
        self.manager_screen = manager_screen
        self.title = "Registrar Venda"
        
        # Configurar tamanho responsivo
        self.configure_responsive_size()
        
        # Obter produtos disponíveis
        db = Database()
        self.products = db.get_products_for_sale()
        
        # Criar dicionário de produtos para referência rápida
        self.product_dict = {f"{p[0]} - {p[1]}": p for p in self.products}
        
        # Lista de itens da venda
        self.sale_items = []
        self.sale_total = 0.0
        self.sale_id = None
        
        self.create_layout()
        
        # Vincular evento de redimensionamento
        Window.bind(on_resize=self.on_window_resize)
    
    def configure_responsive_size(self):
        """Configurar tamanho responsivo baseado no tamanho da tela"""
        screen_width = Window.width
        screen_height = Window.height
        
        # Definir tamanhos baseados no tamanho da tela
        if screen_width < 600:  # Telas muito pequenas (celular)
            self.size_hint = (0.95, 0.95)
            self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        elif screen_width < 1024:  # Tablets
            self.size_hint = (0.9, 0.9)
            self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        else:  # Desktop
            self.size_hint = (0.85, 0.85)
            self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
    
    def on_window_resize(self, window, width, height):
        """Reconfigurar layout quando a janela é redimensionada"""
        self.configure_responsive_size()
        # Recriar layout se necessário
        if hasattr(self, 'content') and self.content:
            self.create_layout()
    
    def get_responsive_font_size(self, base_size=14):
        """Calcular tamanho de fonte responsivo"""
        screen_width = Window.width
        if screen_width < 600:
            return sp(base_size * 0.8)
        elif screen_width < 1024:
            return sp(base_size * 0.9)
        else:
            return sp(base_size)
    
    def get_responsive_height(self, base_height=40):
        """Calcular altura responsiva"""
        screen_height = Window.height
        if screen_height < 600:
            return dp(base_height * 0.8)
        elif screen_height < 800:
            return dp(base_height * 0.9)
        else:
            return dp(base_height)
    
    def create_layout(self):
        """Criar o layout principal do popup"""
        screen_width = Window.width
        
        # Escolher orientação baseada no tamanho da tela
        if screen_width < 800:  # Layout vertical para telas pequenas
            main_layout = BoxLayout(
                orientation='vertical', 
                spacing=dp(10), 
                padding=[dp(10), dp(10)]
            )
            
            # Seção de produtos
            product_section = self.create_product_selection_layout()
            main_layout.add_widget(product_section)
            
            # Seção do carrinho
            cart_section = self.create_cart_layout()
            main_layout.add_widget(cart_section)
            
        else:  # Layout horizontal para telas grandes
            main_layout = BoxLayout(
                orientation='horizontal', 
                spacing=dp(15), 
                padding=[dp(20), dp(20)]
            )
            
            # Lado esquerdo - Seleção de produtos
            left_layout = self.create_product_selection_layout()
            left_layout.size_hint_x = 0.5
            
            # Lado direito - Carrinho e finalização
            right_layout = self.create_cart_layout()
            right_layout.size_hint_x = 0.5
            
            main_layout.add_widget(left_layout)
            main_layout.add_widget(right_layout)
        
        self.content = main_layout
    
    def create_product_selection_layout(self):
        """Criar layout para seleção de produtos"""
        left_layout = BoxLayout(
            orientation='vertical', 
            spacing=dp(8)
        )
        
        # Título da seção
        title_label = Label(
            text="Adicionar Produtos",
            font_size=self.get_responsive_font_size(18),
            bold=True,
            size_hint_y=None,
            height=self.get_responsive_height(40)
        )
        left_layout.add_widget(title_label)
        
        # Layout para pesquisa
        search_layout = BoxLayout(
            size_hint_y=None, 
            height=self.get_responsive_height(50), 
            spacing=dp(10)
        )
        
        search_label = Label(
            text="Pesquisar:", 
            size_hint_x=0.25,
            font_size=self.get_responsive_font_size(12)
        )
        search_layout.add_widget(search_label)
        
        self.search_input = TextInput(
            multiline=False, 
            size_hint_x=0.75,
            hint_text="Digite para pesquisar produtos",
            font_size=self.get_responsive_font_size(12)
        )
        self.search_input.bind(text=self.filter_products)
        search_layout.add_widget(self.search_input)
        
        # Seleção de produto
        product_layout = BoxLayout(
            size_hint_y=None, 
            height=self.get_responsive_height(50), 
            spacing=dp(10)
        )
        
        product_label = Label(
            text="Produto:", 
            size_hint_x=0.25,
            font_size=self.get_responsive_font_size(12)
        )
        product_layout.add_widget(product_label)
        
        product_options = [f"{p[0]} - {p[1]}" for p in self.products]
        self.product_spinner = Spinner(
            text="Selecione um produto" if product_options else "Nenhum produto disponível",
            values=product_options,
            size_hint_x=0.75,
            font_size=self.get_responsive_font_size(12)
        )
        self.product_spinner.bind(text=self.on_product_select)
        product_layout.add_widget(self.product_spinner)
        
        # Informações do produto selecionado
        info_layout = GridLayout(
            cols=2, 
            size_hint_y=None, 
            height=self.get_responsive_height(80), 
            spacing=dp(5)
        )
        
        # Labels de informação
        info_labels = [
            ("Estoque:", "stock_label", ""),
            ("Preço:", "price_label", "0.00 MZN")
        ]
        
        for label_text, attr_name, default_text in info_labels:
            info_layout.add_widget(Label(
                text=label_text, 
                halign='left',
                font_size=self.get_responsive_font_size(12)
            ))
            label = Label(
                text=default_text, 
                halign='left',
                font_size=self.get_responsive_font_size(12)
            )
            setattr(self, attr_name, label)
            info_layout.add_widget(label)
        
        # Quantidade a adicionar
        quantity_layout = BoxLayout(
            size_hint_y=None, 
            height=self.get_responsive_height(50), 
            spacing=dp(10)
        )
        
        quantity_label = Label(
            text="Quantidade:", 
            size_hint_x=0.4,
            font_size=self.get_responsive_font_size(12)
        )
        quantity_layout.add_widget(quantity_label)
        
        self.quantity_input = TextInput(
            hint_text="00", 
            input_filter="int", 
            multiline=False, 
            size_hint_x=0.3,
            font_size=self.get_responsive_font_size(12)
        )
        quantity_layout.add_widget(self.quantity_input)
        
        # Botão adicionar
        add_btn = Button(
            text="Adicionar",
            background_color=(0.1, 0.6, 0.2, 1),
            color=(1, 1, 1, 1),
            size_hint_x=0.3,
            font_size=self.get_responsive_font_size(12)
        )
        add_btn.bind(on_release=self.add_to_cart)
        quantity_layout.add_widget(add_btn)
        
        # Adicionar todos os componentes
        left_layout.add_widget(search_layout)
        left_layout.add_widget(product_layout)
        left_layout.add_widget(info_layout)
        left_layout.add_widget(quantity_layout)
        
        # Espaço flexível apenas em telas grandes
        if Window.width >= 800:
            left_layout.add_widget(BoxLayout())
        
        return left_layout
    
    def create_cart_layout(self):
        """Criar layout do carrinho e finalização"""
        right_layout = BoxLayout(
            orientation='vertical', 
            spacing=dp(8)
        )
        
        # Título do carrinho
        cart_title = Label(
            text="Carrinho de Compras",
            font_size=self.get_responsive_font_size(18),
            bold=True,
            size_hint_y=None,
            height=self.get_responsive_height(40)
        )
        right_layout.add_widget(cart_title)
        
        # ScrollView para lista de itens - altura responsiva
        scroll_height = 0.4 if Window.width >= 800 else 0.3
        scroll = ScrollView(size_hint=(1, scroll_height))
        
        self.cart_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(3),
            size_hint_y=None
        )
        self.cart_layout.bind(minimum_height=self.cart_layout.setter('height'))
        scroll.add_widget(self.cart_layout)
        right_layout.add_widget(scroll)
        
        # Total da venda
        total_layout = BoxLayout(
            size_hint_y=None, 
            height=self.get_responsive_height(50)
        )
        
        total_label = Label(
            text="TOTAL:", 
            font_size=self.get_responsive_font_size(16), 
            bold=True,
            size_hint_x=0.5
        )
        total_layout.add_widget(total_label)
        
        self.total_display = Label(
            text="0.00 MZN", 
            font_size=self.get_responsive_font_size(16), 
            bold=True,
            size_hint_x=0.5
        )
        total_layout.add_widget(self.total_display)
        
        # Seção de pagamento
        payment_section = self.create_payment_section()
        
        # Botões finais
        button_layout = self.create_final_buttons()
        
        right_layout.add_widget(total_layout)
        right_layout.add_widget(payment_section)
        right_layout.add_widget(button_layout)
        
        return right_layout
    
    def create_payment_section(self):
        """Criar seção de pagamento"""
        payment_layout = BoxLayout(
            orientation='vertical', 
            spacing=dp(5), 
            size_hint_y=None, 
            height=self.get_responsive_height(100)
        )
        
        # Valor pago
        payment_row = BoxLayout(
            size_hint_y=None, 
            height=self.get_responsive_height(35)
        )
        
        payment_label = Label(
            text="Valor Pago:", 
            size_hint_x=0.4,
            font_size=self.get_responsive_font_size(12)
        )
        payment_row.add_widget(payment_label)
        
        self.payment_input = TextInput( 
            hint_text="0.00 MZN",
            input_filter="float", 
            multiline=False, 
            size_hint_x=0.6,
            font_size=self.get_responsive_font_size(12)
        )
        self.payment_input.bind(text=self.calculate_change)
        payment_row.add_widget(self.payment_input)
        
        # Troco
        change_row = BoxLayout(
            size_hint_y=None, 
            height=self.get_responsive_height(35)
        )
        
        change_label = Label(
            text="Troco:", 
            size_hint_x=0.4,
            font_size=self.get_responsive_font_size(12)
        )
        change_row.add_widget(change_label)
        
        self.change_label = Label(
            text="0.00 MZN", 
            size_hint_x=0.6, 
            bold=True,
            font_size=self.get_responsive_font_size(12)
        )
        change_row.add_widget(self.change_label)
        
        payment_layout.add_widget(payment_row)
        payment_layout.add_widget(change_row)
        
        return payment_layout
    
    def create_final_buttons(self):
        """Criar botões finais"""
        screen_width = Window.width
        
        # Layout dos botões - empilhar verticalmente em telas pequenas
        if screen_width < 600:
            button_layout = BoxLayout(
                orientation='vertical',
                spacing=dp(5), 
                size_hint_y=None, 
                height=self.get_responsive_height(160)  # 4 botões * 40
            )
        else:
            button_layout = BoxLayout(
                spacing=dp(8), 
                size_hint_y=None, 
                height=self.get_responsive_height(50)
            )
        
        # Definir botões
        buttons = [
            ("Finalizar Venda", (0.1, 0.6, 0.2, 1), self.confirm_sale),
            ("Imprimir", (0.2, 0.4, 0.8, 1), self.print_receipt),
            ("Limpar", (0.8, 0.5, 0.1, 1), self.clear_cart),
            ("Cancelar", (0.7, 0.7, 0.7, 1), self.dismiss)
        ]
        
        for text, color, callback in buttons:
            btn = Button(
                text=text,
                background_color=color,
                color=(1, 1, 1, 1),
                font_size=self.get_responsive_font_size(12)
            )
            btn.bind(on_release=callback)
            button_layout.add_widget(btn)
        
        return button_layout
    
    def filter_products(self, instance, text):
        """Filtrar produtos baseado no texto de pesquisa"""
        if not text:
            self.product_spinner.values = [f"{p[0]} - {p[1]}" for p in self.products]
            return
        
        filtered_products = [
            f"{p[0]} - {p[1]}" for p in self.products 
            if text.lower() in p[1].lower() or text.lower() in str(p[0]).lower()
        ]
        
        self.product_spinner.values = filtered_products
        if filtered_products:
            self.product_spinner.text = filtered_products[0]
            self.on_product_select(self.product_spinner, filtered_products[0])
    
    def on_product_select(self, spinner, text):
        """Atualizar informações quando um produto é selecionado"""
        if text in self.product_dict:
            self.selected_product = self.product_dict[text]
            self.stock_label.text = str(self.selected_product[2])
            self.price_label.text = f"{self.selected_product[3]:.2f} MZN"
    
    def add_to_cart(self, instance):
        """Adicionar produto ao carrinho"""
        if not hasattr(self, 'selected_product') or not self.selected_product:
            self.manager_screen.show_popup("Erro", "Por favor, selecione um produto.")
            return
        
        try:
            quantity = int(self.quantity_input.text) if self.quantity_input.text else 0
            
            if quantity <= 0:
                self.manager_screen.show_popup("Erro", "A quantidade deve ser maior que zero.")
                return
            
            if quantity > self.selected_product[2]:
                self.manager_screen.show_popup("Erro", "Quantidade maior que o estoque disponível.")
                return
            
            # Verificar se o produto já está no carrinho
            existing_item = None
            for item in self.sale_items:
                if item['product_id'] == self.selected_product[0]:
                    existing_item = item
                    break
            
            if existing_item:
                # Verificar se a nova quantidade total não excede o estoque
                new_total_qty = existing_item['quantity'] + quantity
                if new_total_qty > self.selected_product[2]:
                    self.manager_screen.show_popup("Erro", 
                        f"Quantidade total ({new_total_qty}) excede o estoque disponível ({self.selected_product[2]}).")
                    return
                
                # Atualizar quantidade do item existente
                existing_item['quantity'] = new_total_qty
                existing_item['total'] = existing_item['quantity'] * existing_item['price']
            else:
                # Adicionar novo item
                item = {
                    'product_id': self.selected_product[0],
                    'name': self.selected_product[1],
                    'quantity': quantity,
                    'price': self.selected_product[3],
                    'total': quantity * self.selected_product[3]
                }
                self.sale_items.append(item)
            
            self.update_cart_display()
            self.quantity_input.text = "1"  # Reset quantidade
            
        except ValueError:
            self.manager_screen.show_popup("Erro", "Por favor, insira uma quantidade válida.")
    
    def update_cart_display(self):
        """Atualizar display do carrinho"""
        self.cart_layout.clear_widgets()
        self.sale_total = 0.0
        
        for i, item in enumerate(self.sale_items):
            item_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=self.get_responsive_height(35),
                spacing=dp(3)
            )
            
            # Ajustar tamanho do nome baseado no tamanho da tela
            name_max_chars = 15 if Window.width < 600 else 25
            
            # Nome do produto
            name_label = Label(
                text=item['name'][:name_max_chars] + "..." if len(item['name']) > name_max_chars else item['name'],
                size_hint_x=0.4,
                text_size=(None, None),
                halign='left',
                font_size=self.get_responsive_font_size(10)
            )
            
            # Quantidade e preço
            qty_price_label = Label(
                text=f"{item['quantity']} x {item['price']:.2f}",
                size_hint_x=0.3,
                font_size=self.get_responsive_font_size(10)
            )
            
            # Total do item
            total_label = Label(
                text=f"{item['total']:.2f}",
                size_hint_x=0.2,
                font_size=self.get_responsive_font_size(10)
            )
            
            # Botão remover
            remove_btn = Button(
                text="X",
                size_hint_x=0.1,
                background_color=(0.8, 0.2, 0.2, 1),
                color=(1, 1, 1, 1),
                font_size=self.get_responsive_font_size(10)
            )
            remove_btn.bind(on_release=lambda x, idx=i: self.remove_from_cart(idx))
            
            item_layout.add_widget(name_label)
            item_layout.add_widget(qty_price_label)
            item_layout.add_widget(total_label)
            item_layout.add_widget(remove_btn)
            
            self.cart_layout.add_widget(item_layout)
            self.sale_total += item['total']
        
        self.total_display.text = f"{self.sale_total:.2f} MZN"
        self.calculate_change()
    
    def remove_from_cart(self, index):
        """Remover item do carrinho"""
        if 0 <= index < len(self.sale_items):
            self.sale_items.pop(index)
            self.update_cart_display()
    
    def clear_cart(self, instance):
        """Limpar todo o carrinho"""
        self.sale_items.clear()
        self.update_cart_display()
    
    def calculate_change(self, *args):
        """Calcular o troco"""
        try:
            payment = float(self.payment_input.text) if self.payment_input.text else 0
            change = payment - self.sale_total
            if change >= 0:
                self.change_label.text = f"{change:.2f} MZN"
            else:
                self.change_label.text = "Pagamento insuficiente"
        except ValueError:
            self.change_label.text = "0.00 MZN"
    
    def confirm_sale(self, instance):
        """Confirmar e registrar a venda"""
        if not self.sale_items:
            self.manager_screen.show_popup("Erro", "Carrinho vazio. Adicione produtos à venda.")
            return
        
        # Verificar pagamento
        try:
            payment = float(self.payment_input.text) if self.payment_input.text else 0
            if payment < self.sale_total:
                self.manager_screen.show_popup("Erro", "Pagamento insuficiente para concluir a venda.")
                return
        except ValueError:
            self.manager_screen.show_popup("Erro", "Por favor, insira um valor de pagamento válido.")
            return
        
        # Registrar cada item da venda
        db = Database()
        sale_success = True
        
        try:
            # Aqui você pode criar uma venda principal e depois os itens
            # Assumindo que você tem um método para vendas com múltiplos itens
            for item in self.sale_items:
                sale_id = db.add_sale(item['product_id'], item['quantity'], item['price'])
                if not sale_id:
                    sale_success = False
                    break
                elif not self.sale_id:  # Usar o primeiro ID como referência
                    self.sale_id = sale_id
            
            if sale_success:
                self.manager_screen.load_sales()
                self.manager_screen.show_popup("Sucesso", "Venda registrada com sucesso!")
                # Manter popup aberto para permitir impressão
            else:
                self.manager_screen.show_popup("Erro", "Erro ao registrar alguns itens da venda!")
                
        except Exception as e:
            self.manager_screen.show_popup("Erro", f"Erro ao processar venda: {str(e)}")
    
    def print_receipt(self, instance):
        """Gerar e imprimir fatura"""
        if not self.sale_items:
            self.manager_screen.show_popup("Erro", "Nenhuma venda para imprimir.")
            return
        
        # Criar popup da fatura com tamanho responsivo
        receipt_popup = Popup(
            title="Fatura",
            size_hint=(0.8, 0.9) if Window.width < 800 else (0.5, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            auto_dismiss=True
        )
        
        receipt_layout = BoxLayout(
            orientation='vertical', 
            padding=dp(10), 
            spacing=dp(5)
        )
        
        # Cabeçalho
        receipt_layout.add_widget(Label(
            text="FATURA DE VENDA",
            font_size=self.get_responsive_font_size(18),
            bold=True,
            size_hint_y=None,
            height=self.get_responsive_height(30)
        ))
        
        receipt_layout.add_widget(Label(
            text=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            size_hint_y=None,
            height=self.get_responsive_height(20),
            font_size=self.get_responsive_font_size(12)
        ))
        
        if self.sale_id:
            receipt_layout.add_widget(Label(
                text=f"Venda Nº: {self.sale_id}",
                size_hint_y=None,
                height=self.get_responsive_height(20),
                font_size=self.get_responsive_font_size(12)
            ))
        
        # Linha separadora
        receipt_layout.add_widget(Label(
            text="=" * 40,
            size_hint_y=None,
            height=self.get_responsive_height(20),
            font_size=self.get_responsive_font_size(12)
        ))
        
        # ScrollView para itens da venda
        items_scroll = ScrollView(size_hint=(1, 0.5))
        items_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(2),
            size_hint_y=None
        )
        items_layout.bind(minimum_height=items_layout.setter('height'))
        
        # Itens da venda
        for item in self.sale_items:
            items_layout.add_widget(Label(
                text=f"{item['name']}",
                size_hint_y=None,
                height=self.get_responsive_height(20),
                text_size=(300, None),
                halign='left',
                font_size=self.get_responsive_font_size(11)
            ))
            items_layout.add_widget(Label(
                text=f"{item['quantity']} x {item['price']:.2f} = {item['total']:.2f} MZN",
                size_hint_y=None,
                height=self.get_responsive_height(20),
                font_size=self.get_responsive_font_size(11)
            ))
        
        items_scroll.add_widget(items_layout)
        receipt_layout.add_widget(items_scroll)
        
        # Linha separadora
        receipt_layout.add_widget(Label(
            text="=" * 40,
            size_hint_y=None,
            height=self.get_responsive_height(20),
            font_size=self.get_responsive_font_size(12)
        ))
        
        # Totais
        payment = float(self.payment_input.text) if self.payment_input.text else 0
        change = payment - self.sale_total
        
        totals_info = [
            (f"TOTAL: {self.sale_total:.2f} MZN", True, 25),
            (f"Valor Pago: {payment:.2f} MZN", False, 20),
            (f"Troco: {change:.2f} MZN", True, 20),
            ("Obrigado pela preferência!", False, 30)
        ]
        
        for text, is_bold, height in totals_info:
            receipt_layout.add_widget(Label(
                text=text,
                size_hint_y=None,
                height=self.get_responsive_height(height),
                bold=is_bold,
                font_size=self.get_responsive_font_size(12)
            ))
        
        # Botões
        btn_layout = BoxLayout(
            size_hint_y=None, 
            height=self.get_responsive_height(40), 
            spacing=dp(10)
        )
        
        print_btn = Button(
            text="Imprimir", 
            size_hint_x=0.5,
            font_size=self.get_responsive_font_size(12)
        )
        print_btn.bind(on_release=lambda x: self.manager_screen.show_popup(
            "Impressão", "Enviando para impressora...", timeout=2
        ))
        
        close_btn = Button(
            text="Fechar", 
            size_hint_x=0.5,
            font_size=self.get_responsive_font_size(12)
        )
        close_btn.bind(on_release=receipt_popup.dismiss)
        
        btn_layout.add_widget(print_btn)
        btn_layout.add_widget(close_btn)
        
        receipt_layout.add_widget(btn_layout)
        receipt_popup.content = receipt_layout
        receipt_popup.open()            
   


from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from datetime import datetime, timedelta

class ManagerScreen(Screen):
    sales_table = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(ManagerScreen, self).__init__(**kwargs)
        self.db = Database()
        self.current_filter_date = None
        
    def on_enter(self):
        # Sempre carregar vendas de hoje ao entrar na tela
        today_str = datetime.now().strftime("%d/%m/%Y")
        self.current_filter_date = today_str
        self.load_sales(today_str)
        
    def load_sales(self, filter_date=None):
        """Carregar vendas na tabela com filtro opcional por data e agrupamento por produto"""
        self.sales_table.clear_widgets()
        
        # Atualizar filtro atual
        if filter_date:
            self.current_filter_date = filter_date
        
        # Configurar o GridLayout como uma tabela fixa
        self.sales_table.cols = 5
        self.sales_table.rows = 1  # Inicialmente apenas cabeçalho
        self.sales_table.size_hint_y = None
        self.sales_table.spacing = 2
        self.sales_table.padding = 10
        
        # Adicionar cabeçalhos
        self.add_table_headers()
        
        # Buscar vendas do banco de dados
        if self.current_filter_date:
            sales = self.db.get_sales_by_date(self.current_filter_date)
        else:
            sales = self.db.get_all_sales()
        
        # Verificar se há vendas
        if not sales:
            self.add_no_sales_row()
            return
        
        # Agrupar vendas por produto
        grouped_sales = self.group_sales_by_product(sales)
        
        # Adicionar vendas agrupadas à tabela
        for i, (product_name, data) in enumerate(grouped_sales.items()):
            self.add_sales_row(product_name, data, i % 2 == 0)
        
        # Ajustar altura da tabela
        self.adjust_table_height()
    
    def add_table_headers(self):
        """Adicionar cabeçalhos da tabela"""
        headers = ["Produto", "Qtd. Total", "Preço Unit.", "Total", "Última Venda"]
        header_colors = (0.2, 0.4, 0.6, 1)  # Azul escuro
        
        for header in headers:
            header_label = Label(
                text=header,
                size_hint_y=None,
                height=50,
                bold=True,
                color=(1, 1, 1, 1),
                text_size=(None, None),
                halign='center',
                valign='middle'
            )
            
            # Adicionar fundo colorido
            with header_label.canvas.before:
                Color(*header_colors)
                Rectangle(pos=header_label.pos, size=header_label.size)
            
            header_label.bind(pos=lambda instance, value, color=header_colors: 
                            self.update_cell_bg(instance, value, color))
            header_label.bind(size=lambda instance, value, color=header_colors: 
                            self.update_cell_bg(instance, value, color))
            
            self.sales_table.add_widget(header_label)
        
        # Incrementar número de linhas
        self.sales_table.rows += 1
    
    def add_no_sales_row(self):
        """Adicionar linha quando não há vendas"""
        no_sales_label = Label(
            text="Nenhuma venda encontrada",
            size_hint_y=None,
            height=50,
            italic=True,
            color=(0.7, 0.7, 0.7, 1),
            text_size=(None, None),
            halign='center',
            valign='middle'
        )
        
        # Adicionar célula que ocupa toda a largura
        self.sales_table.add_widget(no_sales_label)
        
        # Adicionar células vazias para completar a linha
        for _ in range(4):
            empty_cell = Label(
                text="",
                size_hint_y=None,
                height=50
            )
            self.sales_table.add_widget(empty_cell)
        
        self.sales_table.rows += 1
        self.adjust_table_height()
    
    def add_sales_row(self, product_name, data, is_alternate_row=False):
        """Adicionar uma linha de venda com formatação consistente"""
        # Cor de fundo alternada
        bg_color = (0.15, 0.15, 0.15, 1) if is_alternate_row else (0.1, 0.1, 0.1, 1)
        
        # Dados da linha
        row_data = [
            product_name,
            str(data['total_quantity']),
            f"{data['unit_price']:.2f} MZN",
            f"{data['total_amount']:.2f} MZN",
            self.format_date(data['last_sale_date'])
        ]
        
        # Alinhamentos por coluna
        alignments = ['left', 'center', 'right', 'right', 'center']
        
        for i, (text, align) in enumerate(zip(row_data, alignments)):
            cell_label = Label(
                text=text,
                size_hint_y=None,
                height=50,
                color=(1, 1, 1, 1),
                text_size=(None, None),
                halign=align,
                valign='middle'
            )
            
            # Adicionar fundo colorido
            with cell_label.canvas.before:
                Color(*bg_color)
                Rectangle(pos=cell_label.pos, size=cell_label.size)
            
            cell_label.bind(pos=lambda instance, value, color=bg_color: 
                          self.update_cell_bg(instance, value, color))
            cell_label.bind(size=lambda instance, value, color=bg_color: 
                          self.update_cell_bg(instance, value, color))
            
            self.sales_table.add_widget(cell_label)
        
        # Incrementar número de linhas
        self.sales_table.rows += 1
    
    def update_cell_bg(self, instance, value, color):
        """Atualizar fundo da célula quando posição/tamanho mudar"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*color)
            Rectangle(pos=instance.pos, size=instance.size)
    
    def adjust_table_height(self):
        """Ajustar altura da tabela baseada no número de linhas"""
        self.sales_table.height = self.sales_table.rows * 52  # 50 altura + 2 spacing
    
    def format_date(self, date_str):
        """Formatar data para exibição mais limpa"""
        try:
            # Se a data contém hora, extrair apenas a data
            if ' ' in date_str:
                date_part = date_str.split(' ')[0]
                time_part = date_str.split(' ')[1]
                return f"{date_part} {time_part[:5]}"  # Mostrar apenas HH:MM
            return date_str
        except:
            return date_str
    
    def group_sales_by_product(self, sales):
        """Agrupar vendas por produto, somando quantidades e totais"""
        grouped = {}
        
        for sale in sales:
            product_name = sale[1]  # Nome do produto
            quantity = sale[2]      # Quantidade
            unit_price = sale[3]    # Preço unitário
            total = sale[4]         # Total
            sale_date = sale[5]     # Data da venda
            
            if product_name not in grouped:
                grouped[product_name] = {
                    'total_quantity': 0,
                    'total_amount': 0,
                    'unit_price': unit_price,
                    'last_sale_date': sale_date
                }
            
            # Somar quantidade e total
            grouped[product_name]['total_quantity'] += quantity
            grouped[product_name]['total_amount'] += total
            
            # Manter o preço unitário e data mais recentes
            if sale_date > grouped[product_name]['last_sale_date']:
                grouped[product_name]['unit_price'] = unit_price
                grouped[product_name]['last_sale_date'] = sale_date
        
        # Ordenar por nome do produto
        return dict(sorted(grouped.items()))
    
    def show_date_filter(self):
        """Mostrar popup melhorado para filtrar por data"""
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        # Título com melhor estilo
        title_label = Label(
            text="Filtrar Vendas por Data",
            size_hint_y=None,
            height=50,
            font_size=20,
            bold=True,
            color=(0.2, 0.4, 0.6, 1)
        )
        content.add_widget(title_label)
        
        # Informação atual
        current_info = Label(
            text=f"Filtro atual: {self.current_filter_date or 'Todas as datas'}",
            size_hint_y=None,
            height=35,
            font_size=14,
            color=(0.6, 0.6, 0.6, 1)
        )
        content.add_widget(current_info)
        
        # Campo de data com melhor layout
        date_container = BoxLayout(orientation='vertical', size_hint_y=None, height=80, spacing=5)
        
        date_label = Label(
            text="Selecione a data:",
            size_hint_y=None,
            height=30,
            font_size=14,
            color=(0.8, 0.8, 0.8, 1),
            halign='left'
        )
        date_label.text_size = (date_label.width, None)
        date_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None)))
        
        date_input = TextInput(
            text=self.current_filter_date or datetime.now().strftime("%d/%m/%Y"),
            multiline=False,
            size_hint_y=None,
            height=45,
            font_size=16,
            hint_text="DD/MM/AAAA",
            background_color=(0.9, 0.9, 0.9, 1),
            foreground_color=(0.1, 0.1, 0.1, 1)
        )
        
        date_container.add_widget(date_label)
        date_container.add_widget(date_input)
        content.add_widget(date_container)
        
        # Botões organizados em grid
        button_container = BoxLayout(orientation='vertical', size_hint_y=None, height=130, spacing=10)
        
        # Primeira linha de botões
        button_row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        filter_btn = Button(
            text="Aplicar Filtro",
            background_color=(0.2, 0.7, 0.2, 1),
            font_size=14,
            bold=True
        )
        
        today_btn = Button(
            text="Hoje",
            background_color=(0.2, 0.5, 0.8, 1),
            font_size=14
        )
        
        button_row1.add_widget(filter_btn)
        button_row1.add_widget(today_btn)
        
        # Segunda linha de botões
        button_row2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        yesterday_btn = Button(
            text="Ontem",
            background_color=(0.8, 0.6, 0.2, 1),
            font_size=14
        )
        
        all_btn = Button(
            text="Todas as Vendas",
            background_color=(0.8, 0.4, 0.2, 1),
            font_size=14
        )
        
        button_row2.add_widget(yesterday_btn)
        button_row2.add_widget(all_btn)
        
        # Botão fechar
        close_btn = Button(
            text="Fechar",
            size_hint_y=None,
            height=40,
            background_color=(0.6, 0.3, 0.3, 1),
            font_size=14
        )
        
        button_container.add_widget(button_row1)
        button_container.add_widget(button_row2)
        button_container.add_widget(close_btn)
        content.add_widget(button_container)
        
        # Criar popup
        popup = Popup(
            title="",
            content=content,
            size_hint=(0.85, 0.7),
            auto_dismiss=False,
            background_color=(0.1, 0.1, 0.1, 0.9)
        )
        
        # Funções dos botões
        def apply_filter(instance):
            date_str = date_input.text.strip()
            if self.validate_date(date_str):
                self.current_filter_date = date_str
                self.load_sales(date_str)
                popup.dismiss()
                self.show_popup("Sucesso", f"Filtro aplicado para {date_str}", timeout=2)
            else:
                self.show_popup("Erro", "Formato de data inválido. Use DD/MM/AAAA")
        
        def filter_today(instance):
            today_str = datetime.now().strftime("%d/%m/%Y")
            self.current_filter_date = today_str
            self.load_sales(today_str)
            popup.dismiss()
            self.show_popup("Sucesso", "Mostrando vendas de hoje", timeout=2)
        
        def filter_yesterday(instance):
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_str = yesterday.strftime("%d/%m/%Y")
            self.current_filter_date = yesterday_str
            self.load_sales(yesterday_str)
            popup.dismiss()
            self.show_popup("Sucesso", "Mostrando vendas de ontem", timeout=2)
        
        def show_all(instance):
            self.current_filter_date = None
            self.load_sales()
            popup.dismiss()
            self.show_popup("Sucesso", "Mostrando todas as vendas", timeout=2)
        
        def close_popup(instance):
            popup.dismiss()
        
        # Bind dos botões
        filter_btn.bind(on_press=apply_filter)
        today_btn.bind(on_press=filter_today)
        yesterday_btn.bind(on_press=filter_yesterday)
        all_btn.bind(on_press=show_all)
        close_btn.bind(on_press=close_popup)
        
        popup.open()
    
    def validate_date(self, date_str):
        """Validar formato de data"""
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False
    
    def new_sale(self):
        """Abrir formulário para registrar uma nova venda"""
        sale_form = SaleForm(self)
        if sale_form.products:
            sale_form.open()
        else:
            self.show_popup("Erro", "Não há produtos disponíveis para venda.")
    
    def refresh_sales(self):
        """Atualizar a lista de vendas mantendo o filtro atual"""
        if self.current_filter_date:
            self.load_sales(self.current_filter_date)
        else:
            self.load_sales()
        self.show_popup("Sucesso", "Lista atualizada!", timeout=2)
    
    def show_popup(self, title, message, timeout=None):
        """Exibir uma mensagem popup com timeout opcional"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        message_label = Label(
            text=message,
            text_size=(None, None),
            halign='center',
            valign='middle',
            font_size=16,
            color=(0.9, 0.9, 0.9, 1)
        )
        
        if not timeout:
            ok_btn = Button(
                text="OK",
                size_hint_y=None,
                height=40,
                background_color=(0.2, 0.5, 0.8, 1)
            )
            content.add_widget(message_label)
            content.add_widget(ok_btn)
        else:
            content.add_widget(message_label)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.4),
            background_color=(0.1, 0.1, 0.1, 0.9)
        )
        
        if not timeout:
            ok_btn.bind(on_press=popup.dismiss)
        
        popup.open()
        
        if timeout:
            Clock.schedule_once(lambda dt: popup.dismiss(), timeout)

    def export_sales_data(self):
        """Exportar dados de vendas para CSV"""
        try:
            import csv
            from datetime import datetime
            
            # Obter vendas com base no filtro atual
            if self.current_filter_date:
                sales = self.db.get_sales_by_date(self.current_filter_date)
                filename = f"vendas_{self.current_filter_date.replace('/', '_')}.csv"
            else:
                sales = self.db.get_all_sales()
                filename = f"vendas_completas_{datetime.now().strftime('%d_%m_%Y')}.csv"
            
            if not sales:
                self.show_popup("Aviso", "Não há vendas para exportar.")
                return
            
            # Agrupar vendas por produto
            grouped_sales = self.group_sales_by_product(sales)
            
            # Escrever arquivo CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Produto', 'Quantidade_Total', 'Preco_Unitario', 'Total_Vendas', 'Ultima_Venda']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for product_name, data in grouped_sales.items():
                    writer.writerow({
                        'Produto': product_name,
                        'Quantidade_Total': data['total_quantity'],
                        'Preco_Unitario': data['unit_price'],
                        'Total_Vendas': data['total_amount'],
                        'Ultima_Venda': data['last_sale_date']
                    })
            
            self.show_popup("Sucesso", f"Dados exportados para {filename}", timeout=3)
            
        except Exception as e:
            self.show_popup("Erro", f"Erro ao exportar dados: {str(e)}")

    def show_sales_summary(self):
        """Mostrar resumo das vendas"""
        if self.current_filter_date:
            sales = self.db.get_sales_by_date(self.current_filter_date)
            period_text = f"de {self.current_filter_date}"
        else:
            sales = self.db.get_all_sales()
            period_text = "totais"
        
        if not sales:
            self.show_popup("Aviso", "Não há vendas para resumir.")
            return
        
        # Calcular estatísticas
        total_sales = len(sales)
        total_revenue = sum(sale[4] for sale in sales)  # Total de cada venda
        total_quantity = sum(sale[2] for sale in sales)  # Quantidade total
        
        # Produto mais vendido
        product_quantities = {}
        for sale in sales:
            product_name = sale[1]
            quantity = sale[2]
            if product_name in product_quantities:
                product_quantities[product_name] += quantity
            else:
                product_quantities[product_name] = quantity
        
        most_sold_product = max(product_quantities, key=product_quantities.get) if product_quantities else "N/A"
        most_sold_qty = product_quantities.get(most_sold_product, 0)
        
        summary_text = f"""Resumo das vendas {period_text}:

• Total de vendas: {total_sales}
• Receita total: {total_revenue:.2f} MZN
• Quantidade total vendida: {total_quantity}
• Produto mais vendido: {most_sold_product} ({most_sold_qty} unidades)
• Receita média por venda: {total_revenue/total_sales:.2f} MZN"""
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        summary_label = Label(
            text=summary_text,
            text_size=(None, None),
            halign='left',
            valign='top',
            font_size=14,
            color=(0.9, 0.9, 0.9, 1)
        )
        summary_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None)))
        
        close_btn = Button(
            text="Fechar",
            size_hint_y=None,
            height=40,
            background_color=(0.2, 0.5, 0.8, 1)
        )
        
        content.add_widget(summary_label)
        content.add_widget(close_btn)
        
        popup = Popup(
            title="Resumo de Vendas",
            content=content,
            size_hint=(0.8, 0.7),
            background_color=(0.1, 0.1, 0.1, 0.9)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()