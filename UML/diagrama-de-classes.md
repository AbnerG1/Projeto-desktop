# Diagrama de classes — Gestão de Caixa

```mermaid
classDiagram
direction TB

class BancoDeDados {
  +nome_banco: str
  +__init__()
  +inicializar_banco()
}
class EstoqueBD {
  +cadastrar(nome, preco, qtd)
  +listar_produtos()
  +atualizar(id_p, preco, qtd)
  +deletar(id_p)
  +buscar_produto(id_p)
}
class VendasBD {
  +obter_proximo_id()
  +registrar_venda_e_baixar_estoque(total, carrinho)
  +relatorio_dia()
}
BancoDeDados <|-- EstoqueBD : herança
BancoDeDados <|-- VendasBD : herança

class TkRoot <<Tkinter>>
class TkFrame <<Tkinter>>

class GestaoCaixaApp {
  +estoque_db: EstoqueBD
  +vendas_db: VendasBD
  +perfil_atual: str
  +carrinho: list
  +total_venda: float
  +frames: dict
  +__init__()
  +mostrar_frame(frame_class)
}
class LoginFrame {
  +controller: GestaoCaixaApp
  +__init__(parent, controller)
  +acesso_admin()
  +acesso_funcionario()
}
class AdminFrame {
  +controller: GestaoCaixaApp
  +__init__(parent, controller)
  +criar()
  +listar()
  +atualizar()
  +deletar()
  +relatorio()
}
class FuncionarioFrame {
  +controller: GestaoCaixaApp
  +__init__(parent, controller)
}
class VendaFrame {
  +controller: GestaoCaixaApp
  +lbl_titulo
  +lista
  +lbl_total
  +__init__(parent, controller)
  +preparar_nova_venda()
  +atualizar_visor()
  +add_produto()
  +fechar_venda()
  +cancelar_venda()
  +encerrar_ciclo()
}

TkRoot <|-- GestaoCaixaApp : herança
TkFrame <|-- LoginFrame : herança
TkFrame <|-- AdminFrame : herança
TkFrame <|-- FuncionarioFrame : herança
TkFrame <|-- VendaFrame : herança

GestaoCaixaApp "1" *-- "1" LoginFrame : cria e mantém
GestaoCaixaApp "1" *-- "1" AdminFrame : cria e mantém
GestaoCaixaApp "1" *-- "1" FuncionarioFrame : cria e mantém
GestaoCaixaApp "1" *-- "1" VendaFrame : cria e mantém

LoginFrame --> GestaoCaixaApp : controller
AdminFrame --> GestaoCaixaApp : controller
FuncionarioFrame --> GestaoCaixaApp : controller
VendaFrame --> GestaoCaixaApp : controller

GestaoCaixaApp --> EstoqueBD : utiliza
GestaoCaixaApp --> VendasBD : utiliza
AdminFrame ..> EstoqueBD : dependência
AdminFrame ..> VendasBD : dependência
VendaFrame ..> EstoqueBD : dependência
VendaFrame ..> VendasBD : dependência
```

## Relações identificadas no código

- **Herança:** `EstoqueBD` e `VendasBD` herdam de `BancoDeDados`. A aplicação herda de `tk.Tk`, e as quatro telas herdam de `tk.Frame`.
- **Composição:** `GestaoCaixaApp` instancia as telas e mantém suas referências no dicionário `frames`.
- **Associação:** cada tela recebe e guarda a referência `controller`, que aponta para a instância de `GestaoCaixaApp`.
- **Dependência:** as telas administrativa e de venda utilizam os repositórios de estoque e vendas por meio do controller.

## Limite importante da modelagem

O código atual demonstra claramente herança, composição/gerenciamento das telas, associação com o controller e dependência dos repositórios. A chamada de `tkraise()` em telas diferentes, por si só, não é uma demonstração forte de polimorfismo definido pela aplicação: é um método herdado do Tkinter. Por isso, não classifico esse ponto como polimorfismo comprovado no modelo.

O estado da venda (`carrinho` e `total_venda`) fica em `GestaoCaixaApp`, e `VendaFrame` executa as operações de inclusão, cálculo e fechamento. Não existe uma classe de domínio `Venda` no código original. O diagrama documenta a implementação atual, não uma refatoração proposta.
