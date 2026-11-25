"""Modelos de domínio e acesso ao SQLite do Sistema Desktop de Gestão e Caixa.

As regras de venda ficam nas classes de domínio. A interface Tkinter apenas
coleta entradas, chama essas classes e apresenta os resultados.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
import math
from pathlib import Path
import sqlite3
from typing import Iterator, Optional


@dataclass(frozen=True)
class Produto:
    id: int
    nome: str
    preco: float
    quantidade: int

    def __post_init__(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("O nome do produto é obrigatório.")
        if not math.isfinite(float(self.preco)) or float(self.preco) < 0:
            raise ValueError("O preço deve ser um número válido e não negativo.")
        if isinstance(self.quantidade, bool) or not isinstance(self.quantidade, int):
            raise ValueError("A quantidade em estoque deve ser um número inteiro.")
        if self.quantidade < 0:
            raise ValueError("A quantidade em estoque não pode ser negativa.")
        object.__setattr__(self, "nome", self.nome.strip())
        object.__setattr__(self, "preco", float(self.preco))


@dataclass(frozen=True)
class ItemVenda:
    produto: Produto
    quantidade: int

    def __post_init__(self) -> None:
        if not isinstance(self.produto, Produto):
            raise TypeError("O item precisa estar associado a um Produto.")
        if isinstance(self.quantidade, bool) or not isinstance(self.quantidade, int):
            raise ValueError("A quantidade vendida deve ser um número inteiro.")
        if self.quantidade <= 0:
            raise ValueError("A quantidade vendida deve ser maior que zero.")
        if self.quantidade > self.produto.quantidade:
            raise ValueError("A quantidade solicitada supera o estoque disponível.")

    @property
    def subtotal(self) -> float:
        return round(self.produto.preco * self.quantidade, 2)


class Usuario:
    """Contrato de permissões; as subclasses especializam o comportamento."""

    perfil = "Usuário"

    def pode_gerenciar_estoque(self) -> bool:
        return False

    def pode_cancelar_venda(self) -> bool:
        return False


class Funcionario(Usuario):
    perfil = "Funcionário"

    def pode_gerenciar_estoque(self) -> bool:
        return False

    def pode_cancelar_venda(self) -> bool:
        return False


class Gerente(Usuario):
    perfil = "Gerente"

    def pode_gerenciar_estoque(self) -> bool:
        return True

    def pode_cancelar_venda(self) -> bool:
        return True


class Venda:
    """Mantém os itens, o total e o estado de uma venda."""

    ABERTA = "aberta"
    FECHADA = "fechada"
    CANCELADA = "cancelada"

    def __init__(self) -> None:
        self.id: Optional[int] = None
        self._itens: list[ItemVenda] = []
        self._status = self.ABERTA

    @property
    def itens(self) -> tuple[ItemVenda, ...]:
        return tuple(self._itens)

    @property
    def status(self) -> str:
        return self._status

    @property
    def total(self) -> float:
        return round(sum(item.subtotal for item in self._itens), 2)

    def adicionar_produto(self, produto: Produto, quantidade: int) -> None:
        if self._status != self.ABERTA:
            raise ValueError("Só é possível alterar uma venda aberta.")
        if not isinstance(produto, Produto):
            raise TypeError("O produto informado é inválido.")
        if isinstance(quantidade, bool) or not isinstance(quantidade, int):
            raise ValueError("A quantidade deve ser um número inteiro.")
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")

        quantidade_ja_adicionada = sum(
            item.quantidade for item in self._itens if item.produto.id == produto.id
        )
        if quantidade_ja_adicionada + quantidade > produto.quantidade:
            raise ValueError(
                f"Estoque insuficiente. Disponível: {produto.quantidade}; "
                f"já no carrinho: {quantidade_ja_adicionada}."
            )

        self._itens.append(ItemVenda(produto, quantidade))

    def finalizar(self, repositorio_vendas: "VendasBD") -> int:
        if self._status != self.ABERTA:
            raise ValueError("Esta venda não está aberta.")
        if not self._itens:
            raise ValueError("Não é possível finalizar uma venda sem produtos.")

        # Dependência explícita do repositório: a persistência é delegada.
        id_venda = repositorio_vendas.registrar_venda(self)
        self.id = id_venda
        self._status = self.FECHADA
        return id_venda

    def cancelar(self, usuario: Usuario) -> None:
        if self._status != self.ABERTA:
            raise ValueError("Somente uma venda aberta pode ser cancelada.")
        if not isinstance(usuario, Usuario) or not usuario.pode_cancelar_venda():
            raise PermissionError("O cancelamento precisa ser autorizado por um gerente.")
        self._status = self.CANCELADA


class BancoDeDados:
    """Classe base com a configuração e o ciclo de vida das conexões SQLite."""

    def __init__(self, nome_banco: Optional[str | Path] = None) -> None:
        caminho = Path(nome_banco) if nome_banco else Path(__file__).with_name("sistema_caixa.db")
        caminho.parent.mkdir(parents=True, exist_ok=True)
        self.nome_banco = str(caminho)
        self.inicializar_banco()

    @contextmanager
    def conectar(self) -> Iterator[sqlite3.Connection]:
        conexao = sqlite3.connect(self.nome_banco, timeout=15)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        try:
            yield conexao
            conexao.commit()
        except Exception:
            conexao.rollback()
            raise
        finally:
            conexao.close()

    def inicializar_banco(self) -> None:
        with self.conectar() as con:
            con.execute(
                """CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    preco REAL NOT NULL,
                    quantidade INTEGER NOT NULL CHECK (quantidade >= 0)
                )"""
            )
            con.execute(
                """CREATE TABLE IF NOT EXISTS vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total REAL NOT NULL,
                    data_hora TEXT
                )"""
            )
            con.execute(
                """CREATE TABLE IF NOT EXISTS itens_venda (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venda_id INTEGER NOT NULL,
                    produto_nome TEXT NOT NULL,
                    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
                    subtotal REAL NOT NULL,
                    produto_id INTEGER
                )"""
            )

            # Migração compatível com o banco já entregue pelo projeto.
            colunas_vendas = {
                linha["name"] for linha in con.execute("PRAGMA table_info(vendas)")
            }
            if "data_hora" not in colunas_vendas:
                con.execute("ALTER TABLE vendas ADD COLUMN data_hora TEXT")

            colunas_itens = {
                linha["name"] for linha in con.execute("PRAGMA table_info(itens_venda)")
            }
            if "produto_id" not in colunas_itens:
                con.execute("ALTER TABLE itens_venda ADD COLUMN produto_id INTEGER")


class EstoqueBD(BancoDeDados):
    """Repositório responsável pelo cadastro e pela consulta de produtos."""

    @staticmethod
    def _validar_preco(preco: float) -> float:
        try:
            valor = float(preco)
        except (TypeError, ValueError) as exc:
            raise ValueError("O preço informado é inválido.") from exc
        if not math.isfinite(valor) or valor < 0:
            raise ValueError("O preço deve ser válido e não negativo.")
        return valor

    @staticmethod
    def _validar_quantidade(quantidade: int) -> int:
        if isinstance(quantidade, bool) or not isinstance(quantidade, int):
            raise ValueError("A quantidade deve ser um número inteiro.")
        if quantidade < 0:
            raise ValueError("A quantidade em estoque não pode ser negativa.")
        return quantidade

    def cadastrar(self, nome: str, preco: float, qtd: int) -> int:
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("O nome do produto é obrigatório.")
        preco = self._validar_preco(preco)
        qtd = self._validar_quantidade(qtd)
        with self.conectar() as con:
            cursor = con.execute(
                "INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)",
                (nome, preco, qtd),
            )
            return int(cursor.lastrowid)

    def listar_produtos(self) -> list[Produto]:
        with self.conectar() as con:
            linhas = con.execute(
                "SELECT id, nome, preco, quantidade FROM produtos ORDER BY id"
            ).fetchall()
        return [Produto(row["id"], row["nome"], row["preco"], row["quantidade"]) for row in linhas]

    def buscar_produto(self, id_produto: int) -> Optional[Produto]:
        with self.conectar() as con:
            row = con.execute(
                "SELECT id, nome, preco, quantidade FROM produtos WHERE id = ?",
                (id_produto,),
            ).fetchone()
        if row is None:
            return None
        return Produto(row["id"], row["nome"], row["preco"], row["quantidade"])

    def atualizar(self, id_produto: int, preco: float, qtd: int) -> bool:
        preco = self._validar_preco(preco)
        qtd = self._validar_quantidade(qtd)
        with self.conectar() as con:
            cursor = con.execute(
                "UPDATE produtos SET preco = ?, quantidade = ? WHERE id = ?",
                (preco, qtd, id_produto),
            )
            return cursor.rowcount > 0

    def deletar(self, id_produto: int) -> bool:
        with self.conectar() as con:
            cursor = con.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
            return cursor.rowcount > 0


class VendasBD(BancoDeDados):
    """Repositório que registra vendas e atualiza o estoque em uma transação."""

    def obter_proximo_id(self) -> int:
        with self.conectar() as con:
            row = con.execute("SELECT COALESCE(MAX(id), 0) + 1 AS proximo FROM vendas").fetchone()
            return int(row["proximo"])

    def registrar_venda(self, venda: Venda) -> int:
        if not isinstance(venda, Venda):
            raise TypeError("É necessário informar um objeto Venda.")
        itens = venda.itens
        if not itens:
            raise ValueError("Não é possível registrar uma venda sem itens.")

        quantidades: dict[int, int] = {}
        for item in itens:
            if not isinstance(item, ItemVenda):
                raise TypeError("A venda contém um item inválido.")
            if isinstance(item.quantidade, bool) or not isinstance(item.quantidade, int):
                raise ValueError("A quantidade vendida deve ser um número inteiro.")
            if item.quantidade <= 0:
                raise ValueError("A quantidade vendida deve ser maior que zero.")
            produto_id = item.produto.id
            quantidades[produto_id] = quantidades.get(produto_id, 0) + item.quantidade

        total = venda.total
        if not math.isfinite(total) or total < 0:
            raise ValueError("O total da venda é inválido.")

        with self.conectar() as con:
            # Bloqueia outras escritas durante a validação e a baixa do estoque.
            con.execute("BEGIN IMMEDIATE")

            for produto_id, quantidade in quantidades.items():
                produto = con.execute(
                    "SELECT nome, quantidade FROM produtos WHERE id = ?",
                    (produto_id,),
                ).fetchone()
                if produto is None:
                    raise ValueError(f"Produto {produto_id} não existe mais no estoque.")
                if produto["quantidade"] < quantidade:
                    raise ValueError(
                        f"Estoque insuficiente para {produto['nome']}. "
                        f"Disponível: {produto['quantidade']}; solicitado: {quantidade}."
                    )

            cursor = con.execute(
                "INSERT INTO vendas (total, data_hora) VALUES (?, datetime('now', 'localtime'))",
                (total,),
            )
            id_venda = int(cursor.lastrowid)

            for item in itens:
                cursor_estoque = con.execute(
                    """UPDATE produtos
                       SET quantidade = quantidade - ?
                       WHERE id = ? AND quantidade >= ?""",
                    (item.quantidade, item.produto.id, item.quantidade),
                )
                if cursor_estoque.rowcount != 1:
                    raise ValueError("O estoque mudou durante a venda. Confira os produtos e tente novamente.")

                con.execute(
                    """INSERT INTO itens_venda
                       (venda_id, produto_id, produto_nome, quantidade, subtotal)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        id_venda,
                        item.produto.id,
                        item.produto.nome,
                        item.quantidade,
                        item.subtotal,
                    ),
                )

            return id_venda

    def relatorio_dia(self, data_referencia: Optional[str] = None) -> list[tuple[int, float, Optional[str]]]:
        with self.conectar() as con:
            rows = con.execute(
                """SELECT id, total, data_hora
                   FROM vendas
                   WHERE date(data_hora) = COALESCE(?, date('now', 'localtime'))
                   ORDER BY id""",
                (data_referencia,),
            ).fetchall()
        return [(row["id"], float(row["total"]), row["data_hora"]) for row in rows]

    def resumo_dia(self, data_referencia: Optional[str] = None) -> dict[str, object]:
        vendas = self.relatorio_dia(data_referencia)
        return {
            "quantidade_vendas": len(vendas),
            "total_arrecadado": round(sum(venda[1] for venda in vendas), 2),
            "vendas": vendas,
        }
