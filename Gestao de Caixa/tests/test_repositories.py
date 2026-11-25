import tempfile
import unittest
from pathlib import Path

from sistema_bd import EstoqueBD, ItemVenda, Produto, Venda, VendasBD


class TestRepositoriosSQLite(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / "teste.db"
        self.estoque = EstoqueBD(self.db_path)
        self.vendas = VendasBD(self.db_path)

    def tearDown(self):
        self.temp.cleanup()

    def criar_produto(self, nome="Mouse", preco=50.0, quantidade=8):
        id_produto = self.estoque.cadastrar(nome, preco, quantidade)
        return self.estoque.buscar_produto(id_produto)

    def test_crud_de_produto(self):
        produto = self.criar_produto()
        self.assertEqual(produto.nome, "Mouse")
        self.assertTrue(self.estoque.atualizar(produto.id, 55.0, 10))
        atualizado = self.estoque.buscar_produto(produto.id)
        self.assertEqual(atualizado.preco, 55.0)
        self.assertEqual(atualizado.quantidade, 10)
        self.assertTrue(self.estoque.deletar(produto.id))
        self.assertIsNone(self.estoque.buscar_produto(produto.id))

    def test_cadastro_e_atualizacao_rejeitam_quantidade_negativa(self):
        with self.assertRaises(ValueError):
            self.estoque.cadastrar("Produto inválido", 10.0, -2)
        produto = self.criar_produto()
        with self.assertRaises(ValueError):
            self.estoque.atualizar(produto.id, 10.0, -1)
        self.assertEqual(self.estoque.buscar_produto(produto.id).quantidade, 8)

    def test_venda_valida_registra_itens_e_reduz_estoque(self):
        produto = self.criar_produto(preco=25.0, quantidade=8)
        venda = Venda()
        venda.adicionar_produto(produto, 3)
        id_venda = venda.finalizar(self.vendas)

        self.assertGreater(id_venda, 0)
        self.assertEqual(venda.total, 75.0)
        self.assertEqual(venda.status, Venda.FECHADA)
        self.assertEqual(self.estoque.buscar_produto(produto.id).quantidade, 5)

        resumo = self.vendas.resumo_dia()
        self.assertEqual(resumo["quantidade_vendas"], 1)
        self.assertEqual(resumo["total_arrecadado"], 75.0)

    def test_repositorio_bloqueia_item_adulterado_com_quantidade_negativa(self):
        produto = self.criar_produto(quantidade=8)
        venda = Venda()
        item_adulterado = object.__new__(ItemVenda)
        object.__setattr__(item_adulterado, "produto", produto)
        object.__setattr__(item_adulterado, "quantidade", -3)
        venda._itens.append(item_adulterado)

        with self.assertRaises(ValueError):
            self.vendas.registrar_venda(venda)

        self.assertEqual(self.estoque.buscar_produto(produto.id).quantidade, 8)
        self.assertEqual(self.vendas.resumo_dia()["quantidade_vendas"], 0)

    def test_estoque_e_validado_novamente_na_finalizacao(self):
        produto = self.criar_produto(quantidade=8)
        venda = Venda()
        venda.adicionar_produto(produto, 5)
        self.estoque.atualizar(produto.id, produto.preco, 2)

        with self.assertRaises(ValueError):
            venda.finalizar(self.vendas)

        self.assertEqual(self.estoque.buscar_produto(produto.id).quantidade, 2)
        self.assertEqual(self.vendas.resumo_dia()["quantidade_vendas"], 0)
        self.assertEqual(venda.status, Venda.ABERTA)

    def test_falha_em_um_item_nao_deixa_baixa_parcial(self):
        produto_a = self.criar_produto("Teclado", 80.0, 5)
        produto_b = self.criar_produto("Monitor", 700.0, 5)
        venda = Venda()
        venda.adicionar_produto(produto_a, 2)
        venda.adicionar_produto(produto_b, 4)
        self.estoque.atualizar(produto_b.id, produto_b.preco, 1)

        with self.assertRaises(ValueError):
            venda.finalizar(self.vendas)

        self.assertEqual(self.estoque.buscar_produto(produto_a.id).quantidade, 5)
        self.assertEqual(self.estoque.buscar_produto(produto_b.id).quantidade, 1)
        self.assertEqual(self.vendas.resumo_dia()["quantidade_vendas"], 0)

    def test_relatorio_filtra_data(self):
        produto = self.criar_produto(preco=10.0, quantidade=10)
        venda_hoje = Venda()
        venda_hoje.adicionar_produto(produto, 1)
        venda_hoje.finalizar(self.vendas)

        with self.vendas.conectar() as con:
            con.execute(
                "INSERT INTO vendas (total, data_hora) VALUES (?, datetime('now', 'localtime', '-1 day'))",
                (999.0,),
            )

        resumo = self.vendas.resumo_dia()
        self.assertEqual(resumo["quantidade_vendas"], 1)
        self.assertEqual(resumo["total_arrecadado"], 10.0)


if __name__ == "__main__":
    unittest.main()
