# Roteiro de testes manuais da interface

Os testes automatizados cobrem modelos e persistência SQLite. Este roteiro complementa a verificação visual das telas Tkinter.

## Perfil Funcionário
- [ ] Entrar como Funcionário (Caixa).
- [ ] Iniciar uma venda.
- [ ] Adicionar um produto existente e confirmar item/total na tela.
- [ ] Tentar um ID inexistente e confirmar a mensagem de erro.
- [ ] Tentar quantidade zero ou negativa (a caixa de entrada deve impedir; a classe Venda também valida).
- [ ] Tentar quantidade maior que o estoque e confirmar que o item não entra.
- [ ] Fechar uma venda válida e conferir o comprovante e a baixa do estoque.
- [ ] Cancelar uma venda aberta com PIN de gerente válido.
- [ ] Tentar cancelar com PIN inválido e confirmar que a venda permanece aberta.

## Perfil Gerente
- [ ] Entrar com o PIN administrativo.
- [ ] Cadastrar um produto com dados válidos.
- [ ] Tentar cadastrar quantidade negativa e confirmar que o sistema recusa.
- [ ] Listar produtos.
- [ ] Atualizar preço e quantidade.
- [ ] Tentar atualizar com quantidade negativa e confirmar que o sistema recusa.
- [ ] Excluir um produto de teste.
- [ ] Consultar o relatório diário e conferir quantidade de vendas e total arrecadado.
- [ ] Iniciar e concluir uma venda também pelo perfil Gerente.

## Evidência para a gravação
- [ ] Mostrar o comando de execução dos testes automatizados.
- [ ] Mostrar a saída completa com os testes aprovados.
- [ ] Demonstrar ao menos uma venda válida e uma tentativa de venda inválida.
- [ ] Mostrar que a tentativa inválida não altera o estoque nem registra uma venda.
