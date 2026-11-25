# Sistema Desktop de Gestão e Caixa

Projeto de frente de caixa e controle de estoque para pequenos comércios, desenvolvido em Python com Tkinter e SQLite.

## Integrantes
- **Abner da Silva Gomes** — matrícula 251018184
- **Vinicius Coelho de Souza** — matrícula 251016377

## Código-fonte

A versão de código-fonte organizada e corrigida está na pasta **[Gestao de Caixa/](Gestao%20de%20Caixa/)**.

- [Aplicação Tkinter](Gestao%20de%20Caixa/gestao_de_caixa.py)
- [Modelos, regras de negócio e persistência SQLite](Gestao%20de%20Caixa/sistema_bd.py)
- [Testes automatizados](Gestao%20de%20Caixa/tests/)
- [Diagrama UML de classes](Gestao%20de%20Caixa/uml/classes.md)

O arquivo ZIP mantido na raiz é o pacote original enviado anteriormente. Para executar a versão corrigida, use os arquivos da pasta **Gestao de Caixa/**, e não uma cópia antiga extraída do ZIP.

## Como executar

Requisitos: Python 3.10 ou superior e Tkinter disponível na instalação.

No terminal:

```bash
cd "Gestao de Caixa"
python gestao_de_caixa.py
```

O banco SQLite `sistema_caixa.db` é criado nessa pasta na primeira execução. Ao abrir um banco anterior, o programa acrescenta as colunas necessárias para registrar a data da venda e o vínculo do item com o produto, preservando os registros existentes.

O PIN administrativo padrão é `1234`. Ele pode ser alterado pela variável de ambiente `GESTAO_CAIXA_ADMIN_PIN`.

## Executar os testes

Na pasta `Gestao de Caixa`:

```bash
python -m unittest discover -s tests -v
```

Os testes usam bancos temporários, portanto não alteram o banco utilizado pela aplicação. O GitHub Actions também executa a verificação de sintaxe e os testes em Python 3.10, 3.11, 3.12 e 3.13.

## Organização orientada a objetos

A venda agora é representada por um objeto `Venda`, composto por objetos `ItemVenda), que se associam a `Produto`. A interface `VendaFrame` solicita operações ao modelo e apresenta os resultados; não mantém o carrinho nem calcula ou altera o total diretamente.

Os perfis `Funcionario` e `Gerente` herdam de `Usuario` e implementam as permissões de forma polimórfica. `EstoqueBD` e `VendasBD` compartilham a infraestrutura da classe `BancoDeDados`.

A finalização valida novamente as quantidades e o estoque dentro de uma transação SQLite. Se algum item não puder ser vendido, a venda inteira é cancelada, sem baixa parcial.

## Observação sobre o comprovante

A aplicação apresenta um comprovante simples da venda. O código não integra um serviço fiscal nem emite NF-e/NFC-e oficial; por isso, o comprovante não deve ser apresentado como nota fiscal eletrônica.
