import unittest

from sistema_bd import Funcionario, Gerente, ItemVenda, Produto, Venda


class TestModeloVenda(unittest.TestCase):
    def setUp(self):
        self.produto = Produto(1, "Teclado", 80.0, 5)
        self.venda = Venda()

    def test_adicionar_produto_calcula_total(self):
        self.venda.adicionar_produto(self.produto, 2)
        self.assertEqual(self.venda.total, 160.0)
        self.assertEqual(len(self.venda.itens), 1)

    def test_quantidade_zero_e_negativa_sao_rejeitadas(self):
        for quantidade in (0, -1, -5):
            with self.subTest(quantidade=quantidade):
                with self.assertRaises(ValueError):
                    ItemVenda(self.produto, quantidade)

    def test_quantidade_maior_que_estoque_e_rejeitada(self):
        with self.assertRaises(ValueError):
            self.venda.adicionar_produto(self.produto, 6)

    def test_quantidade_repetida_nao_ultrapassa_estoque(self):
        self.venda.adicionar_produto(self.produto, 3)
        with self.assertRaises(ValueError):
            self.venda.adicionar_produto(self.produto, 3)

    def test_funcionario_e_gerente_tem_permissoes_diferentes(self):
        funcionario = Funcionario()
        gerente = Gerente()
        self.assertFalse(funcionario.pode_gerenciar_estoque())
        self.assertFalse(funcionario.pode_cancelar_venda())
        self.assertTrue(gerente.pode_gerenciar_estoque())
        self.assertTrue(gerente.pode_cancelar_venda())

    def test_venda_vazia_nao_pode_ser_finalizada(self):
        class RepositorioFalso:
            def registrar_venda(self, venda):
                raise AssertionError("O repositório não deveria ser chamado.")

        with self.assertRaises(ValueError):
            self.venda.finalizar(RepositorioFalso())

    def test_venda_fechada_nao_pode_ser_alterada_ou_finalizada_novamente(self):
        class RepositorioFalso:
            def registrar_venda(self, venda):
                return 42

        self.venda.adicionar_produto(self.produto, 1)
        self.venda.finalizar(RepositorioFalso())

        with self.assertRaises(ValueError):
            self.venda.adicionar_produto(self.produto, 1)
        with self.assertRaises(ValueError):
            self.venda.finalizar(RepositorioFalso())

    def test_cancelamento_exige_gerente(self):
        with self.assertRaises(PermissionError):
            self.venda.cancelar(Funcionario())
        self.venda.cancelar(Gerente())
        self.assertEqual(self.venda.status, Venda.CANCELADA)

    def test_venda_cancelada_nao_recebe_itens(self):
        self.venda.cancelar(Gerente())
        with self.assertRaises(ValueError):
            self.venda.adicionar_produto(self.produto, 1)


if __name__ == "__main__":
    unittest.main()
