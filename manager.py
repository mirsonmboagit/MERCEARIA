from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.clock import Clock
from database import Database
from datetime import datetime
import cv2
from pyzbar.pyzbar import decode
import numpy as np


class ModernSalesScreen(Screen):
    def __init__(self, **kwargs):
        super(ModernSalesScreen, self).__init__(**kwargs)
        self.db = Database()
        self.cart_items = []
        self.total_amount = 0.0
        self.products_dict = {}
        self.scanning = False
        self.camera_active = False
        self.current_camera = 0
        
        self.create_ui()
        Clock.schedule_once(lambda dt: self.load_products(), 0.1)
        Clock.schedule_once(lambda dt: self.test_barcode_database(), 0.2)
    
    def test_barcode_database(self):
        """Teste: verificar produtos com código de barras no banco"""
        try:
            print("\n" + "="*70)
            print("🧪 TESTE - Produtos com Código de Barras")
            print("="*70)
            
            self.db.cursor.execute("""
                SELECT id, description, barcode, existing_stock
                FROM products
                WHERE barcode IS NOT NULL AND barcode != ''
                ORDER BY id
            """)
            
            produtos = self.db.cursor.fetchall()
            
            if produtos:
                print(f"✅ {len(produtos)} produto(s) com código de barras:\n")
                for p in produtos:
                    print(f"   ID: {p[0]:4d} | Barcode: '{p[2]:15s}' | {p[1]:30s} | Estoque: {p[3]}")
            else:
                print("⚠️ NENHUM produto possui código de barras!")
                print("   Cadastre produtos com códigos de barras antes de usar o scanner.")
            
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            import traceback
            traceback.print_exc()
    
    def create_ui(self):
        """Criar interface moderna"""
        main_layout = BoxLayout(orientation='vertical', padding=0, spacing=0)
        
        # Background
        with main_layout.canvas.before:
            Color(0.94, 0.94, 0.94, 1)
            self.bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self._update_bg, size=self._update_bg)
        
        # Header
        header = self.create_header()
        main_layout.add_widget(header)
        
        # Main Content (3 colunas)
        content = BoxLayout(orientation='horizontal', padding=[15, 10], spacing=12)
        
        # Coluna 1: Pesquisa e Produtos (36%)
        left_col = self.create_products_column()
        left_col.size_hint_x = 0.36
        
        # Coluna 2: Carrinho (42%)
        middle_col = self.create_cart_column()
        middle_col.size_hint_x = 0.42
        
        # Coluna 3: Scanner e Pagamento (22%)
        right_col = self.create_right_column()
        right_col.size_hint_x = 0.22
        
        content.add_widget(left_col)
        content.add_widget(middle_col)
        content.add_widget(right_col)
        
        main_layout.add_widget(content)
        self.add_widget(main_layout)
    
    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
    
    def create_header(self):
        """Criar cabeçalho moderno"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.09,
            padding=[18, 6],
            spacing=20
        )
        
        with header.canvas.before:
            Color(0.22, 0.32, 0.52, 1)
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self._update_header, size=self._update_header)
        
        # Título
        title = Label(
            text='💰 SISTEMA DE VENDAS',
            font_size='24sp',
            bold=True,
            color=[1, 1, 1, 1],
            size_hint_x=0.5,
            halign='left',
            valign='middle'
        )
        title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        
        # Info do usuário
        info_box = BoxLayout(orientation='vertical', size_hint_x=0.3)
        info_box.add_widget(Label(
            text=f'📅 {datetime.now().strftime("%d/%m/%Y")}',
            color=[1, 1, 1, 1],
            font_size='12sp'
        ))
        info_box.add_widget(Label(
            text=f'🕐 {datetime.now().strftime("%H:%M")}',
            color=[1, 1, 1, 1],
            font_size='12sp'
        ))
        
        # Botão Voltar
        btn_voltar = Button(
            text='← VOLTAR',
            size_hint_x=0.2,
            background_color=[0.85, 0.22, 0.22, 1],
            background_normal='',
            bold=True,
            font_size='14sp'
        )
        btn_voltar.bind(on_release=self.go_back)
        
        header.add_widget(title)
        header.add_widget(info_box)
        header.add_widget(btn_voltar)
        
        return header
    
    def _update_header(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
    
    def create_products_column(self):
        """Coluna de produtos redesenhada"""
        col = BoxLayout(orientation='vertical', spacing=8)
        
        # Card de pesquisa ÚNICO com busca por nome/ID/código
        search_card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(105),
            padding=10,
            spacing=6
        )
        with search_card.canvas.before:
            Color(1, 1, 1, 1)
            self.search_card_rect = RoundedRectangle(
                pos=search_card.pos,
                size=search_card.size,
                radius=[10]
            )
        search_card.bind(pos=self._update_search_card, size=self._update_search_card)
        
        search_title = Label(
            text='🔍 PESQUISAR',
            size_hint_y=None,
            height=24,
            bold=True,
            font_size='14sp',
            color=[0.2, 0.2, 0.2, 1]
        )
        
        # Input único que aceita nome, ID ou código de barras
        self.search_input = TextInput(
            hint_text='Nome, ID ou Código de Barras...',
            multiline=False,
            size_hint_y=None,
            height=40,
            font_size='14sp',
            padding=[10, 10],
            background_color=[0.97, 0.97, 0.97, 1],
            foreground_color=[0.2, 0.2, 0.2, 1]
        )
        self.search_input.bind(text=self.on_search)
        self.search_input.bind(on_text_validate=self.on_search_enter)
        
        search_card.add_widget(search_title)
        search_card.add_widget(self.search_input)
        
        # Card de produtos
        products_card = BoxLayout(orientation='vertical', spacing=6, padding=10)
        with products_card.canvas.before:
            Color(1, 1, 1, 1)
            self.products_card_rect = RoundedRectangle(
                pos=products_card.pos,
                size=products_card.size,
                radius=[10]
            )
        products_card.bind(pos=self._update_products_card, size=self._update_products_card)
        
        # Header
        products_header = BoxLayout(size_hint_y=None, height=28, spacing=6)
        products_title = Label(
            text='📦 PRODUTOS',
            bold=True,
            font_size='14sp',
            color=[0.2, 0.2, 0.2, 1],
            halign='left',
            size_hint_x=0.65
        )
        products_title.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        
        self.products_count_label = Label(
            text='0 itens',
            font_size='11sp',
            color=[0.5, 0.5, 0.5, 1],
            size_hint_x=0.35,
            halign='right'
        )
        self.products_count_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        
        products_header.add_widget(products_title)
        products_header.add_widget(self.products_count_label)
        
        # Scroll de produtos
        scroll = ScrollView()
        self.products_list = BoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None,
            padding=[3, 3]
        )
        self.products_list.bind(minimum_height=self.products_list.setter('height'))
        scroll.add_widget(self.products_list)
        
        products_card.add_widget(products_header)
        products_card.add_widget(scroll)
        
        col.add_widget(search_card)
        col.add_widget(products_card)
        
        return col
    
    def _update_search_card(self, instance, value):
        self.search_card_rect.pos = instance.pos
        self.search_card_rect.size = instance.size
    
    def _update_products_card(self, instance, value):
        self.products_card_rect.pos = instance.pos
        self.products_card_rect.size = instance.size
    
    def create_cart_column(self):
        """Coluna do carrinho"""
        col = BoxLayout(orientation='vertical', spacing=6, padding=10)
        
        with col.canvas.before:
            Color(1, 1, 1, 1)
            self.cart_col_rect = RoundedRectangle(
                pos=col.pos,
                size=col.size,
                radius=[10]
            )
        col.bind(pos=self._update_cart_col, size=self._update_cart_col)
        
        # Header
        cart_header = BoxLayout(size_hint_y=None, height=40, spacing=8, padding=[0, 3])
        
        header_left = BoxLayout(orientation='vertical', size_hint_x=0.72)
        header_left.add_widget(Label(
            text='🛒 CARRINHO',
            bold=True,
            font_size='16sp',
            color=[0.2, 0.2, 0.2, 1],
            halign='left',
            size_hint_y=0.6
        ))
        self.cart_count_label = Label(
            text='0 itens',
            font_size='10sp',
            color=[0.5, 0.5, 0.5, 1],
            halign='left',
            size_hint_y=0.4
        )
        self.cart_count_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        header_left.add_widget(self.cart_count_label)
        
        clear_btn = Button(
            text='🗑️',
            size_hint_x=0.28,
            background_color=[0.88, 0.28, 0.28, 1],
            background_normal='',
            bold=True,
            font_size='17sp'
        )
        clear_btn.bind(on_release=self.clear_cart)
        
        cart_header.add_widget(header_left)
        cart_header.add_widget(clear_btn)
        
        # Tabela header
        table_header = GridLayout(
            cols=5,
            size_hint_y=None,
            height=32,
            spacing=1,
            padding=[1, 1]
        )
        
        headers = [
            ('ID', 0.11),
            ('Produto', 0.39),
            ('Quantidade', 0.17),
            ('Total', 0.23),
            ('Del', 0.10)
        ]
        
        for h, width in headers:
            lbl = Label(
                text=h,
                bold=True,
                color=[1, 1, 1, 1],
                font_size='12sp',
                size_hint_x=width
            )
            with lbl.canvas.before:
                Color(0.26, 0.36, 0.56, 1)
                lbl_rect = RoundedRectangle(pos=lbl.pos, size=lbl.size, radius=[4])
            lbl.bind(size=lambda s, v, r=lbl_rect: setattr(r, 'size', s.size))
            lbl.bind(pos=lambda s, v, r=lbl_rect: setattr(r, 'pos', s.pos))
            table_header.add_widget(lbl)
        
        # Scroll
        scroll = ScrollView()
        self.cart_list = GridLayout(
            cols=5,
            spacing=1,
            size_hint_y=None,
            padding=[1, 1]
        )
        self.cart_list.bind(minimum_height=self.cart_list.setter('height'))
        scroll.add_widget(self.cart_list)
        
        # Total
        total_box = BoxLayout(
            size_hint_y=None,
            height=65,
            padding=[6, 8],
            spacing=12
        )
        with total_box.canvas.before:
            Color(0.16, 0.66, 0.26, 1)
            self.total_box_rect = RoundedRectangle(
                pos=total_box.pos,
                size=total_box.size,
                radius=[8]
            )
        total_box.bind(pos=self._update_total_box, size=self._update_total_box)
        
        total_box.add_widget(Label(
            text='TOTAL:',
            bold=True,
            font_size='19sp',
            color=[1, 1, 1, 1]
        ))
        self.total_label = Label(
            text='0.00 MZN',
            bold=True,
            font_size='24sp',
            color=[1, 1, 1, 1]
        )
        total_box.add_widget(self.total_label)
        
        col.add_widget(cart_header)
        col.add_widget(table_header)
        col.add_widget(scroll)
        col.add_widget(total_box)
        
        return col
    
    def _update_cart_col(self, instance, value):
        self.cart_col_rect.pos = instance.pos
        self.cart_col_rect.size = instance.size
    
    def _update_total_box(self, instance, value):
        self.total_box_rect.pos = instance.pos
        self.total_box_rect.size = instance.size
    
    def create_right_column(self):
        """Coluna direita: Scanner + Pagamento"""
        col = BoxLayout(orientation='vertical', spacing=8)
        
        # Scanner Card COMPACTO
        scanner_card = self.create_scanner_card()
        scanner_card.size_hint_y = 0.35
        
        # Payment Card
        payment_card = self.create_payment_card()
        payment_card.size_hint_y = 0.65
        
        col.add_widget(scanner_card)
        col.add_widget(payment_card)
        
        return col
    
    def create_scanner_card(self):
        """Scanner minimalista e funcional"""
        card = BoxLayout(orientation='vertical', padding=8, spacing=5)
        
        with card.canvas.before:
            Color(1, 1, 1, 1)
            self.scanner_card_rect = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[10]
            )
        card.bind(pos=self._update_scanner_card, size=self._update_scanner_card)
        
        # Título com botão destacar
        title_box = BoxLayout(size_hint_y=None, height=22, spacing=4)
        title_text = Label(
            text='📷 SCANNER',
            bold=True,
            font_size='13sp',
            color=[0.2, 0.2, 0.2, 1],
            halign='left'
        )
        title_text.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        
        self.detach_btn = Button(
            text='⬈',
            size_hint=(None, None),
            size=(24, 22),
            background_color=[0.3, 0.5, 0.7, 1],
            background_normal='',
            bold=True,
            font_size='12sp',
            color=[1, 1, 1, 1]
        )
        self.detach_btn.bind(on_release=self.toggle_camera_detach)
        
        title_box.add_widget(title_text)
        title_box.add_widget(self.detach_btn)
        
        # Container da câmera MUITO MENOR
        self.camera_container = BoxLayout(
            size_hint_y=None,
            height=85,
            padding=2
        )
        with self.camera_container.canvas.before:
            Color(0.89, 0.89, 0.89, 1)
            self.camera_outer_border = RoundedRectangle(
                pos=self.camera_container.pos,
                size=self.camera_container.size,
                radius=[6]
            )
        self.camera_container.bind(pos=self._update_camera_outer, size=self._update_camera_outer)
        
        camera_inner = BoxLayout(padding=0)
        with camera_inner.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            self.camera_bg = RoundedRectangle(
                pos=camera_inner.pos,
                size=camera_inner.size,
                radius=[5]
            )
        camera_inner.bind(pos=self._update_camera_bg, size=self._update_camera_bg)
        
        self.camera_image = Image(allow_stretch=True, keep_ratio=True)
        camera_inner.add_widget(self.camera_image)
        self.camera_container.add_widget(camera_inner)
        
        # Status ultra-compacto
        self.scanner_status = Label(
            text='⚫ Inativa',
            size_hint_y=None,
            height=20,
            color=[0.5, 0.5, 0.5, 1],
            font_size='10sp',
            bold=True
        )
        
        # Botões em linha
        btn_layout = BoxLayout(size_hint_y=None, height=32, spacing=4)
        
        self.scan_btn = Button(
            text='▶',
            background_color=[0.16, 0.66, 0.26, 1],
            background_normal='',
            bold=True,
            font_size='14sp',
            color=[1, 1, 1, 1]
        )
        self.scan_btn.bind(on_release=self.toggle_scanner)
        
        switch_cam_btn = Button(
            text='🔄',
            size_hint_x=0.4,
            background_color=[0.26, 0.46, 0.66, 1],
            background_normal='',
            bold=True,
            font_size='13sp',
            color=[1, 1, 1, 1]
        )
        switch_cam_btn.bind(on_release=self.switch_camera)
        
        btn_layout.add_widget(self.scan_btn)
        btn_layout.add_widget(switch_cam_btn)
        
        card.add_widget(title_box)
        card.add_widget(self.camera_container)
        card.add_widget(self.scanner_status)
        card.add_widget(btn_layout)
        
        self.camera_detached = False
        self.floating_camera_popup = None
        
        return card
    
    def _update_camera_outer(self, instance, value):
        self.camera_outer_border.pos = instance.pos
        self.camera_outer_border.size = instance.size
    
    def _update_camera_bg(self, instance, value):
        self.camera_bg.pos = instance.pos
        self.camera_bg.size = instance.size
    
    def _update_scanner_card(self, instance, value):
        self.scanner_card_rect.pos = instance.pos
        self.scanner_card_rect.size = instance.size
    
    def toggle_camera_detach(self, instance):
        """Destacar/encaixar câmera"""
        if not self.camera_detached:
            self.detach_camera()
        else:
            self.attach_camera()
    
    def detach_camera(self):
        """Destacar câmera em janela flutuante"""
        content = BoxLayout(orientation='vertical', padding=0, spacing=0)
        
        scatter = Scatter(
            do_rotation=False,
            do_scale=True,
            scale_min=0.3,
            scale_max=3.0,
            size_hint=(None, None),
            size=(400, 350)
        )
        
        scatter_content = BoxLayout(orientation='vertical', padding=10, spacing=5)
        with scatter_content.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            scatter_bg = Rectangle(pos=scatter_content.pos, size=scatter_content.size)
        scatter_content.bind(pos=lambda s, v, r=scatter_bg: setattr(r, 'pos', s.pos))
        scatter_content.bind(size=lambda s, v, r=scatter_bg: setattr(r, 'size', s.size))
        
        title_bar = BoxLayout(size_hint_y=None, height=35, spacing=10, padding=[10, 5])
        with title_bar.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            title_bg = Rectangle(pos=title_bar.pos, size=title_bar.size)
        title_bar.bind(pos=lambda s, v, r=title_bg: setattr(r, 'pos', s.pos))
        title_bar.bind(size=lambda s, v, r=title_bg: setattr(r, 'size', s.size))
        
        title_label = Label(
            text='📷 Scanner - Arraste | Pinça para redimensionar',
            color=[1, 1, 1, 1],
            font_size='12sp',
            bold=True
        )
        
        close_btn = Button(
            text='✖',
            size_hint=(None, None),
            size=(30, 25),
            background_color=[0.8, 0.2, 0.2, 1],
            background_normal='',
            bold=True,
            color=[1, 1, 1, 1]
        )
        close_btn.bind(on_release=lambda x: self.attach_camera())
        
        title_bar.add_widget(title_label)
        title_bar.add_widget(close_btn)
        
        camera_box = BoxLayout(padding=5)
        with camera_box.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            camera_box_bg = Rectangle(pos=camera_box.pos, size=camera_box.size)
        camera_box.bind(pos=lambda s, v, r=camera_box_bg: setattr(r, 'pos', s.pos))
        camera_box.bind(size=lambda s, v, r=camera_box_bg: setattr(r, 'size', s.size))
        
        self.camera_container.clear_widgets()
        camera_box.add_widget(self.camera_image)
        
        scatter_content.add_widget(title_bar)
        scatter_content.add_widget(camera_box)
        scatter.add_widget(scatter_content)
        content.add_widget(scatter)
        
        self.floating_camera_popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(500, 450),
            separator_height=0,
            auto_dismiss=False,
            background='',
            background_color=[0, 0, 0, 0]
        )
        
        self.floating_camera_popup.open()
        self.camera_detached = True
        self.detach_btn.text = '⬊'
        self.detach_btn.background_color = [0.8, 0.4, 0.2, 1]
        
        placeholder = Label(
            text='📷\nCâmera\nDestacada',
            color=[0.5, 0.5, 0.5, 1],
            font_size='10sp',
            halign='center'
        )
        placeholder.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        self.camera_container.add_widget(placeholder)
    
    def attach_camera(self):
        """Encaixar câmera de volta"""
        if self.floating_camera_popup:
            self.floating_camera_popup.content.children[0].children[0].children[0].clear_widgets()
            self.floating_camera_popup.dismiss()
            self.floating_camera_popup = None
        
        self.camera_container.clear_widgets()
        
        camera_inner = BoxLayout(padding=0)
        with camera_inner.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            camera_bg = RoundedRectangle(pos=camera_inner.pos, size=camera_inner.size, radius=[5])
        camera_inner.bind(pos=lambda s, v, r=camera_bg: setattr(r, 'pos', s.pos))
        camera_inner.bind(size=lambda s, v, r=camera_bg: setattr(r, 'size', s.size))
        
        camera_inner.add_widget(self.camera_image)
        self.camera_container.add_widget(camera_inner)
        
        self.camera_detached = False
        self.detach_btn.text = '⬈'
        self.detach_btn.background_color = [0.3, 0.5, 0.7, 1]
    
    def create_payment_card(self):
        """Card de pagamento"""
        card = BoxLayout(orientation='vertical', padding=12, spacing=8)
        
        with card.canvas.before:
            Color(1, 1, 1, 1)
            self.payment_card_rect = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[10]
            )
        card.bind(pos=self._update_payment_card, size=self._update_payment_card)
        
        title = Label(
            text='💳 PAGAMENTO',
            size_hint_y=None,
            height=26,
            bold=True,
            font_size='15sp',
            color=[0.2, 0.2, 0.2, 1]
        )
        
        # Valor pago
        paid_layout = BoxLayout(size_hint_y=None, height=45, spacing=8)
        paid_layout.add_widget(Label(
            text='Pago:',
            bold=True,
            size_hint_x=0.35,
            color=[0.2, 0.2, 0.2, 1],
            font_size='13sp'
        ))
        self.paid_input = TextInput(
            hint_text='0.00',
            input_filter='float',
            multiline=False,
            font_size='16sp',
            size_hint_x=0.65,
            padding=[8, 10]
        )
        self.paid_input.bind(text=self.calculate_change)
        paid_layout.add_widget(self.paid_input)
        
        # Troco
        change_layout = BoxLayout(size_hint_y=None, height=45, spacing=8)
        change_layout.add_widget(Label(
            text='Troco:',
            bold=True,
            size_hint_x=0.35,
            color=[0.2, 0.2, 0.2, 1],
            font_size='13sp'
        ))
        self.change_label = Label(
            text='0.00 MZN',
            bold=True,
            font_size='16sp',
            size_hint_x=0.65,
            color=[0.16, 0.66, 0.16, 1]
        )
        change_layout.add_widget(self.change_label)
        
        # Botões
        actions_layout = BoxLayout(
            orientation='vertical',
            spacing=7,
            size_hint_y=None,
            height=135
        )
        
        btn_finalize = Button(
            text='✓ FINALIZAR',
            background_color=[0.12, 0.62, 0.22, 1],
            background_normal='',
            bold=True,
            font_size='14sp'
        )
        btn_finalize.bind(on_release=self.finalize_sale)
        
        btn_print = Button(
            text='🖨️ IMPRIMIR',
            background_color=[0.22, 0.42, 0.72, 1],
            background_normal='',
            bold=True,
            font_size='13sp'
        )
        btn_print.bind(on_release=self.print_receipt)
        
        btn_cancel = Button(
            text='✖ CANCELAR',
            background_color=[0.82, 0.32, 0.32, 1],
            background_normal='',
            bold=True,
            font_size='13sp'
        )
        btn_cancel.bind(on_release=self.cancel_sale)
        
        actions_layout.add_widget(btn_finalize)
        actions_layout.add_widget(btn_print)
        actions_layout.add_widget(btn_cancel)
        
        card.add_widget(title)
        card.add_widget(Widget())
        card.add_widget(paid_layout)
        card.add_widget(change_layout)
        card.add_widget(Widget())
        card.add_widget(actions_layout)
        
        return card
    
    def _update_payment_card(self, instance, value):
        self.payment_card_rect.pos = instance.pos
        self.payment_card_rect.size = instance.size
    
    # =============== MÉTODOS DE FUNCIONALIDADE ===============
    
    def load_products(self):
        """Carregar produtos"""
        try:
            products = self.db.get_products_for_sale()
            self.products_dict = {}
            
            print("\n" + "="*70)
            print("📦 PRODUTOS CARREGADOS")
            print("="*70)
            
            for p in products:
                self.products_dict[p[0]] = p
                barcode_display = f"'{p[4]}'" if p[4] else "SEM CÓDIGO"
                print(f"ID: {p[0]:4d} | {p[1]:35s} | Estoque: {p[2]:4d} | "
                      f"Preço: {p[3]:8.2f} | Barcode: {barcode_display}")
            
            print(f"\n✅ Total: {len(self.products_dict)} produtos")
            print("="*70 + "\n")
            
            self.display_products(products)
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
    
    def display_products(self, products):
        """Exibir produtos"""
        self.products_list.clear_widgets()
        
        if not products:
            self.products_list.add_widget(Label(
                text='Nenhum produto',
                size_hint_y=None,
                height=50,
                color=[0.5, 0.5, 0.5, 1],
                italic=True
            ))
            self.products_count_label.text = '0 itens'
            return
        
        self.products_count_label.text = f'{len(products)} itens'
        
        for product in products:
            try:
                product_id = product[0]
                product_name = product[1]
                product_stock = product[2]
                product_price = product[3]
                
                item_card = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=70,
                    padding=[0, 0],
                    spacing=0
                )

                # ===== FUNDO DO CARD =====
                with item_card.canvas.before:
                    # Sombra
                    Color(0, 0, 0, 0.06)
                    shadow = RoundedRectangle(
                        pos=(item_card.x + 1, item_card.y - 2),
                        size=item_card.size,
                        radius=[10]
                    )
                    # Fundo branco
                    Color(1, 1, 1, 1)
                    bg = RoundedRectangle(
                        pos=item_card.pos,
                        size=item_card.size,
                        radius=[10]
                    )
                    # Borda
                    Color(0.92, 0.92, 0.92, 1)
                    border = Line(
                        rounded_rectangle=(item_card.x, item_card.y, item_card.width, item_card.height, 10),
                        width=1
                    )

                item_card.bind(
                    pos=lambda s, v, r=bg, sh=shadow, b=border: [
                        setattr(r, 'pos', s.pos),
                        setattr(sh, 'pos', (s.x + 1, s.y - 2)),
                        setattr(b, 'rounded_rectangle', (s.x, s.y, s.width, s.height, 10))
                    ],
                    size=lambda s, v, r=bg, sh=shadow, b=border: [
                        setattr(r, 'size', s.size),
                        setattr(sh, 'size', s.size),
                        setattr(b, 'rounded_rectangle', (s.x, s.y, s.width, s.height, 10))
                    ]
                )

                # ===== CAMPO ID (8% da largura) =====
                id_field = BoxLayout(
                    orientation='vertical',
                    size_hint=(0.08, 1),
                    padding=[8, 10]
                )

                id_header = Label(
                    text='ID',
                    font_size='9sp',
                    bold=True,
                    color=[0.5, 0.5, 0.5, 1],
                    size_hint_y=None,
                    height=12,
                    halign='center',
                    valign='bottom'
                )
                id_header.bind(size=lambda s, v: setattr(s, 'text_size', s.size))

                id_value = Label(
                    text=f'{product_id}',
                    font_size='14sp',
                    bold=True,
                    color=[0.25, 0.5, 0.85, 1],
                    halign='center',
                    valign='top'
                )
                id_value.bind(size=lambda s, v: setattr(s, 'text_size', s.size))

                id_field.add_widget(id_header)
                id_field.add_widget(id_value)

                # Divisor 1
                div1 = Widget(size_hint=(None, 1), width=1)
                with div1.canvas:
                    Color(0.9, 0.9, 0.9, 1)
                    div1_line = Rectangle(pos=div1.pos, size=div1.size)
                div1.bind(
                    pos=lambda s, v, r=div1_line: setattr(r, 'pos', (s.x, s.y + 10)),
                    size=lambda s, v, r=div1_line: setattr(r, 'size', (s.width, s.height - 20))
                )

                # ===== CAMPO NOME (40% da largura - flex) =====
                name_field = BoxLayout(
                    orientation='vertical',
                    size_hint=(0.30, 1),
                    padding=[12, 10]
                )

                name_header = Label(
                    text='PRODUTO',
                    font_size='9sp',
                    bold=True,
                    color=[0.5, 0.5, 0.5, 1],
                    size_hint_y=None,
                    height=12,
                    halign='left',
                    valign='bottom'
                )
                name_header.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

                name_value = Label(
                    text=product_name,
                    font_size='14sp',
                    bold=True,
                    color=[0.15, 0.15, 0.15, 1],
                    halign='left',
                    valign='top',
                    shorten=True,
                    shorten_from='right'
                )
                name_value.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))

                name_field.add_widget(name_header)
                name_field.add_widget(name_value)

                # Divisor 2
                div2 = Widget(size_hint=(None, 1), width=1)
                with div2.canvas:
                    Color(0.9, 0.9, 0.9, 1)
                    div2_line = Rectangle(pos=div2.pos, size=div2.size)
                div2.bind(
                    pos=lambda s, v, r=div2_line: setattr(r, 'pos', (s.x, s.y + 10)),
                    size=lambda s, v, r=div2_line: setattr(r, 'size', (s.width, s.height - 20))
                )

                # ===== CAMPO ESTOQUE (15% da largura) =====
                stock_field = BoxLayout(
                    orientation='vertical',
                    size_hint=(0.20, 1),
                    padding=[10, 10]
                )

                stock_header = Label(
                    text='ESTOQUE',
                    font_size='9sp',
                    bold=True,
                    color=[0.5, 0.5, 0.5, 1],
                    size_hint_y=None,
                    height=12,
                    halign='center',
                    valign='bottom'
                )
                stock_header.bind(size=lambda s, v: setattr(s, 'text_size', s.size))

                # Definir cor baseada no estoque
                if product_stock > 50:
                    stock_color = [0.15, 0.7, 0.3, 1]  # Verde
                elif product_stock > 20:
                    stock_color = [0.9, 0.7, 0.1, 1]  # Amarelo
                else:
                    stock_color = [0.9, 0.2, 0.2, 1]  # Vermelho

                stock_value = Label(
                    text=str(product_stock),
                    font_size='16sp',
                    bold=True,
                    color=stock_color,
                    halign='center',
                    valign='top'
                )
                stock_value.bind(size=lambda s, v: setattr(s, 'text_size', s.size))

                stock_field.add_widget(stock_header)
                stock_field.add_widget(stock_value)

                # Divisor 3
                div3 = Widget(size_hint=(None, 1), width=1)
                with div3.canvas:
                    Color(0.9, 0.9, 0.9, 1)
                    div3_line = Rectangle(pos=div3.pos, size=div3.size)
                div3.bind(
                    pos=lambda s, v, r=div3_line: setattr(r, 'pos', (s.x, s.y + 10)),
                    size=lambda s, v, r=div3_line: setattr(r, 'size', (s.width, s.height - 20))
                )

                # ===== CAMPO PREÇO (20% da largura) =====
                price_field = BoxLayout(
                    orientation='vertical',
                    size_hint=(0.30, 1),
                    padding=[10, 10]
                )

                price_header = Label(
                    text='PREÇO',
                    font_size='9sp',
                    bold=True,
                    color=[0.5, 0.5, 0.5, 1],
                    size_hint_y=None,
                    height=12,
                    halign='center',
                    valign='bottom'
                )
                price_header.bind(size=lambda s, v: setattr(s, 'text_size', s.size))

                price_value_box = BoxLayout(
                    orientation='horizontal',
                    spacing=3,
                    padding=[0, 2, 0, 0]
                )

                price_amount = Label(
                    text=f'{product_price:,.2f}',
                    font_size='14sp',
                    bold=True,
                    color=[0.12, 0.65, 0.25, 1],
                    halign='right',
                    valign='top'
                )
                price_amount.bind(size=lambda s, v: setattr(s, 'text_size', s.size))

                price_currency = Label(
                    text='MZN',
                    font_size='9sp',
                    bold=True,
                    color=[0.12, 0.65, 0.25, 0.8],
                    size_hint_x=None,
                    width=28,
                    halign='left',
                    valign='top'
                )
                price_currency.bind(size=lambda s, v: setattr(s, 'text_size', s.size))

                price_value_box.add_widget(price_amount)
                price_value_box.add_widget(price_currency)

                price_field.add_widget(price_header)
                price_field.add_widget(price_value_box)

                # Divisor 4
                div4 = Widget(size_hint=(None, 1), width=1)
                with div4.canvas:
                    Color(0.9, 0.9, 0.9, 1)
                    div4_line = Rectangle(pos=div4.pos, size=div4.size)
                div4.bind(
                    pos=lambda s, v, r=div4_line: setattr(r, 'pos', (s.x, s.y + 10)),
                    size=lambda s, v, r=div4_line: setattr(r, 'size', (s.width, s.height - 20))
                )

                # ===== BOTÃO ADICIONAR (17% da largura) =====
                btn_field = BoxLayout(
                    size_hint=(0.17, 1),
                    padding=[10, 12]
                )

                add_btn = Button(
                    text='+',
                    size_hint=(1, 1),
                    background_color=[0, 0, 0, 0],
                    background_normal='',
                    bold=True,
                    font_size='26sp',
                    color=[1, 1, 1, 1]
                )

                with add_btn.canvas.before:
                    Color(0.15, 0.7, 0.3, 1)
                    btn_bg = RoundedRectangle(
                        pos=add_btn.pos,
                        size=add_btn.size,
                        radius=[8]
                    )

                add_btn.bind(
                    pos=lambda s, v, r=btn_bg: setattr(r, 'pos', s.pos),
                    size=lambda s, v, r=btn_bg: setattr(r, 'size', s.size)
                )

                add_btn.bind(on_release=lambda btn, p=product: self.add_to_cart(p))

                btn_field.add_widget(add_btn)

                # ===== MONTAGEM DA TABELA RESPONSIVA =====
                item_card.add_widget(id_field)
                item_card.add_widget(div1)
                item_card.add_widget(name_field)
                item_card.add_widget(div2)
                item_card.add_widget(stock_field)
                item_card.add_widget(div3)
                item_card.add_widget(price_field)
                item_card.add_widget(div4)
                item_card.add_widget(btn_field)

                self.products_list.add_widget(item_card)
            except Exception as e:
                print(f"Erro ao exibir produto: {e}")
                continue
    
    def on_search(self, instance, text):
        """Filtrar produtos por nome, ID ou código"""
        if not text:
            self.load_products()
            return
        
        try:
            products = self.db.get_products_for_sale()
            text_lower = text.lower().strip()
            
            filtered = [
                p for p in products
                if (text_lower in str(p[1]).lower() or  # nome
                    text_lower in str(p[0]) or  # ID
                    (p[4] and text_lower in str(p[4]).lower()))  # barcode
            ]
            
            self.display_products(filtered)
            
        except Exception as e:
            print(f"Erro na pesquisa: {e}")
    
    def on_search_enter(self, instance):
        """Ao pressionar Enter, busca por código de barras exato"""
        text = instance.text.strip()
        if not text:
            return
        
        print(f"\n{'='*70}")
        print(f"🔍 BUSCA POR ENTER - Código: '{text}'")
        print(f"{'='*70}")
        
        try:
            # Tentar buscar produto por código de barras exato
            product = self.db.get_product_by_barcode(text)
            
            if product:
                print(f"✅ PRODUTO ENCONTRADO!")
                print(f"   ID: {product[0]} | Nome: {product[1]}")
                print(f"{'='*70}\n")
                
                self.add_to_cart(product)
                self.show_message(f'✅ {product[1]} adicionado!')
                instance.text = ''
            else:
                print(f"❌ Código não encontrado")
                print(f"{'='*70}\n")
                # Mantém o filtro de pesquisa
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
    
    def add_to_cart(self, product):
        """Adicionar ao carrinho"""
        try:
            product_id = product[0]
            product_name = product[1]
            product_stock = product[2]
            product_price = product[3]
            
            for item in self.cart_items:
                if item['id'] == product_id:
                    if item['qty'] + 1 <= product_stock:
                        item['qty'] += 1
                        item['total'] = item['qty'] * item['price']
                        self.update_cart_display()
                        return
                    else:
                        self.show_message("❌ Estoque insuficiente!")
                        return
            
            self.cart_items.append({
                'id': product_id,
                'name': product_name,
                'qty': 1,
                'price': product_price,
                'total': product_price,
                'max_stock': product_stock
            })
            
            self.update_cart_display()
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()
    
    def update_cart_display(self):
        """Atualizar carrinho"""
        self.cart_list.clear_widgets()
        self.total_amount = 0
        
        if not self.cart_items:
            self.cart_count_label.text = '0 itens'
        else:
            self.cart_count_label.text = f'{len(self.cart_items)} itens'
        
        for i, item in enumerate(self.cart_items):
            bg_color = [0.98, 0.98, 0.98, 1] if i % 2 == 0 else [1, 1, 1, 1]
            
            headers = [
                ('ID', 0.11),
                ('Produto', 0.39),
                ('Qtd', 0.17),
                ('Total', 0.23),
                ('', 0.10)
            ]
            
            # ID
            id_cell = self.create_cart_cell(str(item['id']), bg_color)
            id_cell.size_hint_x = headers[0][1]
            self.cart_list.add_widget(id_cell)
            
            # Nome
            name = item['name'][:11] + '...' if len(item['name']) > 11 else item['name']
            name_cell = self.create_cart_cell(name, bg_color)
            name_cell.size_hint_x = headers[1][1]
            self.cart_list.add_widget(name_cell)
            
            # Quantidade
            qty_input = TextInput(
                text=str(item['qty']),
                input_filter='int',
                multiline=False,
                size_hint_y=None,
                height=26,
                font_size='11sp',
                padding=[3, 5]
            )
            qty_input.bind(text=lambda inst, val, idx=i: self.update_qty(idx, val))
            cell = BoxLayout(padding=1, size_hint_x=headers[2][1])
            with cell.canvas.before:
                Color(*bg_color)
                cell_rect = RoundedRectangle(pos=cell.pos, size=cell.size, radius=[3])
            cell.bind(pos=lambda s, v, r=cell_rect: setattr(r, 'pos', s.pos))
            cell.bind(size=lambda s, v, r=cell_rect: setattr(r, 'size', s.size))
            cell.add_widget(qty_input)
            self.cart_list.add_widget(cell)
            
            # Total
            total_cell = self.create_cart_cell(f'{item["total"]:.2f}', bg_color)
            total_cell.size_hint_x = headers[3][1]
            self.cart_list.add_widget(total_cell)
            
            # Remover
            btn_remove = Button(
                text='✖',
                size_hint_y=None,
                height=26,
                background_color=[0.88, 0.22, 0.22, 1],
                background_normal='',
                font_size='13sp'
            )
            btn_remove.bind(on_release=lambda btn, idx=i: self.remove_from_cart(idx))
            cell = BoxLayout(padding=1, size_hint_x=headers[4][1])
            with cell.canvas.before:
                Color(*bg_color)
                cell_rect = RoundedRectangle(pos=cell.pos, size=cell.size, radius=[3])
            cell.bind(pos=lambda s, v, r=cell_rect: setattr(r, 'pos', s.pos))
            cell.bind(size=lambda s, v, r=cell_rect: setattr(r, 'size', s.size))
            cell.add_widget(btn_remove)
            self.cart_list.add_widget(cell)
            
            self.total_amount += item['total']
        
        self.total_label.text = f'{self.total_amount:.2f} MZN'
        self.calculate_change()
    
    def create_cart_cell(self, text, bg_color):
        """Criar célula"""
        lbl = Label(
            text=text,
            size_hint_y=None,
            height=26,
            color=[0.2, 0.2, 0.2, 1],
            font_size='11sp'
        )
        with lbl.canvas.before:
            Color(*bg_color)
            bg_rect = RoundedRectangle(size=lbl.size, pos=lbl.pos, radius=[3])
        lbl.bind(size=lambda s, v, r=bg_rect: setattr(r, 'size', s.size))
        lbl.bind(pos=lambda s, v, r=bg_rect: setattr(r, 'pos', s.pos))
        return lbl
    
    def update_qty(self, index, value):
        """Atualizar quantidade"""
        try:
            if not value or value.strip() == '':
                return
            qty = int(value)
            if qty <= 0:
                return
            if index >= len(self.cart_items):
                return
            if qty > self.cart_items[index]['max_stock']:
                self.show_message("❌ Qtd excede estoque!")
                return
            
            self.cart_items[index]['qty'] = qty
            self.cart_items[index]['total'] = qty * self.cart_items[index]['price']
            Clock.schedule_once(lambda dt: self.update_cart_display(), 0.5)
            
        except ValueError:
            pass
        except Exception as e:
            print(f"Erro: {e}")
    
    def remove_from_cart(self, index):
        """Remover do carrinho"""
        try:
            if 0 <= index < len(self.cart_items):
                self.cart_items.pop(index)
                self.update_cart_display()
        except Exception as e:
            print(f"Erro: {e}")
    
    def clear_cart(self, instance):
        """Limpar carrinho"""
        self.cart_items.clear()
        self.update_cart_display()
    
    def calculate_change(self, *args):
        """Calcular troco"""
        try:
            paid = float(self.paid_input.text) if self.paid_input.text else 0
            change = paid - self.total_amount
            
            if change >= 0:
                self.change_label.text = f'{change:.2f} MZN'
                self.change_label.color = [0.16, 0.66, 0.16, 1]
            else:
                self.change_label.text = 'INSUFICIENTE'
                self.change_label.color = [0.88, 0.22, 0.22, 1]
                
        except ValueError:
            self.change_label.text = '0.00 MZN'
        except Exception as e:
            self.change_label.text = '0.00 MZN'
    
    def toggle_scanner(self, instance):
        """Toggle scanner"""
        if not self.scanning:
            self.scanning = True
            self.scan_btn.text = '⏹'
            self.scan_btn.background_color = [0.88, 0.26, 0.26, 1]
            self.scanner_status.text = '🟢 Ativo'
            self.scanner_status.color = [0.16, 0.72, 0.22, 1]
            Clock.schedule_interval(self.update_camera, 1.0/15.0)
        else:
            self.scanning = False
            self.scan_btn.text = '▶'
            self.scan_btn.background_color = [0.16, 0.66, 0.26, 1]
            self.scanner_status.text = '⚫ Inativa'
            self.scanner_status.color = [0.5, 0.5, 0.5, 1]
            Clock.unschedule(self.update_camera)
            if hasattr(self, 'camera_capture') and self.camera_capture:
                self.camera_capture.release()
                self.camera_capture = None
            self.camera_image.texture = None
    
    def update_camera(self, dt):
        """Atualizar câmera"""
        if not self.scanning:
            return
        
        if not hasattr(self, 'camera_capture') or self.camera_capture is None:
            try:
                self.camera_capture = cv2.VideoCapture(self.current_camera)
                self.camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                if not self.camera_capture.isOpened():
                    self.scanner_status.text = f'❌ Erro'
                    self.scanner_status.color = [0.9, 0.2, 0.2, 1]
                    self.scanning = False
                    self.scan_btn.text = '▶'
                    self.scan_btn.background_color = [0.16, 0.66, 0.26, 1]
                    return
                
                self.last_barcode = None
                self.last_barcode_time = 0
                
            except Exception as e:
                print(f"❌ Erro: {e}")
                return
        
        ret, frame = self.camera_capture.read()
        
        if not ret:
            return
        
        try:
            import time
            
            frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)
            codes = decode(frame)
            current_time = time.time()
            
            if codes:
                for code in codes:
                    try:
                        barcode_raw = code.data.decode('utf-8')
                        barcode_value = ''.join(c for c in barcode_raw if c.isprintable()).strip()
                        
                        if (barcode_value == self.last_barcode and 
                            (current_time - self.last_barcode_time) < 2):
                            continue
                        
                        self.last_barcode = barcode_value
                        self.last_barcode_time = current_time
                        
                        print(f"\n{'='*70}")
                        print(f"📷 CÓDIGO: '{barcode_value}'")
                        print(f"{'='*70}")
                        
                        self.scanner_status.text = f'🔍'
                        self.scanner_status.color = [0.2, 0.5, 0.8, 1]
                        
                        product = self.db.get_product_by_barcode(barcode_value)
                        
                        if product:
                            print(f"✅ OK: {product[1]}")
                            print(f"{'='*70}\n")
                            
                            self.add_to_cart(product)
                            self.show_message(f'✅ {product[1]}')
                            self.scanner_status.text = f'✅ OK'
                            self.scanner_status.color = [0.16, 0.72, 0.22, 1]
                            
                        else:
                            print(f"❌ NÃO ENCONTRADO")
                            print(f"{'='*70}\n")
                            
                            self.show_message(f'❌ Não cadastrado!')
                            self.scanner_status.text = f'❌'
                            self.scanner_status.color = [0.88, 0.32, 0.22, 1]
                        
                        pts = code.polygon
                        if len(pts) == 4:
                            pts = [(p.x, p.y) for p in pts]
                            cv2.polylines(frame, [np.array(pts, dtype=np.int32)], 
                                        True, (0, 255, 0), 3)
                        
                        x, y, w, h = code.rect
                        cv2.putText(frame, barcode_value, (x, y - 10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                    except Exception as e:
                        print(f"❌ Erro: {e}")
                        continue
            
            else:
                if (current_time - self.last_barcode_time) > 2.5:
                    self.scanner_status.text = '🟢 Ativo'
                    self.scanner_status.color = [0.16, 0.72, 0.22, 1]
            
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), 
                colorfmt='bgr'
            )
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.camera_image.texture = texture
            
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    def switch_camera(self, instance):
        """Trocar câmera"""
        was_scanning = self.scanning
        
        if self.scanning:
            self.scanning = False
            Clock.unschedule(self.update_camera)
            if hasattr(self, 'camera_capture') and self.camera_capture:
                self.camera_capture.release()
                self.camera_capture = None
        
        self.current_camera = (self.current_camera + 1) % 3
        self.show_message(f'📷 Câmera {self.current_camera}')
        
        if was_scanning:
            Clock.schedule_once(lambda dt: self.restart_scanner(), 0.3)
    
    def restart_scanner(self):
        """Reiniciar scanner"""
        self.scanning = True
        self.scan_btn.text = '⏹'
        self.scan_btn.background_color = [0.88, 0.26, 0.26, 1]
        self.scanner_status.text = '🟢 Ativo'
        self.scanner_status.color = [0.16, 0.72, 0.22, 1]
        Clock.schedule_interval(self.update_camera, 1.0/15.0)
    
    def finalize_sale(self, instance):
        """Finalizar venda"""
        if not self.cart_items:
            self.show_message("❌ Carrinho vazio!")
            return
        
        try:
            paid = float(self.paid_input.text) if self.paid_input.text else 0
            if paid < self.total_amount:
                self.show_message("❌ Pagamento insuficiente!")
                return
        except ValueError:
            self.show_message("❌ Valor inválido!")
            return
        
        try:
            for item in self.cart_items:
                self.db.add_sale(item['id'], item['qty'], item['price'])
            
            self.show_message("✅ Venda finalizada!")
            Clock.schedule_once(lambda dt: self.reset_sale(), 2)
            
        except Exception as e:
            print(f"Erro: {e}")
            self.show_message("❌ Erro!")
    
    def reset_sale(self):
        """Reset"""
        self.cart_items.clear()
        self.paid_input.text = ''
        self.update_cart_display()
        self.load_products()
    
    def print_receipt(self, instance):
        """Imprimir"""
        if not self.cart_items:
            self.show_message("❌ Nada para imprimir!")
            return
        
        receipt_text = "=" * 40 + "\n"
        receipt_text += "   RECIBO DE VENDA\n"
        receipt_text += "=" * 40 + "\n"
        receipt_text += f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        receipt_text += "-" * 40 + "\n"
        
        for item in self.cart_items:
            receipt_text += f"{item['name']}\n"
            receipt_text += f"  {item['qty']} x {item['price']:.2f} = {item['total']:.2f} MZN\n"
        
        receipt_text += "-" * 40 + "\n"
        receipt_text += f"TOTAL: {self.total_amount:.2f} MZN\n"
        
        try:
            paid = float(self.paid_input.text) if self.paid_input.text else 0
            change = paid - self.total_amount
            receipt_text += f"Pago: {paid:.2f} MZN\n"
            receipt_text += f"Troco: {change:.2f} MZN\n"
        except:
            pass
        
        receipt_text += "=" * 40 + "\n"
        receipt_text += "  Obrigado!\n"
        receipt_text += "=" * 40
        
        self.show_receipt_popup(receipt_text)
    
    def show_receipt_popup(self, receipt_text):
        """Mostrar recibo"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        scroll = ScrollView()
        receipt_label = Label(
            text=receipt_text,
            size_hint_y=None,
            font_size='14sp',
            color=[0.2, 0.2, 0.2, 1],
            halign='left',
            valign='top'
        )
        receipt_label.bind(texture_size=receipt_label.setter('size'))
        receipt_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width - 40, None)))
        scroll.add_widget(receipt_label)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        save_btn = Button(
            text='💾 Salvar',
            background_color=[0.2, 0.5, 0.8, 1],
            bold=True
        )
        
        close_btn = Button(
            text='Fechar',
            background_color=[0.5, 0.5, 0.5, 1],
            bold=True
        )
        
        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(close_btn)
        
        content.add_widget(scroll)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='📄 Recibo',
            content=content,
            size_hint=(0.6, 0.8)
        )
        
        close_btn.bind(on_release=popup.dismiss)
        save_btn.bind(on_release=lambda x: self.save_receipt(receipt_text, popup))
        
        popup.open()
    
    def save_receipt(self, receipt_text, popup):
        """Salvar recibo"""
        try:
            filename = f"recibo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(receipt_text)
            
            self.show_message(f"✅ Salvo: {filename}")
            popup.dismiss()
            
        except Exception as e:
            print(f"Erro: {e}")
            self.show_message(f"❌ Erro!")
    
    def cancel_sale(self, instance):
        """Cancelar"""
        if not self.cart_items:
            self.show_message("Carrinho vazio!")
            return
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        message = Label(
            text='⚠️ Cancelar venda?',
            font_size='18sp',
            color=[0.2, 0.2, 0.2, 1]
        )
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        yes_btn = Button(
            text='✓ Sim',
            background_color=[0.9, 0.3, 0.3, 1],
            bold=True
        )
        
        no_btn = Button(
            text='✖ Não',
            background_color=[0.5, 0.5, 0.5, 1],
            bold=True
        )
        
        btn_layout.add_widget(no_btn)
        btn_layout.add_widget(yes_btn)
        
        content.add_widget(message)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Confirmar',
            content=content,
            size_hint=(0.5, 0.4),
            auto_dismiss=False
        )
        
        yes_btn.bind(on_release=lambda x: self.confirm_cancel(popup))
        no_btn.bind(on_release=popup.dismiss)
        
        popup.open()
    
    def confirm_cancel(self, popup):
        """Confirmar cancelamento"""
        self.cart_items.clear()
        self.paid_input.text = ''
        self.update_cart_display()
        popup.dismiss()
        self.show_message("✅ Cancelado!")
    
    def show_message(self, message):
        """Mensagem"""
        content = BoxLayout(padding=20)
        content.add_widget(Label(
            text=message,
            font_size='16sp',
            color=[0.2, 0.2, 0.2, 1]
        ))
        
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.35, 0.18),
            auto_dismiss=True
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.8)
    
    def go_back(self, instance):
        """Voltar"""
        if self.camera_detached:
            self.attach_camera()
        
        if self.scanning:
            self.scanning = False
            Clock.unschedule(self.update_camera)
            if hasattr(self, 'camera_capture') and self.camera_capture:
                self.camera_capture.release()
                self.camera_capture = None
        self.manager.current = 'login'
    
    def on_leave(self):
        """Sair"""
        if hasattr(self, 'camera_detached') and self.camera_detached:
            self.attach_camera()
        
        if self.scanning:
            self.scanning = False
            Clock.unschedule(self.update_camera)
            if hasattr(self, 'camera_capture') and self.camera_capture:
                self.camera_capture.release()
                self.camera_capture = None