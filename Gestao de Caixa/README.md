# Sistema Desktop de Gestão e Caixa

Projeto de PDV e controle de estoque para pequenos comércios, desenvolvido em Python com Tkinter e SQLite.

## Executar

Requisitos: Python 3.10 ou superior e Tkinter instalado.

1. Abra esta pasta no VS Code.
2. Execute no terminal:

   ```bash
   python gestao_de_caixa.py
   ```

O banco `sistema_caixa.db` é criado ao lado dos arquivos Python na primeira execução. Ao abrir um banco antigo, a aplicação acrescenta as colunas de data e vínculo do produto que faltarem, sem apagar os registros existentes.

PIN administrativo padrão: `1234`. Para alterar, defina a variável de ambiente `GESTAO_CAIXA_ADMIN_PIN`.

## Testes automatizados

Na pasta `Gestao de Caixa`, execute:

```bash
python -m unittest discover -s tests -v
```

Os testes usam bancos temporários e não alteram o banco usado pela aplicação.

## Organização

- `gestao_de_caixa.py`: telas Tkinter e navegação.
- `sistema_bd.py`: modelos de domínio, permissões dos perfis e repositórios SQLite.
- `tests/`: testes automatizados de modelos, validações, CRUD, venda e estoque.
- `uml/classes.mmd`: diagrama de classes em Mermaid.

## Mudanças importantes

- A classe `Venda` passou a controlar os itens, o total e o estado da operação.
- `VendaFrame` deixou de alterar diretamente carrinho, total e estoque; agora delega as operações ao modelo `Venda`.
- Quantidades zero, negativas, não inteiras ou acima do estoque são recusadas.
- A gravação da venda e a baixa do estoque acontecem em uma única transação SQLite. Se qualquer item falhar na validação, nenhuma baixa parcial é confirmada.
- O relatório diário passou a filtrar as vendas pela data de registro.
- Os perfis `Funcionario` e `Gerente` implementam permissões diferentes a partir da classe base `Usuario`.

## Sobre o comprovante

O fechamento apresenta um comprovante simples da venda no próprio aplicativo. O código não integra um serviço fiscal nem emite NF-e/NFC-e oficial; por isso, o comprovante não deve ser apresentado como nota fiscal eletrônica.

## UML e orientação a objetos

O diagrama registra as relações que estão implementadas no código: herança, polimorfismo, composição, associação e dependência. Abra `uml/classes.mmd` em um visualizador/editor Mermaid para visualizar o diagrama.
