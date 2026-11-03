class Produto:
    def __init__(self, id_produto, nome, preco, quantidade):
        self.id_produto = id_produto
        self.nome = nome
        self.preco = preco
        self.quantidade = quantidade

    def exibir(self):
        return "ID: " + str(self.id_produto) + " | Produto: " + self.nome + " | R$ " + str(self.preco) + " | Estoque: " + str(self.quantidade)

class Estoque:
    def __init__(self):
        self.produtos = []

    def cadastrar(self, produto):
        self.produtos.append(produto)
        print("Produto cadastrado com sucesso!")

    def listar(self):
        print("\n--- LISTA DE PRODUTOS ---")
        for p in self.produtos:
            print(p.exibir())
        print("-------------------------")

    def atualizar(self, id_produto, novo_preco, nova_qtd):
        for p in self.produtos:
            if p.id_produto == id_produto:
                p.preco = novo_preco
                p.quantidade = nova_qtd
                print("Produto atualizado!")
                return
        print("Produto nao encontrado.")

    def remover(self, id_produto):
        for p in self.produtos:
            if p.id_produto == id_produto:
                self.produtos.remove(p)
                print("Produto removido do sistema!")
                return
        print("Produto nao encontrado.")

    def buscar(self, id_produto):
        for p in self.produtos:
            if p.id_produto == id_produto:
                return p
        return None

class Venda:
    def __init__(self, id_venda):
        self.id_venda = id_venda
        self.itens = []
        self.total = 0.0

    def adicionar_item(self, produto, qtd):
        if produto.quantidade >= qtd:
            produto.quantidade = produto.quantidade - qtd
            subtotal = produto.preco * qtd
            self.itens.append({"nome": produto.nome, "qtd": qtd, "subtotal": subtotal})
            self.total = self.total + subtotal
            print("Item adicionado na venda!")
        else:
            print("Erro: Estoque insuficiente.")

    def fechar_venda(self):
        print("\n--- CUPOM FISCAL ---")
        print("Venda ID: " + str(self.id_venda))
        for item in self.itens:
            print("Item: " + item['nome'] + " | Qtd: " + str(item['qtd']) + " | Subtotal: R$ " + str(item['subtotal']))
        print("TOTAL A PAGAR: R$ " + str(self.total))
        print("--------------------\n")

def menu():
    estoque = Estoque()
    venda_atual = None

    while True:
        print("\n=== MENU DO SISTEMA ===")
        print("1. Cadastrar Produto")
        print("2. Listar Produtos")
        print("3. Atualizar Produto")
        print("4. Remover Produto")
        print("5. Iniciar Nova Venda")
        print("6. Adicionar Item na Venda")
        print("7. Fechar Venda Atual")
        print("0. Sair")

        opcao = input("Escolha uma opcao: ")

        if opcao == "1":
            id_p = int(input("ID do produto: "))
            nome = input("Nome do produto: ")
            preco = float(input("Preco: "))
            qtd = int(input("Quantidade no estoque: "))
            produto = Produto(id_p, nome, preco, qtd)
            estoque.cadastrar(produto)
            
        elif opcao == "2":
            estoque.listar()
            
        elif opcao == "3":
            id_p = int(input("ID do produto a atualizar: "))
            novo_preco = float(input("Novo preco: "))
            nova_qtd = int(input("Nova quantidade: "))
            estoque.atualizar(id_p, novo_preco, nova_qtd)
            
        elif opcao == "4":
            id_p = int(input("ID do produto a remover: "))
            estoque.remover(id_p)
            
        elif opcao == "5":
            id_v = int(input("ID da venda: "))
            venda_atual = Venda(id_v)
            print("Venda iniciada. Agora adicione os itens.")
            
        elif opcao == "6":
            if venda_atual == None:
                print("Você precisa iniciar uma venda primeiro (Opção 5).")
            else:
                id_p = int(input("ID do produto desejado: "))
                prod = estoque.buscar(id_p)
                if prod != None:
                    qtd = int(input("Quantidade: "))
                    venda_atual.adicionar_item(prod, qtd)
                else:
                    print("Produto não cadastrado.")
                    
        elif opcao == "7":
            if venda_atual != None:
                venda_atual.fechar_venda()
                venda_atual = None
            else:
                print("Nenhuma venda aberta.")
                
        elif opcao == "0":
            print("Saindo do sistema...")
            break
            
        else:
            print("Opcao invalida. Digite um numero do menu.")
            
menu()
