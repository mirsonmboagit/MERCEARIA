"""
SCRIPT DE DIAGNÓSTICO - Código de Barras
Execute este script para verificar o que está acontecendo
"""

import sqlite3
from datetime import datetime

def diagnosticar_banco():
    """Verificar todos os produtos com código de barras"""
    try:
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        
        print("\n" + "="*80)
        print("🔍 DIAGNÓSTICO COMPLETO - CÓDIGOS DE BARRAS")
        print("="*80)
        
        # 1. Verificar estrutura da tabela
        print("\n1️⃣ ESTRUTURA DA TABELA PRODUCTS:")
        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"   Coluna: {col[1]:20s} | Tipo: {col[2]:10s} | Não-Nulo: {bool(col[3])}")
        
        # 2. Contar produtos com e sem barcode
        print("\n2️⃣ ESTATÍSTICAS DE CÓDIGO DE BARRAS:")
        
        cursor.execute("SELECT COUNT(*) FROM products")
        total = cursor.fetchone()[0]
        print(f"   Total de produtos: {total}")
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE barcode IS NOT NULL AND barcode != ''")
        with_barcode = cursor.fetchone()[0]
        print(f"   Com código de barras: {with_barcode}")
        print(f"   Sem código de barras: {total - with_barcode}")
        
        # 3. Listar TODOS os produtos com barcode
        print("\n3️⃣ PRODUTOS COM CÓDIGO DE BARRAS:")
        cursor.execute("""
            SELECT id, description, barcode, existing_stock, sale_price
            FROM products
            WHERE barcode IS NOT NULL AND barcode != ''
            ORDER BY id
        """)
        
        produtos = cursor.fetchall()
        
        if produtos:
            print(f"\n   Encontrados {len(produtos)} produto(s):\n")
            for p in produtos:
                barcode = p[2]
                print(f"   {'─'*76}")
                print(f"   ID: {p[0]}")
                print(f"   Nome: {p[1]}")
                print(f"   Código de Barras:")
                print(f"      - Original: '{barcode}'")
                print(f"      - Tamanho: {len(barcode)} caracteres")
                print(f"      - Representação: {repr(barcode)}")
                print(f"      - Bytes: {barcode.encode('utf-8')}")
                print(f"      - Limpo: '{barcode.strip()}'")
                print(f"   Estoque: {p[3]} unidades")
                print(f"   Preço: {p[4]:.2f} MZN")
        else:
            print("\n   ⚠️ NENHUM produto possui código de barras!")
            print("   AÇÃO NECESSÁRIA: Cadastre produtos com códigos de barras")
        
        # 4. Testar busca com códigos existentes
        if produtos:
            print("\n4️⃣ TESTE DE BUSCA:")
            for p in produtos:
                barcode = p[2]
                barcode_clean = barcode.strip()
                
                print(f"\n   Testando produto ID {p[0]}: {p[1]}")
                print(f"   Código: '{barcode_clean}'")
                
                # Teste 1: Busca exata
                cursor.execute("""
                    SELECT id, description FROM products 
                    WHERE barcode = ? AND existing_stock > 0
                """, (barcode_clean,))
                result = cursor.fetchone()
                
                if result:
                    print(f"   ✅ Busca EXATA: SUCESSO")
                else:
                    print(f"   ❌ Busca EXATA: FALHOU")
                    
                    # Teste 2: Busca com TRIM
                    cursor.execute("""
                        SELECT id, description FROM products 
                        WHERE TRIM(barcode) = ? AND existing_stock > 0
                    """, (barcode_clean,))
                    result = cursor.fetchone()
                    
                    if result:
                        print(f"   ✅ Busca com TRIM: SUCESSO")
                    else:
                        print(f"   ❌ Busca com TRIM: FALHOU")
                        print(f"   ⚠️ PROBLEMA DETECTADO: Código não é encontrável!")
        
        # 5. Verificar vendas recentes
        print("\n5️⃣ ÚLTIMAS TENTATIVAS DE VENDA:")
        cursor.execute("""
            SELECT id, product_id, quantity, sale_date 
            FROM sales 
            ORDER BY sale_date DESC 
            LIMIT 5
        """)
        vendas = cursor.fetchall()
        
        if vendas:
            print(f"   Últimas {len(vendas)} vendas:")
            for v in vendas:
                print(f"   - Venda ID {v[0]} | Produto ID {v[1]} | Qtd: {v[2]} | Data: {v[3]}")
        else:
            print("   Nenhuma venda registrada ainda")
        
        print("\n" + "="*80)
        print("✅ DIAGNÓSTICO COMPLETO")
        print("="*80 + "\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERRO NO DIAGNÓSTICO: {e}")
        import traceback
        traceback.print_exc()

def testar_codigo_manual():
    """Testar um código de barras manualmente"""
    print("\n" + "="*80)
    print("🧪 TESTE MANUAL DE CÓDIGO DE BARRAS")
    print("="*80)
    
    codigo = input("\nDigite o código de barras para testar: ").strip()
    
    if not codigo:
        print("❌ Código vazio!")
        return
    
    try:
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        
        print(f"\n📋 Código digitado: '{codigo}'")
        print(f"   Tamanho: {len(codigo)}")
        print(f"   Representação: {repr(codigo)}")
        print(f"   Bytes: {codigo.encode('utf-8')}")
        
        # Buscar
        cursor.execute("""
            SELECT id, description, barcode, existing_stock, sale_price
            FROM products
            WHERE barcode = ? AND existing_stock > 0
        """, (codigo,))
        
        result = cursor.fetchone()
        
        if result:
            print(f"\n✅ PRODUTO ENCONTRADO!")
            print(f"   ID: {result[0]}")
            print(f"   Nome: {result[1]}")
            print(f"   Código no BD: '{result[2]}'")
            print(f"   Estoque: {result[3]}")
            print(f"   Preço: {result[4]:.2f} MZN")
        else:
            print(f"\n❌ PRODUTO NÃO ENCONTRADO")
            print(f"\n   Comparando com códigos cadastrados:")
            
            cursor.execute("""
                SELECT id, description, barcode
                FROM products
                WHERE barcode IS NOT NULL AND barcode != ''
            """)
            todos = cursor.fetchall()
            
            for p in todos:
                db_code = p[2].strip() if p[2] else ""
                match = "✅ IGUAL" if db_code == codigo else "❌ DIFERENTE"
                
                print(f"\n   Produto ID {p[0]}: {p[1]}")
                print(f"      BD: '{db_code}' (len: {len(db_code)})")
                print(f"      Digitado: '{codigo}' (len: {len(codigo)})")
                print(f"      {match}")
                
                if db_code and codigo:
                    if len(db_code) == len(codigo):
                        for i, (c1, c2) in enumerate(zip(db_code, codigo)):
                            if c1 != c2:
                                print(f"      Diferença na posição {i}: '{c1}'(ord:{ord(c1)}) vs '{c2}'(ord:{ord(c2)})")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🔬 SISTEMA DE DIAGNÓSTICO DE CÓDIGO DE BARRAS")
    print("="*80)
    
    while True:
        print("\nEscolha uma opção:")
        print("1 - Diagnóstico completo do banco")
        print("2 - Testar código de barras manualmente")
        print("3 - Sair")
        
        opcao = input("\nOpção: ").strip()
        
        if opcao == "1":
            diagnosticar_banco()
        elif opcao == "2":
            testar_codigo_manual()
        elif opcao == "3":
            print("\n👋 Encerrando...\n")
            break
        else:
            print("\n❌ Opção inválida!")