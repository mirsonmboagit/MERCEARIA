import os
import sys
import sqlite3
import bcrypt
# Kivy and local imports
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.metrics import dp, sp
from kivy.core.window import Window
from database import Database
from kivy.lang import Builder



Builder.load_string('''

<AdminSettingsScreen>:
    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.98, 1  # Light background
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: [40, 30]
        spacing: 25

        # Header Section
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 60
            
            Label:
                text: 'Configurações de Administração'
                font_size: '28sp'
                bold: True
                color: (0.1, 0.1, 0.2, 1)  # Dark text color
                halign: 'center'  # Centralizado
                size_hint_x: 1

            Button:
                text: 'Voltar'
                on_press: root.manager.current = 'admin'
                size_hint: None, None
                size: 140, 40
                pos_hint: {'right': 1, 'top': 1}  # Ajustado para boa posição
                background_color: 0, 0, 0, 0  # Sem fundo
                color: (0, 0, 0, 1)  # Cor do texto preto
                bold: True
                font_name: 'Roboto'  # Fonte padrão do Kivy (Roboto)
                canvas.before:
                    Color:
                        rgba: 0, 0, 0, 1  # Cor preta para a borda também
                    Line:
                        width: 1.5
                        rounded_rectangle: (*self.pos, *self.size, 10)

        # Buttons Section
        GridLayout:
            cols: 2
            spacing: [20, 20]
            padding: [20, 10]
            
            Button:
                text: 'Adicionar Usuário'
                on_press: root.add_user()
                font_size: '16sp'
                bold: True
                font_name: 'Roboto'  # Fonte padrão do Kivy
                color: (0, 0, 0, 1)
                background_color: 0, 0, 0, 0
                canvas.before:
                    Color:
                        rgba: 0.2, 0.2, 0.2, 1
                    Line:
                        width: 1.5
                        rounded_rectangle: (*self.pos, *self.size, 10)

            Button:
                text: 'Apagar Gerente'
                on_press: root.delete_manager()
                font_size: '16sp'
                bold: True
                font_name: 'Roboto'  # Fonte padrão do Kivy
                color: (0, 0, 0, 1)
                background_color: 0, 0, 0, 0
                canvas.before:
                    Color:
                        rgba: 0.2, 0.2, 0.2, 1
                    Line:
                        width: 1.5
                        rounded_rectangle: (*self.pos, *self.size, 10)

            Button:
                text: 'Alterar Dados do Admin'
                on_press: root.change_admin_data()
                font_size: '16sp'
                bold: True
                font_name: 'Roboto'  # Fonte padrão do Kivy
                color: (0, 0, 0, 1)
                background_color: 0, 0, 0, 0
                canvas.before:
                    Color:
                        rgba: 0.2, 0.2, 0.2, 1
                    Line:
                        width: 1.5
                        rounded_rectangle: (*self.pos, *self.size, 10)

            Button:
                text: 'Dimensões da Tela'
                on_press: root.change_screen_size()
                font_size: '16sp'
                bold: True
                font_name: 'Roboto'  # Fonte padrão do Kivy
                color: (0, 0, 0, 1)
                background_color: 0, 0, 0, 0
                canvas.before:
                    Color:
                        rgba: 0.2, 0.2, 0.2, 1
                    Line:
                        width: 1.5
                        rounded_rectangle: (*self.pos, *self.size, 10)

            Button:
                text: 'Logs do Sistema'
                font_size: '16sp'
                bold: True
                font_name: 'Roboto'  # Fonte padrão do Kivy
                color: (0, 0, 0, 1)
                background_color: 0, 0, 0, 0
                canvas.before:
                    Color:
                        rgba: 0.2, 0.2, 0.2, 1
                    Line:
                        width: 1.5
                        rounded_rectangle: (*self.pos, *self.size, 10)

            Button:
                text: 'Configurações de Segurança'
                font_size: '16sp'
                bold: True
                font_name: 'Roboto'  # Fonte padrão do Kivy
                color: (0, 0, 0, 1)
                background_color: 0, 0, 0, 0
                canvas.before:
                    Color:
                        rgba: 0.2, 0.2, 0.2, 1
                    Line:
                        width: 1.5
                        rounded_rectangle: (*self.pos, *self.size, 10)

        # Footer Section
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 60
            
            Widget:  # Flexible spacing


''')
# Modal to Change Admin Data
class ChangeAdminDataPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Alterar Dados do Admin"
        self.size_hint = (0.5, 0.6)
        
        # Centralizar o popup na tela e impedir deslocamento
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Current Username
        current_username_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        current_username_layout.add_widget(Label(text='Usuário Atual:', size_hint_x=0.3))
        self.current_username_input = TextInput(multiline=False, size_hint_x=0.7)
        current_username_layout.add_widget(self.current_username_input)
        layout.add_widget(current_username_layout)
        
        # New Username
        new_username_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        new_username_layout.add_widget(Label(text='Novo Usuário:', size_hint_x=0.3))
        self.new_username_input = TextInput(multiline=False, size_hint_x=0.7)
        new_username_layout.add_widget(self.new_username_input)
        layout.add_widget(new_username_layout)
        
        # Current Password
        current_password_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        current_password_layout.add_widget(Label(text='Senha Atual:', size_hint_x=0.3))
        self.current_password_input = TextInput(multiline=False, password=True, size_hint_x=0.7)
        current_password_layout.add_widget(self.current_password_input)
        layout.add_widget(current_password_layout)
        
        # New Password
        new_password_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        new_password_layout.add_widget(Label(text='Nova Senha:', size_hint_x=0.3))
        self.new_password_input = TextInput(multiline=False, password=True, size_hint_x=0.7)
        new_password_layout.add_widget(self.new_password_input)
        layout.add_widget(new_password_layout)
        
        # Confirm New Password
        confirm_password_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        confirm_password_layout.add_widget(Label(text='Confirmar Senha:', size_hint_x=0.3))
        self.confirm_password_input = TextInput(multiline=False, password=True, size_hint_x=0.7)
        confirm_password_layout.add_widget(self.confirm_password_input)
        layout.add_widget(confirm_password_layout)
        
        # Buttons
        button_layout = BoxLayout(
            spacing=dp(10), 
            size_hint_y=None, 
            height=dp(50))
        save_btn = Button(text='Salvar', on_press=self.save_changes, background_color=(0.1, 0.6, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=sp(16),
            size_hint=(0.5, 1))
        cancel_btn = Button(text='Cancelar', on_press=self.dismiss, background_color=(0.7, 0.7, 0.7, 1),
            color=(1, 1, 1, 1), font_size=sp(16), size_hint=(0.5, 1))
        button_layout.add_widget(save_btn)
        button_layout.add_widget(cancel_btn)
        layout.add_widget(button_layout)
        
        self.content = layout
        
        # Adicionar bind para reposicionar o popup quando a janela mudar de tamanho
        from kivy.core.window import Window
        Window.bind(on_resize=self.reposition)
    
    def reposition(self, instance, width, height):
        # Recalcular a posição do popup para mantê-lo centralizado
        if self.parent:
            self.center = Window.center
    
    def open(self, *args, **kwargs):
        # Sobrescrever o método open para garantir posicionamento correto
        super(ChangeAdminDataPopup, self).open(*args, **kwargs)
        from kivy.core.window import Window
        self.center = Window.center
    
    def save_changes(self, *args):
        current_username = self.current_username_input.text.strip()
        new_username = self.new_username_input.text.strip()
        current_password = self.current_password_input.text.strip()
        new_password = self.new_password_input.text.strip()
        confirm_password = self.confirm_password_input.text.strip()
        
        # Validation
        if not current_username or not current_password:
            self.show_error('Por favor, preencha os campos de usuário e senha atuais')
            return
        
        if new_password and new_password != confirm_password:
            self.show_error('As senhas não coincidem')
            return
        
        try:
            with Database() as db:
                # Verificar se o usuário atual existe e é um admin
                db.cursor.execute(
                    "SELECT * FROM users WHERE username = ? AND role = 'admin'", 
                    (current_username,)
                )
                admin_data = db.cursor.fetchone()
                
                if not admin_data:
                    self.show_error('Usuário não encontrado ou não é administrador')
                    return
                
                # Validar a senha atual usando o método validate_user
                role = db.validate_user(current_username, current_password)
                if role != 'admin':
                    self.show_error('Senha atual incorreta')
                    return
                
                # Verificar se há alterações para fazer
                if not new_username and not new_password:
                    self.show_error('Nenhuma alteração solicitada')
                    return
                
                # Preparar a query de atualização
                update_parts = []
                update_params = []
                
                if new_username:
                    # Verificar se o novo nome de usuário já existe
                    db.cursor.execute(
                        "SELECT * FROM users WHERE username = ? AND username != ?", 
                        (new_username, current_username)
                    )
                    if db.cursor.fetchone():
                        self.show_error('Este nome de usuário já está em uso')
                        return
                    
                    update_parts.append("username = ?")
                    update_params.append(new_username)
                
                if new_password:
                    update_parts.append("password = ?")
                    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    update_params.append(hashed_password)
                
                # Construir a query final
                update_query = f"UPDATE users SET {', '.join(update_parts)} WHERE username = ? AND role = 'admin'"
                update_params.append(current_username)
                
                # Executar a atualização
                db.cursor.execute(update_query, update_params)
                db.conn.commit()
                
                # Feedback de sucesso
                success_popup = Popup(
                    title='Sucesso', 
                    content=Label(text='Dados do administrador atualizados com sucesso'),
                    size_hint=(0.6, 0.3)
                )
                success_popup.open()
                
                # Limpar os campos
                self.current_username_input.text = ''
                self.new_username_input.text = ''
                self.current_password_input.text = ''
                self.new_password_input.text = ''
                self.confirm_password_input.text = ''
                
                self.dismiss()
                
        except sqlite3.IntegrityError:
            self.show_error('Nome de usuário já existe')
        except Exception as e:
            self.show_error(f'Erro ao atualizar: {str(e)}')
    
    def show_error(self, message):
        error_popup = Popup(
            title='Erro', 
            content=Label(text=message),
            size_hint=(0.6, 0.3),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Centralizar popups de erro também
        )
        error_popup.open()
        
        # Centralizar também o popup de erro quando aberto
        from kivy.core.window import Window
        error_popup.center = Window.center

# Modal to Add User
class AddUserPopup(Popup):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.title = "Adicionar Novo Usuário"
        self.size_hint = (0.5, 0.5)  
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Username
        username_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        username_layout.add_widget(Label(text='Usuário:', size_hint_x=0.3))
        self.username_input = TextInput(multiline=False, size_hint_x=0.7)
        username_layout.add_widget(self.username_input)
        layout.add_widget(username_layout)
        
        # Password
        password_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        password_layout.add_widget(Label(text='Senha:', size_hint_x=0.3))
        self.password_input = TextInput(multiline=False, password=True, size_hint_x=0.7)
        password_layout.add_widget(self.password_input)
        layout.add_widget(password_layout)
        
        # Role (admin or manager) using Spinner
        role_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        role_layout.add_widget(Label(text='Função:', size_hint_x=0.3))
        self.role_spinner = Spinner(
            text='Escolha a função',
            values=('admin', 'manager'),  # Valores corretos para o banco
            size_hint_x=0.7
        )
        role_layout.add_widget(self.role_spinner)
        layout.add_widget(role_layout)
        
        # Buttons
        button_layout = BoxLayout(
            spacing=dp(10), 
            size_hint_y=None, 
            height=dp(50))
        save_btn = Button(text='Salvar', on_press=self.save_user,background_color=(0.1, 0.6, 0.2, 1 ),  # Vermelho para delete
            color=(1, 1, 1, 1),
            font_size=sp(16),
            size_hint=(0.5, 1))
        cancel_btn = Button(text='Cancelar', on_press=self.dismiss, background_color=(0.7, 0.7, 0.7, 1),  # Cinza para cancelar
            color=(1, 1, 1, 1),
            font_size=sp(16),
            size_hint=(0.5, 1))
        button_layout.add_widget(save_btn)
        button_layout.add_widget(cancel_btn)
        layout.add_widget(button_layout)
        
        self.content = layout
    
    def show_error(self, message):
        """Exibe uma mensagem de erro em um popup."""
        error_popup = Popup(
            title='Erro',
            content=Label(text=message),
            size_hint=(0.6, 0.3)
        )
        error_popup.open()

    def save_user(self, *args):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        role = self.role_spinner.text.strip()
        
        if not username or not password or role == 'Escolha a função':
            self.show_error('Todos os campos são obrigatórios')
            return
        
        # Verificar se o nome de usuário já existe no banco de dados
        self.db.cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
        if self.db.cursor.fetchone()[0] > 0:
            self.show_error('Erro: Nome de usuário já existe')
            return
        
        # Hash da senha usando bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            db = self.db  # Obtém a instância do banco de dados
            cursor = db.cursor  # Obtém o cursor do banco de dados
            
            # Inserir o novo usuário no banco de dados
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                (username, hashed_password, role)
            )
            db.conn.commit()  # Confirma a transação
            
            # Exibir popup de sucesso
            success_popup = Popup(
                title='Sucesso',
                content=Label(text="Usuário adicionado com sucesso"),
                size_hint=(0.6, 0.3)
            )
            success_popup.open()
            
            # Fechar o popup de adicionar usuário
            self.dismiss()

        except Exception as e:
            print(f"Erro ao adicionar usuário: {e}")
    
    def show_error(self, message):
        error_popup = Popup(
            title='Erro',
            content=Label(text=message),
            size_hint=(0.6, 0.3)
        )
        error_popup.open()

        

# Modal Delete gerente
class DeleteManagerPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Excluir Gerente"
        self.size_hint = (0.5, 0.5)
        
        # Centralizar o popup na tela e impedir deslocamento
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        
        # Título
        layout.add_widget(Label(
            text='Selecione o Gerente:', 
            size_hint_y=None, 
            height=dp(60),
            font_size=sp(24),
            color=(1, 1, 1, 1)
        ))
        
        # Obter lista de gerentes
        with Database() as db:
            self.managers = db.get_all_managers()
        
        # Spinner para seleção de gerente
        spinner_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        spinner_layout.add_widget(Label(
            text='Gerente:',
            size_hint_x=0.3,
            font_size=sp(16)
        ))
        
        # Criar o Spinner com a lista de gerentes
        self.manager_spinner = Spinner(
            text='Selecione um gerente',
            values=self.managers,
            size_hint_x=0.7,
            font_size=sp(16),
            background_color=(1, 1, 1, 1)
        )
        
        spinner_layout.add_widget(self.manager_spinner)
        layout.add_widget(spinner_layout)
        
        # Checkbox para confirmar a exclusão do último gerente
        self.confirm_checkbox_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            opacity=4  # Inicialmente invisível
        )
        
        self.confirm_checkbox = CheckBox(
            size_hint_x=0.6,
            color=(1, 0, 0, 1)
        )
        
        self.confirm_checkbox_container.add_widget(self.confirm_checkbox)
        self.confirm_checkbox_container.add_widget(Label(
            text='Confirmo que quero excluir o último gerente',
            size_hint_x=0.9,
            color=(0.9, 0.2, 0.2, 1),
            font_size=sp(14)
        ))
        
        layout.add_widget(self.confirm_checkbox_container)
        
        # Espaço adicional
        layout.add_widget(Widget(size_hint_y=None, height=dp(20)))
        
        # Botões
        button_layout = BoxLayout(
            spacing=dp(10), 
            size_hint_y=None, 
            height=dp(50)
        )
        
        self.delete_btn = Button(
            text='Excluir', 
            on_press=self.delete_manager,
            background_color=(0.9, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=sp(16),
            size_hint=(0.5, 1)
        )
        
        cancel_btn = Button(
            text='Cancelar', 
            on_press=self.dismiss,
            background_color=(0.7, 0.7, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size=sp(16),
            size_hint=(0.5, 1)
        )
        
        button_layout.add_widget(self.delete_btn)
        button_layout.add_widget(cancel_btn)
        layout.add_widget(button_layout)
        
        self.content = layout
        
        # Verificar se há apenas um gerente
        self.check_last_manager()
        
        # Adicionar bind para reposicionar o popup quando a janela mudar de tamanho
        from kivy.core.window import Window
        Window.bind(on_resize=self.reposition)
    
    def reposition(self, instance, width, height):
        # Recalcular a posição do popup para mantê-lo centralizado
        if self.parent:
            from kivy.core.window import Window
            self.center = Window.center
    
    def open(self, *args, **kwargs):
        # Sobrescrever o método open para garantir posicionamento correto
        super(DeleteManagerPopup, self).open(*args, **kwargs)
        from kivy.core.window import Window
        self.center = Window.center
    
    def check_last_manager(self):
        """Verifica se há apenas um gerente e ajusta a UI conforme necessário"""
        if len(self.managers) == 1:
            self.confirm_checkbox_container.opacity = 1
            
            # Atualizar o texto do spinner para o único gerente
            self.manager_spinner.text = self.managers[0]
            
            # Desabilitar o spinner se houver apenas um gerente
            self.manager_spinner.disabled = True
    
    def delete_manager(self, *args):
        selected_manager = self.manager_spinner.text
        
        # Verificar se um gerente foi selecionado
        if selected_manager == 'Selecione um gerente':
            self.show_error('Selecione um gerente para excluir')
            return
        
        # Verificar se é o último gerente e se a confirmação foi marcada
        is_last_manager = len(self.managers) == 1
        if is_last_manager and not self.confirm_checkbox.active:
            self.show_error('Marque a confirmação para excluir o último gerente')
            return
        
        # Mostrar popup de confirmação final
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(
            text=f'Tem certeza que deseja excluir o gerente "{selected_manager}"?',
            font_size=sp(14)
        ))
        
        buttons = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        confirm_btn = Button(
            text='Sim, excluir',
            on_press=lambda x: self.confirm_delete(selected_manager, confirmation_popup),
            background_color=(0.9, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        cancel_confirm_btn = Button(
            text='Cancelar',
            on_press=lambda x: confirmation_popup.dismiss(),
            background_color=(0.7, 0.7, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        
        buttons.add_widget(confirm_btn)
        buttons.add_widget(cancel_confirm_btn)
        content.add_widget(buttons)
        
        confirmation_popup = Popup(
            title='Confirmar Exclusão',
            content=content,
            size_hint=(0.6, 0.3),
            auto_dismiss=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Centralizar também o popup de confirmação
        )
        
        confirmation_popup.open()
        
        # Centralizar o popup de confirmação quando aberto
        from kivy.core.window import Window
        confirmation_popup.center = Window.center
        
        # Adicionar bind para reposicionar o popup de confirmação quando a janela mudar de tamanho
        confirmation_popup.reposition = lambda instance, width, height: setattr(confirmation_popup, 'center', Window.center) if confirmation_popup.parent else None
        Window.bind(on_resize=confirmation_popup.reposition)
    
    def confirm_delete(self, username, confirmation_popup):
        """Confirma e processa a exclusão do gerente após confirmação final"""
        # Fechar o popup de confirmação
        confirmation_popup.dismiss()
        
        # Modificar o método delete_manager na classe Database para permitir excluir o último gerente
        try:
            with Database() as db:
                # Ignorar a validação de último gerente executando diretamente a exclusão
                db.cursor.execute(
                    "DELETE FROM users WHERE username = ? AND role = 'manager'", 
                    (username,)
                )
                db.conn.commit()
                
                # Mostrar mensagem de sucesso
                success_popup = Popup(
                    title='Sucesso',
                    title_color=(0.2, 0.7, 0.2, 1),
                    content=Label(
                        text=f'Gerente "{username}" excluído com sucesso', 
                        font_size=sp(14),
                        color=(0.2, 0.2, 0.2, 1)
                    ),
                    size_hint=(0.5, 0.2),
                    pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Centralizar popup de sucesso
                )
                success_popup.open()
                
                # Centralizar o popup de sucesso
                from kivy.core.window import Window
                success_popup.center = Window.center
                
                # Adicionar bind para reposicionar o popup de sucesso
                success_popup.reposition = lambda instance, width, height: setattr(success_popup, 'center', Window.center) if success_popup.parent else None
                Window.bind(on_resize=success_popup.reposition)
                
                # Fechar o popup atual
                self.dismiss()
        
        except Exception as e:
            self.show_error(f'Erro ao excluir gerente: {str(e)}')
    
    def show_error(self, message):
        error_popup = Popup(
            title='Erro', 
            title_color=(0.9, 0.2, 0.2, 1),
            content=Label(
                text=message, 
                font_size=sp(14),
                color=(0.2, 0.2, 0.2, 1)
            ),
            size_hint=(0.5, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}  # Centralizar popup de erro
        )
        error_popup.open()
        
        # Centralizar o popup de erro
        error_popup.center = Window.center
        
        # Adicionar bind para reposicionar o popup de erro
        error_popup.reposition = lambda instance, width, height: setattr(error_popup, 'center', Window.center) if error_popup.parent else None
        Window.bind(on_resize=error_popup.reposition)

# Modal for Changing Screen Size
class ScreenSizePopup(Popup):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.title = "Alterar Tamanho da Tela"
        self.size_hint = (0.6, 0.6)
        
        # Lista de resoluções comuns (largura x altura)
        self.resolutions = [
            "Selecione uma resolução",
            "640 x 480 (VGA)",
            "800 x 600 (SVGA)",
            "1024 x 768 (XGA)",
            "1280 x 720 (HD/WXGA)",
            "1280 x 800 (WXGA)",
            "1280 x 1024 (SXGA)",
            "1366 x 768 (HD)",
            "1440 x 900 (WXGA+)",
            "1600 x 900 (HD+)",
            "1680 x 1050 (WSXGA+)",
            "1920 x 1080 (Full HD)",
            "1920 x 1200 (WUXGA)",
            "2048 x 1152 (QWXGA)",
            "2560 x 1440 (QHD/WQHD)",
            "2560 x 1600 (WQXGA)",
            "3440 x 1440 (UWQHD)",
            "3840 x 2160 (4K UHD)",
            "4096 x 2160 (4K)",
            "5120 x 2880 (5K)",
            "7680 x 4320 (8K UHD)",
            "Personalizado"
        ]
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Resolution Spinner
        spinner_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        spinner_layout.add_widget(Label(text='Resolução:', size_hint_x=0.3))
        self.resolution_spinner = Spinner(
            text=self.resolutions[0],
            values=self.resolutions,
            size_hint_x=0.7
        )
        self.resolution_spinner.bind(text=self.on_resolution_select)
        spinner_layout.add_widget(self.resolution_spinner)
        layout.add_widget(spinner_layout)
        
        # Width
        width_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        width_layout.add_widget(Label(text='Largura:', size_hint_x=0.3))
        self.width_input = TextInput(multiline=False, size_hint_x=0.7)
        width_layout.add_widget(self.width_input)
        layout.add_widget(width_layout)
        
        # Height
        height_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        height_layout.add_widget(Label(text='Altura:', size_hint_x=0.3))
        self.height_input = TextInput(multiline=False, size_hint_x=0.7)
        height_layout.add_widget(self.height_input)
        layout.add_widget(height_layout)
        
        # Buttons
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        change_btn = Button(text='Alterar', on_press=self.change_size)
        cancel_btn = Button(text='Cancelar', on_press=self.dismiss)
        btn_layout.add_widget(change_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)
        
        self.content = layout
    
    def on_resolution_select(self, spinner, text):
        if text == "Personalizado":
            # Limpar os campos para entrada personalizada
            self.width_input.text = ""
            self.height_input.text = ""
            return
        
        if text == self.resolutions[0]:  # "Selecione uma resolução"
            return
            
        # Extrair largura e altura da opção selecionada
        resolution_text = text.split(" (")[0]  # Remove a parte descritiva
        width, height = resolution_text.split(" x ")
        
        # Preencher os campos com os valores extraídos
        self.width_input.text = width
        self.height_input.text = height
    
    def change_size(self, *args):
        width = self.width_input.text.strip()
        height = self.height_input.text.strip()
        
        if not width or not height:
            self.show_error('Por favor, insira as dimensões')
            return
        
        try:
            width = int(width)
            height = int(height)
            
            self.app.change_screen_size(width, height)
            
            success_popup = Popup(
                title='Sucesso',
                content=Label(text="Tamanho da tela alterado com sucesso"),
                size_hint=(0.6, 0.3)
            )
            success_popup.open()
            
            self.dismiss()
            
        except ValueError:
            self.show_error('Por favor, insira números válidos para a largura e altura')
        except Exception as e:
            self.show_error(f'Erro ao alterar tamanho: {str(e)}')
    
    def show_error(self, message):
        error_popup = Popup(
            title='Erro',
            content=Label(text=message),
            size_hint=(0.6, 0.3)
        )
        error_popup.open()

# Screen to manage settings
class AdminSettingsScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.name = 'settings'
    
    def add_user(self):
        popup = AddUserPopup(Database())
        popup.open()
    
    def delete_manager(self):
        popup = DeleteManagerPopup()
        popup.open()
    
    def change_admin_data(self):
        popup = ChangeAdminDataPopup()
        popup.open()
    
    def change_screen_size(self):
        popup = ScreenSizePopup(self.app)
        popup.open()