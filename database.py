import sqlite3
import os
from datetime import datetime
import bcrypt

class Database:
    def __init__(self, db_name="inventory.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.setup()
    
    def connect(self):
        """Conectar ao banco de dados"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
    
    def close(self):
        """Fechar a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
    
    def setup(self):
        """Configurar tabelas do banco de dados"""
        try:
            # Tabela de usuários (administrador e gerente)
            self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )''')
            
            # Adicionar usuário padrão se não existir
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            if self.cursor.fetchone()[0] == 0:
                # Hash da senha padrão "123456"
                default_password = bcrypt.hashpw("123456".encode('utf-8'), bcrypt.gensalt())
                self.cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    ("admin", default_password, "admin")
                )
            
            # Tabela de produtos (atualizada com barcode, expiry_date, weight_kg e is_sold_by_weight)
            self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                category TEXT,
                existing_stock REAL NOT NULL,
                sold_stock REAL DEFAULT 0,
                sale_price REAL NOT NULL,
                total_purchase_price REAL NOT NULL,
                unit_purchase_price REAL NOT NULL,
                profit_per_unit REAL NOT NULL,
                barcode TEXT,
                expiry_date TEXT,
                date_added TEXT NOT NULL,
                is_sold_by_weight INTEGER DEFAULT 0
            )''')
            
            # Verificar e adicionar colunas necessárias
            self.cursor.execute("PRAGMA table_info(products)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            if 'is_sold_by_weight' not in columns:
                print("⚙️ Adicionando coluna 'is_sold_by_weight' à tabela products...")
                self.cursor.execute("ALTER TABLE products ADD COLUMN is_sold_by_weight INTEGER DEFAULT 0")
                print("✅ Coluna 'is_sold_by_weight' adicionada com sucesso!")
            
            # Tabela de vendas (atualizada para aceitar quantidades decimais)
            self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY,
                product_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                sale_price REAL NOT NULL,
                total_price REAL NOT NULL,
                sale_date TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )''')
            
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao configurar o banco de dados: {e}")
    
    def validate_user(self, username, password):
        """Validar credenciais do usuário usando hashing"""
        try:
            self.cursor.execute(
                "SELECT password, role FROM users WHERE username = ?", (username,)
            )
            result = self.cursor.fetchone()
            if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
                return result[1]  # Retorna a role do usuário
            return None
        except sqlite3.Error as e:
            print(f"Erro ao validar usuário: {e}")
            return None
    
    # ==================== MÉTODOS PARA PRODUTOS ====================
    
    def add_product(self, description, category, existing_stock, sold_stock, sale_price, total_purchase_price, unit_purchase_price, barcode=None, expiry_date=None, is_sold_by_weight=False):
        """Adicionar um novo produto ao banco de dados"""
        try:
            profit_per_unit = sale_price - unit_purchase_price
            date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
            self.cursor.execute(''' 
            INSERT INTO products (description, category, existing_stock, sold_stock, sale_price, total_purchase_price, unit_purchase_price, profit_per_unit, barcode, expiry_date, date_added, is_sold_by_weight)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
            ''', (description, category, existing_stock, sold_stock, sale_price, total_purchase_price, unit_purchase_price, profit_per_unit, barcode, expiry_date, date_added, 1 if is_sold_by_weight else 0))
            
            self.conn.commit()
            print(f"✅ Produto adicionado com sucesso! ID: {self.cursor.lastrowid}")
        except sqlite3.Error as e:
            print(f"Erro ao adicionar produto: {e}")
    
    def update_product(self, id, description, category, existing_stock, sold_stock, sale_price, total_purchase_price, unit_purchase_price, barcode=None, expiry_date=None, is_sold_by_weight=False):
        """Atualizar produto existente"""
        try:
            profit_per_unit = sale_price - unit_purchase_price
            self.cursor.execute(
                """UPDATE products SET 
                   description = ?, category = ?, existing_stock = ?, sold_stock = ?, 
                   sale_price = ?, total_purchase_price = ?, unit_purchase_price = ?, 
                   profit_per_unit = ?, barcode = ?, expiry_date = ?, is_sold_by_weight = ?
                   WHERE id = ?""", 
                (description, category, existing_stock, sold_stock, sale_price, 
                 total_purchase_price, unit_purchase_price, profit_per_unit, barcode, expiry_date, 1 if is_sold_by_weight else 0, id)
            )
            self.conn.commit()
            print(f"✅ Produto {id} atualizado com sucesso!")
        except sqlite3.Error as e:
            print(f"Erro ao atualizar produto: {e}")
    
    def delete_product(self, id):
        """Excluir produto"""
        try:
            self.cursor.execute("DELETE FROM products WHERE id = ?", (id,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao excluir produto: {e}")
    
    def get_all_products(self):
        """Obter todos os produtos"""
        try:
            self.cursor.execute(""" 
                SELECT 
                    p.id,                           -- 0
                    p.description,                  -- 1
                    p.existing_stock,               -- 2
                    p.sold_stock,                   -- 3
                    p.sale_price,                   -- 4
                    p.total_purchase_price,         -- 5
                    p.unit_purchase_price,          -- 6
                    p.profit_per_unit,              -- 7
                    (p.profit_per_unit * p.sold_stock) as total_profit,  -- 8
                    CASE 
                        WHEN p.sold_stock > 0 THEN (p.profit_per_unit * p.sold_stock * 100) / (p.unit_purchase_price * p.sold_stock)
                        ELSE 0 
                    END as profit_percentage,       -- 9
                    (p.sale_price - p.unit_purchase_price) / p.unit_purchase_price * 100 as price_percentage,  -- 10
                    p.category,                     -- 11
                    p.barcode,                      -- 12
                    p.expiry_date,                  -- 13
                    p.date_added,                   -- 14
                    p.is_sold_by_weight             -- 15 (NOVO)
                FROM products p
                ORDER BY p.id DESC
            """)
            results = self.cursor.fetchall()
            
            if results:
                print(f"\n📊 DEBUG get_all_products:")
                print(f"   - Total de produtos: {len(results)}")
                print(f"   - Colunas por produto: {len(results[0])}")
                print(f"   - Primeiro produto (ID {results[0][0]}): {results[0][1]}")
                print(f"   - Vendido por peso: {'Sim' if results[0][15] else 'Não'}")
            
            return results
        except sqlite3.Error as e:
            print(f"Erro ao obter produtos: {e}")
            return []
    
    def get_product(self, id):
        """Obter um produto específico"""
        try:
            self.cursor.execute(""" 
                SELECT 
                    p.id, p.description, p.existing_stock, p.sold_stock, 
                    p.sale_price, p.total_purchase_price, p.unit_purchase_price, 
                    p.profit_per_unit,
                    (p.profit_per_unit * p.sold_stock) as total_profit,
                    CASE 
                        WHEN p.sold_stock > 0 THEN (p.profit_per_unit * p.sold_stock * 100) / (p.unit_purchase_price * p.sold_stock)
                        ELSE 0 
                    END as profit_percentage,
                    (p.sale_price - p.unit_purchase_price) / p.unit_purchase_price * 100 as price_percentage,
                    p.category,
                    p.barcode,
                    p.expiry_date,
                    p.date_added,
                    p.is_sold_by_weight
                FROM products p
                WHERE p.id = ?""", (id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erro ao obter produto: {e}")
            return None
    
    def get_products_for_sale(self):
        """Obter produtos disponíveis para venda"""
        try:
            self.cursor.execute(""" 
                SELECT id, description, existing_stock, sale_price, barcode, is_sold_by_weight
                FROM products
                WHERE existing_stock > 0
                ORDER BY description ASC
            """)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao obter produtos para venda: {e}")
            return []
    
    def get_products_by_weight(self):
        """Obter apenas produtos vendidos por peso (kg)"""
        try:
            self.cursor.execute(""" 
                SELECT 
                    p.id, p.description, p.existing_stock, p.sold_stock, 
                    p.sale_price, p.total_purchase_price, p.unit_purchase_price, 
                    p.profit_per_unit,
                    (p.profit_per_unit * p.sold_stock) as total_profit,
                    CASE 
                        WHEN p.sold_stock > 0 THEN (p.profit_per_unit * p.sold_stock * 100) / (p.unit_purchase_price * p.sold_stock)
                        ELSE 0 
                    END as profit_percentage,
                    (p.sale_price - p.unit_purchase_price) / p.unit_purchase_price * 100 as price_percentage,
                    p.category,
                    p.barcode,
                    p.expiry_date,
                    p.date_added,
                    p.is_sold_by_weight
                FROM products p
                WHERE p.is_sold_by_weight = 1
                ORDER BY p.description ASC
            """)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao obter produtos por peso: {e}")
            return []
    
    def get_product_by_barcode(self, barcode):
        """Buscar produto pelo código de barras - VERSÃO ROBUSTA"""
        try:
            barcode_clean = barcode.strip() if barcode else ""
            
            print(f"\n🔍 DB: Buscando código de barras...")
            print(f"   Código recebido: '{barcode}' (tamanho: {len(barcode)})")
            print(f"   Código limpo: '{barcode_clean}' (tamanho: {len(barcode_clean)})")
            
            if not barcode_clean:
                print(f"   ⚠️ Código vazio após limpeza!")
                return None
            
            # ESTRATÉGIA 1: Busca EXATA
            self.cursor.execute(""" 
                SELECT id, description, existing_stock, sale_price, barcode, is_sold_by_weight
                FROM products
                WHERE barcode = ? AND existing_stock > 0
            """, (barcode_clean,))
            
            result = self.cursor.fetchone()
            
            if result:
                print(f"✅ Encontrado com busca EXATA!")
                print(f"   ID: {result[0]} | Nome: {result[1]}")
                print(f"   Vendido por peso: {'Sim' if result[5] else 'Não'}")
                return result
            
            # ESTRATÉGIA 2: Busca com TRIM
            self.cursor.execute(""" 
                SELECT id, description, existing_stock, sale_price, barcode, is_sold_by_weight
                FROM products
                WHERE TRIM(barcode) = ? AND existing_stock > 0
            """, (barcode_clean,))
            
            result = self.cursor.fetchone()
            
            if result:
                print(f"✅ Encontrado com busca TRIM!")
                print(f"   ID: {result[0]} | Nome: {result[1]}")
                print(f"   Vendido por peso: {'Sim' if result[5] else 'Não'}")
                return result
            
            # ESTRATÉGIA 3: Busca case-insensitive
            self.cursor.execute(""" 
                SELECT id, description, existing_stock, sale_price, barcode, is_sold_by_weight
                FROM products
                WHERE LOWER(TRIM(barcode)) = LOWER(?) AND existing_stock > 0
            """, (barcode_clean,))
            
            result = self.cursor.fetchone()
            
            if result:
                print(f"✅ Encontrado com busca case-insensitive!")
                print(f"   ID: {result[0]} | Nome: {result[1]}")
                print(f"   Vendido por peso: {'Sim' if result[5] else 'Não'}")
                return result
            
            print(f"\n❌ Código '{barcode_clean}' NÃO ENCONTRADO")
            return None
            
        except sqlite3.Error as e:
            print(f"❌ Erro SQL ao buscar código de barras: {e}")
            return None
        except Exception as e:
            print(f"❌ Erro geral ao buscar código de barras: {e}")
            return None
    
    # ==================== MÉTODOS PARA VENDAS ====================
    
    def add_sale(self, product_id, quantity, sale_price):
        """Adicionar nova venda (aceita quantidades decimais para produtos por kg)"""
        try:
            total_price = quantity * sale_price
            sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Atualizar estoque e vendidos do produto
            self.cursor.execute(
                "UPDATE products SET existing_stock = existing_stock - ?, sold_stock = sold_stock + ? WHERE id = ?",
                (quantity, quantity, product_id)
            )
            
            # Registrar a venda
            self.cursor.execute(
                "INSERT INTO sales (product_id, quantity, sale_price, total_price, sale_date) VALUES (?, ?, ?, ?, ?)",
                (product_id, quantity, sale_price, total_price, sale_date)
            )
            
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao adicionar venda: {e}")
            return None
    
    def get_all_sales(self):
        """Obter todas as vendas"""
        try:
            self.cursor.execute(""" 
                SELECT s.id, p.description, s.quantity, s.sale_price, s.total_price, s.sale_date
                FROM sales s
                JOIN products p ON s.product_id = p.id
                ORDER BY s.sale_date DESC
            """)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao obter vendas: {e}")
            return []
    
    def get_sales_by_date(self, date_str):
        """Buscar vendas por data específica"""
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            formatted_date = date_obj.strftime("%Y-%m-%d")
            
            self.cursor.execute("""
                SELECT s.id, p.description, s.quantity, s.sale_price, s.total_price, s.sale_date
                FROM sales s
                JOIN products p ON s.product_id = p.id
                WHERE DATE(s.sale_date) = ?
                ORDER BY s.sale_date DESC
            """, (formatted_date,))
            
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar vendas por data: {e}")
            return []

    def get_sales_by_date_range(self, start_date, end_date):
        """Buscar vendas por período (intervalo de datas)"""
        try:
            start_obj = datetime.strptime(start_date, "%d/%m/%Y")
            end_obj = datetime.strptime(end_date, "%d/%m/%Y")
            
            formatted_start = start_obj.strftime("%Y-%m-%d")
            formatted_end = end_obj.strftime("%Y-%m-%d")
            
            self.cursor.execute("""
                SELECT s.id, p.description, s.quantity, s.sale_price, s.total_price, s.sale_date
                FROM sales s
                JOIN products p ON s.product_id = p.id
                WHERE DATE(s.sale_date) BETWEEN ? AND ?
                ORDER BY s.sale_date DESC
            """, (formatted_start, formatted_end))
            
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar vendas por período: {e}")
            return []

    def get_sales_by_month(self, month, year):
        """Buscar vendas por mês específico"""
        try:
            self.cursor.execute("""
                SELECT s.id, p.description, s.quantity, s.sale_price, s.total_price, s.sale_date
                FROM sales s
                JOIN products p ON s.product_id = p.id
                WHERE strftime('%m', s.sale_date) = ? AND strftime('%Y', s.sale_date) = ?
                ORDER BY s.sale_date DESC
            """, (f"{month:02d}", str(year)))
            
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar vendas por mês: {e}")
            return []

    def get_sales_by_year(self, year):
        """Buscar vendas por ano específico"""
        try:
            self.cursor.execute("""
                SELECT s.id, p.description, s.quantity, s.sale_price, s.total_price, s.sale_date
                FROM sales s
                JOIN products p ON s.product_id = p.id
                WHERE strftime('%Y', s.sale_date) = ?
                ORDER BY s.sale_date DESC
            """, (str(year),))
            
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar vendas por ano: {e}")
            return []

    def get_today_sales(self):
        """Buscar vendas de hoje"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            self.cursor.execute("""
                SELECT s.id, p.description, s.quantity, s.sale_price, s.total_price, s.sale_date
                FROM sales s
                JOIN products p ON s.product_id = p.id
                WHERE DATE(s.sale_date) = ?
                ORDER BY s.sale_date DESC
            """, (today,))
            
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar vendas de hoje: {e}")
            return []

    def get_sales_statistics_by_date(self, date_str):
        """Obter estatísticas de vendas por data específica"""
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            formatted_date = date_obj.strftime("%Y-%m-%d")
            
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(s.quantity) as total_quantity,
                    SUM(s.total_price) as total_revenue,
                    AVG(s.total_price) as average_sale,
                    MIN(s.total_price) as min_sale,
                    MAX(s.total_price) as max_sale
                FROM sales s
                WHERE DATE(s.sale_date) = ?
            """, (formatted_date,))
            
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter estatísticas por data: {e}")
            return None

    def get_monthly_sales_summary(self, month, year):
        """Obter resumo de vendas mensais"""
        try:
            self.cursor.execute("""
                SELECT 
                    DATE(s.sale_date) as date,
                    COUNT(*) as daily_sales,
                    SUM(s.quantity) as daily_quantity,
                    SUM(s.total_price) as daily_revenue
                FROM sales s
                WHERE strftime('%m', s.sale_date) = ? AND strftime('%Y', s.sale_date) = ?
                GROUP BY DATE(s.sale_date)
                ORDER BY DATE(s.sale_date) DESC
            """, (f"{month:02d}", str(year)))
            
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter resumo mensal: {e}")
            return []
    
    # ==================== MÉTODOS PARA GERENTES ====================

    def get_all_managers(self):
        """Obter todos os gerentes"""
        try:
            self.cursor.execute("SELECT username FROM users WHERE role = 'manager'")
            return [manager[0] for manager in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Erro ao buscar gerentes: {e}")
            return []
    
    def delete_manager(self, username):
        """Excluir um gerente específico"""
        try:
            self.cursor.execute("SELECT username FROM users WHERE role = 'manager'")
            current_managers = self.cursor.fetchall()
            
            self.cursor.execute(
                "SELECT id FROM users WHERE username = ? AND role = 'manager'", 
                (username,)
            )
            manager = self.cursor.fetchone()
            
            if not manager:
                return False, "Gerente não encontrado"
            
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'manager'")
            manager_count = self.cursor.fetchone()[0]
            
            if manager_count <= 1:
                return False, "Não é possível excluir o último gerente"
            
            self.cursor.execute(
                "DELETE FROM users WHERE username = ? AND role = 'manager'", 
                (username,)
            )
            self.conn.commit()
            
            return True, "Gerente excluído com sucesso"
        
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Erro ao excluir gerente: {str(e)}"
        except Exception as e:
            self.conn.rollback()
            return False, f"Erro inesperado: {str(e)}"
    
    # ==================== CONTEXT MANAGER ====================
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()