"""Interface Tkinter do Sistema Desktop de Gestão e Caixa."""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import messagebox, simpledialog

from sistema_bd import EstoqueBD, Funcionario, Gerente, Venda, VendasBD


BG_SISTEMA = "#121214"
BG_OPCOES = "#202024"
COR_TITULO = "#FFFFFF"
COR_SUBTITULO = "#A8A8B3"
COR_BORDA = "#323238"
COR_DESTAQUE_VERDE = "#04D361"
COR_DESTAQUE_LARANJA = "#EF760B"
COR_PERIGO_VERMELHO = "#A60000"
SENHA_ADMIN = os.environ.get("GESTAO_CAIXA_ADMIN_PIN", "1234")


def criar_botao(parent, texto, cor_fundo, comando, largura=35, cor_texto=COR_TITULO):
    """Cria os botões padronizados da interface."""
    frame_borda = tk.Frame(parent, bg=COR_BORDA, padx=2, pady=2)
    botao = tk.Button(
        frame_borda,
        text=texto,
        font=("Arial", 14, "bold"),
        bg=cor_fundo,
        fg=cor_texto,
        width=largura,
        height=2,
        relief="flat",
        activebackground=cor_fundo,
        activeforeground=cor_texto,
        command=comando,
    )
    botao.pack(fill="both", expand=True)
    return frame_borda


class GestaoCaixaApp(tk.Tk):
    """Controla a navegação e mantém as dependências usadas pelas telas."""

    def __init__(self):
        super().__init__()
        self.title("Sistema Gestão de Caixa - PDV")
        self.geometry("1366x768")
        self.minsize(1000, 650)
        self.configure(bg=BG_SISTEMA)

        self.estoque_db = EstoqueBD()
        self.vendas_db = VendasBD(self.estoque_db.nome_banco)
        self.usuario = None
        self.venda_atual = None

        self.container = tk.Frame(self, bg=BG_SISTEMA)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for classe in (LoginFrame, AdminFrame, FuncionarioFrame, VendaFrame):
            frame = classe(self.container, self)
            self.frames[classe] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.mostrar_frame(LoginFrame)

    def mostrar_frame(self, classe_frame):
        frame = self.frames[classe_frame]
        frame.tkraise()
        if classe_frame is VendaFrame:
            frame.preparar_nova_venda()

    def iniciar_venda(self):
        self.venda_atual = Venda()
        self.mostrar_frame(VendaFrame)

    def sair(self):
        self.usuario = None
        self.venda_atual = None
        self.mostrar_frame(LoginFrame)


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_SISTEMA)
        self.controller = controller

        painel = tk.Frame(self, bg=BG_OPCOES, highlightbackground=COR_BORDA, highlightthickness=2)
        painel.place(relx=0.5, rely=0.5, anchor="center", width=600, height=450)

        tk.Label(
            painel, text="SELECIONE SEU ACESSO", font=("Arial", 26, "bold"),
            bg=BG_OPCOES, fg=COR_TITULO,
        ).pack(pady=(50, 10))
        tk.Label(
            painel, text="Escolha seu perfil para iniciar o sistema",
            font=("Arial", 12), bg=BG_OPCOES, fg=COR_SUBTITULO,
        ).pack(pady=(0, 40))

        criar_botao(
            painel, "ADMINISTRADOR / GERENTE", COR_DESTAQUE_LARANJA, self.acesso_admin
        ).pack(pady=15)
        criar_botao(
            painel, "FUNCIONÁRIO (CAIXA)", COR_DESTAQUE_VERDE, self.acesso_funcionario
        ).pack(pady=15)

    def acesso_admin(self):
        senha = simpledialog.askstring("Segurança", "Digite a senha (Admin):", show="*")
        if senha == SENHA_ADMIN:
            self.controller.usuario = Gerente()
            self.controller.mostrar_frame(AdminFrame)
        elif senha is not None:
            messagebox.showerror("Erro", "Senha incorreta!")

    def acesso_funcionario(self):
        self.controller.usuario = Funcionario()
        self.controller.mostrar_frame(FuncionarioFrame)


class AdminFrame(tk.Frame):
    """Tela de administração; as regras de estoque ficam no repositório."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_SISTEMA)
        self.controller = controller

        painel = tk.Frame(self, bg=BG_OPCOES, highlightbackground=COR_BORDA, highlightthickness=2)
        painel.place(relx=0.5, rely=0.5, anchor="center", width=700, height=850)

        tk.Label(
            painel, text="PAINEL ADMINISTRATIVO", font=("Arial", 26, "bold"),
            bg=BG_OPCOES, fg=COR_DESTAQUE_LARANJA,
        ).pack(pady=(40, 10))
        tk.Label(
            painel, text="Gerenciamento de Estoque e Relatórios",
            font=("Arial", 12), bg=BG_OPCOES, fg=COR_SUBTITULO,
        ).pack(pady=(0, 30))

        botoes = [
            ("1. Criar Produto", self.criar),
            ("2. Listar Produtos em Estoque", self.listar),
            ("3. Atualizar Produto", self.atualizar),
            ("4. Deletar Produto", self.deletar),
            ("5. Relatório de Vendas do Dia", self.relatorio),
        ]
        for texto, comando in botoes:
            cor_texto = COR_PERIGO_VERMELHO if texto.startswith("4.") else COR_TITULO
            criar_botao(
                painel, texto, BG_SISTEMA, comando, cor_texto=cor_texto
            ).pack(pady=10)

        criar_botao(
            painel, "INICIAR NOVA VENDA (Admin)", COR_DESTAQUE_LARANJA,
            controller.iniciar_venda,
        ).pack(pady=15)
        criar_botao(
            painel, "SAIR (Trocar Usuário)", COR_PERIGO_VERMELHO, controller.sair
        ).pack(pady=15)

    def _gerente_autorizado(self):
        usuario = self.controller.usuario
        if usuario is None or not usuario.pode_gerenciar_estoque():
            messagebox.showerror("Acesso negado", "Esta operação é exclusiva do gerente.")
            return False
        return True

    def criar(self):
        if not self._gerente_autorizado():
            return
        nome = simpledialog.askstring("Novo produto", "Nome do produto:")
        if not nome or not nome.strip():
            return
        preco = simpledialog.askfloat("Novo produto", "Preço (R$):", minvalue=0)
        if preco is None:
            return
        qtd = simpledialog.askinteger("Novo produto", "Quantidade em estoque:", minvalue=0)
        if qtd is None:
            return
        try:
            id_produto = self.controller.estoque_db.cadastrar(nome, preco, qtd)
        except ValueError as erro:
            messagebox.showerror("Dados inválidos", str(erro))
            return
        messagebox.showinfo("Produto cadastrado", f"Produto cadastrado com ID {id_produto:02d}.")

    def listar(self):
        if not self._gerente_autorizado():
            return
        produtos = self.controller.estoque_db.listar_produtos()
        if not produtos:
            messagebox.showinfo("Estoque", "O estoque está vazio.")
            return
        texto = "=== PRODUTOS NO ESTOQUE ===\n\n"
        for produto in produtos:
            texto += (
                f"ID: {produto.id:02d} | {produto.nome} | "
                f"R$ {produto.preco:.2f} | Estoque: {produto.quantidade} un\n"
            )
        messagebox.showinfo("Listagem de estoque", texto)

    def atualizar(self):
        if not self._gerente_autorizado():
            return
        id_produto = simpledialog.askinteger("Atualizar", "ID do produto:", minvalue=1)
        if id_produto is None:
            return
        preco = simpledialog.askfloat("Atualizar", "Novo preço (R$):", minvalue=0)
        if preco is None:
            return
        qtd = simpledialog.askinteger("Atualizar", "Nova quantidade:", minvalue=0)
        if qtd is None:
            return
        try:
            sucesso = self.controller.estoque_db.atualizar(id_produto, preco, qtd)
        except ValueError as erro:
            messagebox.showerror("Dados inválidos", str(erro))
            return
        if sucesso:
            messagebox.showinfo("Produto atualizado", "Alterações salvas com sucesso.")
        else:
            messagebox.showwarning("Não encontrado", "Produto não encontrado.")

    def deletar(self):
        if not self._gerente_autorizado():
            return
        id_produto = simpledialog.askinteger("Excluir", "ID do produto:", minvalue=1)
        if id_produto is None:
            return
        if self.controller.estoque_db.deletar(id_produto):
            messagebox.showinfo("Produto excluído", "Produto removido do estoque.")
        else:
            messagebox.showwarning("Não encontrado", "Produto não encontrado.")

    def relatorio(self):
        if not self._gerente_autorizado():
            return
        resumo = self.controller.vendas_db.resumo_dia()
        texto = (
            "=== FECHAMENTO DO DIA ===\n\n"
            f"Quantidade de vendas: {resumo['quantidade_vendas']}\n"
            f"Total arrecadado: R$ {resumo['total_arrecadado']:.2f}\n\n"
        )
        if resumo["vendas"]:
            texto += "Vendas registradas:\n"
            for id_venda, total, _data in resumo["vendas"]:
                texto += f"Venda #{id_venda:02d}: R$ {total:.2f}\n"
        else:
            texto += "Nenhuma venda registrada hoje."
        messagebox.showinfo("Relatório diário", texto)


class FuncionarioFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_SISTEMA)
        self.controller = controller

        painel = tk.Frame(self, bg=BG_OPCOES, highlightbackground=COR_BORDA, highlightthickness=2)
        painel.place(relx=0.5, rely=0.5, anchor="center", width=600, height=450)

        tk.Label(
            painel, text="ÁREA DO FUNCIONÁRIO", font=("Arial", 26, "bold"),
            bg=BG_OPCOES, fg=COR_DESTAQUE_VERDE,
        ).pack(pady=(60, 10))
        tk.Label(
            painel, text="Terminal de Caixa", font=("Arial", 12),
            bg=BG_OPCOES, fg=COR_SUBTITULO,
        ).pack(pady=(0, 40))

        criar_botao(
            painel, "INICIAR NOVA VENDA", COR_DESTAQUE_VERDE, controller.iniciar_venda
        ).pack(pady=20)
        criar_botao(
            painel, "SAIR", COR_PERIGO_VERMELHO, controller.sair, largura=20
        ).pack(pady=20)


class VendaFrame(tk.Frame):
    """A tela coleta entradas e exibe a Venda; não calcula nem altera o estoque."""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_SISTEMA)
        self.controller = controller

        painel = tk.Frame(self, bg=BG_OPCOES, highlightbackground=COR_BORDA, highlightthickness=2)
        painel.place(relx=0.5, rely=0.5, anchor="center", width=1000, height=800)

        self.lbl_titulo = tk.Label(
            painel, text="NOVA VENDA", font=("Arial", 28, "bold"),
            bg=BG_OPCOES, fg=COR_TITULO,
        )
        self.lbl_titulo.pack(pady=(30, 5))
        tk.Label(
            painel, text="Detalhes do carrinho", font=("Arial", 12),
            bg=BG_OPCOES, fg=COR_SUBTITULO,
        ).pack(pady=(0, 20))

        frame_lista = tk.Frame(painel, bg=COR_BORDA, padx=2, pady=2)
        frame_lista.pack(pady=10)
        self.lista = tk.Listbox(
            frame_lista, font=("Courier", 16), width=70, height=14,
            bg=BG_SISTEMA, fg=COR_TITULO, relief="flat", highlightthickness=0,
        )
        self.lista.pack()

        self.lbl_total = tk.Label(
            painel, text="TOTAL: R$ 0.00", font=("Arial", 26, "bold"),
            bg=BG_OPCOES, fg=COR_DESTAQUE_VERDE,
        )
        self.lbl_total.pack(pady=25)

        frame_botoes = tk.Frame(painel, bg=BG_OPCOES)
        frame_botoes.pack(pady=10)
        criar_botao(
            frame_botoes, "Adicionar Produto", BG_SISTEMA, self.add_produto, largura=20
        ).grid(row=0, column=0, padx=15)
        criar_botao(
            frame_botoes, "FECHAR VENDA", COR_DESTAQUE_VERDE, self.fechar_venda, largura=20
        ).grid(row=0, column=1, padx=15)
        criar_botao(
            frame_botoes, "CANCELAR VENDA", COR_PERIGO_VERMELHO,
            self.cancelar_venda, largura=20,
        ).grid(row=0, column=2, padx=15)

    def preparar_nova_venda(self):
        venda = self.controller.venda_atual
        if venda is None:
            self.controller.venda_atual = Venda()
            venda = self.controller.venda_atual
        proximo_id = self.controller.vendas_db.obter_proximo_id()
        self.lbl_titulo.config(text=f"NOVA VENDA #{proximo_id:02d}")
        self.atualizar_visor()

    def atualizar_visor(self):
        venda = self.controller.venda_atual
        self.lista.delete(0, tk.END)
        if venda is None:
            self.lbl_total.config(text="TOTAL: R$ 0.00")
            return
        for item in venda.itens:
            self.lista.insert(
                tk.END,
                f"{item.produto.nome:<25} | Qtd: {item.quantidade:<3} | "
                f"Subtotal: R$ {item.subtotal:.2f}",
            )
        self.lbl_total.config(text=f"TOTAL: R$ {venda.total:.2f}")

    def add_produto(self):
        venda = self.controller.venda_atual
        if venda is None:
            messagebox.showerror("Venda", "Inicie uma venda antes de adicionar produtos.")
            return
        id_produto = simpledialog.askinteger("Adicionar produto", "ID do produto:", minvalue=1)
        if id_produto is None:
            return
        quantidade = simpledialog.askinteger(
            "Adicionar produto", "Quantidade desejada:", minvalue=1
        )
        if quantidade is None:
            return

        produto = self.controller.estoque_db.buscar_produto(id_produto)
        if produto is None:
            messagebox.showerror("Produto não encontrado", "Confira o ID informado.")
            return
        try:
            # A regra de quantidade e estoque pertence ao objeto Venda.
            venda.adicionar_produto(produto, quantidade)
        except (ValueError, TypeError) as erro:
            messagebox.showerror("Não foi possível adicionar", str(erro))
            return
        self.atualizar_visor()

    def fechar_venda(self):
        venda = self.controller.venda_atual
        if venda is None:
            return
        try:
            id_venda = venda.finalizar(self.controller.vendas_db)
        except (ValueError, TypeError) as erro:
            messagebox.showerror("Venda não concluída", str(erro))
            return
        linhas = [
            f"{item.produto.nome} — {item.quantidade} x R$ {item.produto.preco:.2f}"
            for item in venda.itens
        ]
        comprovante = (
            f"COMPROVANTE DE VENDA #{id_venda:02d}\n\n"
            + "\n".join(linhas)
            + f"\n\nTOTAL: R$ {venda.total:.2f}"
        )
        messagebox.showinfo("Venda concluída", comprovante)
        self.encerrar_ciclo()

    def cancelar_venda(self):
        venda = self.controller.venda_atual
        usuario = self.controller.usuario
        if venda is None or usuario is None:
            return

        autorizador = usuario
        if not usuario.pode_cancelar_venda():
            senha = simpledialog.askstring(
                "Autorização do gerente",
                "Digite a senha do gerente para cancelar a venda:",
                show="*",
            )
            if senha is None:
                return
            if senha != SENHA_ADMIN:
                messagebox.showerror("Erro", "Senha inválida. Venda não cancelada.")
                return
            autorizador = Gerente()

        try:
            venda.cancelar(autorizador)
        except (ValueError, PermissionError) as erro:
            messagebox.showerror("Não foi possível cancelar", str(erro))
            return

        messagebox.showinfo(
            "Venda cancelada",
            "Venda cancelada. Como ainda não havia sido finalizada, o estoque não foi alterado.",
        )
        self.encerrar_ciclo()

    def encerrar_ciclo(self):
        usuario = self.controller.usuario
        self.controller.venda_atual = None
        if usuario is not None and usuario.pode_gerenciar_estoque():
            self.controller.mostrar_frame(AdminFrame)
        else:
            self.controller.mostrar_frame(FuncionarioFrame)


if __name__ == "__main__":
    app = GestaoCaixaApp()
    app.mainloop()
