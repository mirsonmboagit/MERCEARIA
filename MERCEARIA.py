import os
import sys

# Para Windows - define o ícone da aplicação na barra de tarefas
if sys.platform.startswith('win'):
    try:
        import ctypes
        # Define o AppUserModelID para aparecer como aplicação separada
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('MerceariaApp.SistemaEstoque.1.0')
        
        # Define o ícone da janela
        if os.path.exists('icon4.ico'):
            import ctypes.wintypes
            # Carrega o ícone
            icon_path = os.path.abspath('icon4.ico')
            ctypes.windll.shell32.ExtractIconW.argtypes = [ctypes.wintypes.HINSTANCE, ctypes.wintypes.LPCWSTR, ctypes.wintypes.UINT]
            ctypes.windll.shell32.ExtractIconW.restype = ctypes.wintypes.HICON
    except:
        pass  # Se der erro, continua sem o ícone

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.config import Config

# Configurações do ícone antes de outros imports do Kivy
Config.set('kivy', 'window_icon', 'icon4.ico')

from database import Database
from admin import AdminScreen
from manager import ModernSalesScreen
from login import LoginScreen
from reports_screen import ReportsScreen
from settings import AdminSettingsScreen

# Define o tamanho da janela
Window.size = (1120, 680)

# Impede que a janela seja redimensionada para menos do que isso
Window.minimum_width = 1120
Window.minimum_height = 680

# Inicializa o banco de dados
db = Database()
db.setup()

class MainApp(App):
    def build(self):
        # Define o título da janela
        self.title = 'Sistema de Controle de Estoque - MERCEARIA'
        
        # Define o ícone da aplicação
        self.icon = 'icon4.ico'

        # Cria o gerenciador de telas
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(AdminScreen(name='admin'))
        sm.add_widget(AdminSettingsScreen(app=self, name='settings'))  # Adiciona a tela de configurações
        sm.add_widget(ManagerScreen(name='manager'))
        sm.add_widget(ReportsScreen(name='reports'))
        
        return sm
    
    def on_start(self):
        """Configurações adicionais após iniciar a aplicação"""
        # Reforça o título da janela
        Window.set_title('MERCEARIA')
        
        # Define o ícone programaticamente se o arquivo existir
        if os.path.exists('icon4.ico'):
            Window.set_icon('icon4.ico')
    
    def change_screen_size(self, width, height):
        """
        Altera o tamanho da janela do aplicativo
        
        Args:
            width (int): Largura da janela em pixels
            height (int): Altura da janela em pixels
        """
        try:
            if width < 1120 or height < 680:
                raise ValueError("Tamanho mínimo permitido é 1120x680.")

            Window.size = (int(width), int(height))
            Window.minimum_width = int(width)
            Window.minimum_height = int(height)

            return True
        except Exception as e:
            raise Exception(f"Erro ao alterar tamanho da janela: {str(e)}")

if __name__ == '__main__':
    MainApp().run()