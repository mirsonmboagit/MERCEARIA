from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.label import Label
from kivy.clock import Clock
from database import Database
from kivy.lang import Builder


Builder.load_string('''

<LoginScreen>:
    username: username
    password: password

    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'horizontal'
        spacing: 0

        # =======================
        # LADO ESQUERDO - CARROSSEL
        # =======================
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.55
            
            Carousel:
                id: carousel
                direction: 'right'
                loop: True
                anim_move_duration: 0.99

                # Slide 1
                FloatLayout:
                    Image:
                        source: 'image/slide1.png'
                        allow_stretch: True
                        keep_ratio: True
                        size_hint: 0.8, 0.8
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                # Slide 2 - REDUZIDO
                FloatLayout:
                    Image:
                        source: 'image/slide2.png'
                        allow_stretch: True
                        keep_ratio: True
                        size_hint: 0.70, 0.70
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                # Slide 3
                FloatLayout:
                    Image:
                        source: 'image/slide3.png'
                        allow_stretch: True
                        keep_ratio: True
                        size_hint: 0.5, 0.5
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                

        # LINHA SEPARADORA VERTICAL
        Widget:
            size_hint_x: None
            width: 1
            canvas.before:
                Color:
                    rgba: 0.8, 0.8, 0.8, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

        # =======================
        # LADO DIREITO - LOGIN
        # =======================
        BoxLayout:
            orientation: 'vertical'
            padding: 50
            spacing: 20
            size_hint_x: 0.45
                    
                 

            # LOGO/NOME DO SISTEMA
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: 100
                spacing: 5

                Label:
                    text: 'MERCEARIA'
                    font_size: 32
                    bold: True
                    color: 0.9, 0.4, 0.1, 1
                    size_hint_y: None
                    height: 40

                Label:
                    text: 'Sistema de Gestão Comercial'
                    font_size: 14
                    color: 0.5, 0.5, 0.5, 1
                    size_hint_y: None
                    height: 20

            Widget:
                size_hint_y: None
                height: 20

            Label:
                text: 'LOGIN'
                font_size: 24
                bold: True
                size_hint_y: None
                height: 40
                color: 0.3, 0.3, 0.3, 1

            # USUÁRIO
            BoxLayout:
                orientation: 'vertical'
                spacing: 5
                size_hint_y: None
                height: 80

                Label:
                    text: 'Utilizador:'
                    color: 0.2, 0.2, 0.2, 1
                    size_hint_y: None
                    height: 20
                    halign: 'left'
                    bold: 'true'
                    text_size: self.width, None

                TextInput:
                    id: username
                    multiline: False
                    hint_text: 'Digite seu utilizador'
                    background_color: 0, 0, 0, 0
                    padding: [10, 8]
                    canvas.before:
                        Color:
                            rgba: (1, 0, 0, 1) if root.username_error else (0.8, 0.8, 0.8, 1)
                        Line:
                            rounded_rectangle: self.x, self.y, self.width, self.height, 8
                            width: 1

                Label:
                    text: root.username_error
                    color: 1, 0, 0, 1
                    font_size: 12
                    size_hint_y: None
                    height: 15
                    halign: 'left'
                    text_size: self.width, None

            # SENHA
            BoxLayout:
                orientation: 'vertical'
                spacing: 5
                size_hint_y: None
                height: 80

                Label:
                    text: 'Palavra-passe:'
                    color: 0.2, 0.2, 0.2, 1
                    size_hint_y: None
                    height: 20
                    halign: 'left'
                    bold: 'true'
                    text_size: self.width, None

                TextInput:
                    id: password
                    password: True
                    multiline: False
                    hint_text: 'Digite sua palavra-passe'
                    background_color: 0, 0, 0, 0
                    padding: [10, 8]
                    on_text_validate: root.login()
                    canvas.before:
                        Color:
                            rgba: (1, 0, 0, 1) if root.password_error else (0.8, 0.8, 0.8, 1)
                        Line:
                            rounded_rectangle: self.x, self.y, self.width, self.height, 8
                            width: 1

                Label:
                    text: root.password_error
                    color: 1, 0, 0, 1
                    font_size: 12
                    size_hint_y: None
                    height: 15
                    halign: 'left'
                    text_size: self.width, None

            # BOTÃO
            Button:
                text: 'INICIAR SESSÃO'
                size_hint_y: None
                height: 45
                background_color: 0.9, 0.4, 0.1, 1
                color: 1, 1, 1, 1
                bold: True
                font_size: 16
                on_release: root.login()

            # LINKS
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: 30
                spacing: 10

                Button:
                    text: 'Esqueci a senha'
                    font_size: 12
                    color: 0.9, 0.4, 0.1, 1
                    background_color: 0, 0, 0, 0
                    on_release: root.forgot_password()

                Label:
                    text: '|'
                    color: 0.7, 0.7, 0.7, 1
                    size_hint_x: None
                    width: 10

                Button:
                    text: 'Criar nova conta'
                    font_size: 12
                    color: 0.9, 0.4, 0.1, 1
                    background_color: 0, 0, 0, 0
                    on_release: root.register()

            Widget:
                size_hint_y: 0.5

''')

class LoginScreen(Screen):
    username = ObjectProperty(None)
    password = ObjectProperty(None)
    
    # Propriedades para armazenar os erros
    username_error = StringProperty("")
    password_error = StringProperty("")
    
    # Usuário padrão
    DEFAULT_USERNAME = "admin"
    DEFAULT_PASSWORD = "123"
    
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.db = Database()
        self.carousel_event = None
    
    def on_enter(self):
        """Chamado quando a tela é exibida"""
        # Inicia a rotação automática do carrossel a cada 4 segundos
        self.carousel_event = Clock.schedule_interval(self.next_slide, 4)
    
    def on_leave(self):
        """Chamado quando a tela é deixada"""
        # Para a rotação automática quando sair da tela
        if self.carousel_event:
            self.carousel_event.cancel()
    
    def next_slide(self, dt):
        """Avança para o próximo slide do carrossel"""
        carousel = self.ids.carousel
        carousel.load_next()
    
    def login(self):
        user = self.username.text
        pwd = self.password.text
        
        # Resetando mensagens de erro
        self.username_error = ""
        self.password_error = ""
        
        # Validação dos campos vazios
        if user == "" or pwd == "":
            if user == "":
                self.username_error = "Usuário é obrigatório!"
            if pwd == "":
                self.password_error = "Senha é obrigatória!"
            return
        
        # Verificar se é o usuário padrão
        if user == self.DEFAULT_USERNAME and pwd == self.DEFAULT_PASSWORD:
            self.reset_fields()
            self.manager.current = "admin"
            return
        
        # Caso contrário, validar no banco de dados
        role = self.db.validate_user(user, pwd)
        
        if role == "admin":
            self.reset_fields()
            self.manager.current = "admin"
        elif role == "manager":
            self.reset_fields()
            self.manager.current = "manager"
        else:
            self.username_error = "Credenciais inválidas!"
            self.password_error = "Credenciais inválidas!"
    
    def reset_fields(self):
        self.username.text = ""
        self.password.text = ""
        self.username_error = ""
        self.password_error = ""
    
    def forgot_password(self):
        """Função para recuperação de senha"""
        print("Recuperar senha - a implementar")
        # Aqui você pode abrir um popup ou navegar para outra tela
    
    def register(self):
        """Função para cadastro de novo usuário"""
        print("Cadastrar novo usuário - a implementar")
        # Aqui você pode abrir um popup ou navegar para outra tela