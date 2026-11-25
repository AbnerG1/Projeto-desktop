# Diagrama de classes — Sistema Desktop

O diagrama abaixo corresponde às classes da versão atual do código. Ele inclui os modelos de venda, os repositórios SQLite, os perfis e as telas Tkinter.

```mermaid
classDiagram
direction TB

class Usuario {
  +perfil: str
  +pode_gerenciar_estoque() bool
  +pode_cancelar_venda() bool
}
class Funcionario {
  +pode_gerenciar_estoque() bool
  +pode_cancelar_venda() bool
}
class Gerente {
  +pode_gerenciar_estoque() bool
  +pode_cancelar_venda() bool
}
Usuario <|-- Funcionario : herança
Usuario <|-- Gerente : herança

note for Usuario "Polimorfismo: a aplicação chama os mesmos métodos de permissão; cada perfil responde de forma diferente."

class Produto {
  +id: int
  +nome: str
  +preco: float
  +quantidade: int
}
class ItemVenda {
  +produto: Produto
  +quantidade: int
  +subtotal: float
}
class Venda {
  +id: int
  +status: str
  +itens: tuple
  +total: float
  +adicionar_produto(produto, quantidade)
  +finalizar(repositorio_vendas)
  +cancelar(usuario)
}
Venda "1" *-- "0..*" ItemVenda : composição
ItemVenda "0..*" --> "1" Produto : associação
Venda ..> VendasBD : dependência

class BancoDeDados {
  +nome_banco: str
  +conectar()
  +inicializar_banco()
}
class EstoqueBD {
  +cadastrar(nome, preco, qtd)
  +listar_produtos()
  +buscar_produto(id)
  +atualizar(id, preco, qtd)
  +deletar(id)
}
class VendasBD {
  +registrar_venda(venda)
  +relatorio_dia(data)
  +resumo_dia(data)
}
BancoDeDados <|-- EstoqueBD : herança
BancoDeDados <|-- VendasBD : herança

class TkRoot <<Tkinter>>
class TkFrame <<Tkinter>>
class GestaoCaixaApp {
  +usuario: Usuario
  +venda_atual: Venda
  +estoque_db: EstoqueBD
  +vendas_db: VendasBD
  +iniciar_venda()
  +mostrar_frame(classe)
  +sair()
}
class LoginFrame {
  +acesso_admin()
  +acesso_funcionario()
}
class AdminFrame {
  +criar()
  +listar()
  +atualizar()
  +deletar()
  +relatorio()
}
class FuncionarioFrame
class VendaFrame {
  +preparar_nova_venda()
  +atualizar_visor()
  +add_produto()
  +fechar_venda()
  +cancelar_venda()
}
GestaoCaixaApp --|> TkRoot : herança Tkinter
LoginFrame --|> TkFrame : herança Tkinter
AdminFrame --|> TkFrame : herança Tkinter
FuncionarioFrame --|> TkFrame : herança Tkinter
VendaFrame --|> TkFrame : herança Tkinter
GestaoCaixaApp *-- LoginFrame : composição
GestaoCaixaApp *-- AdminFrame : composição
GestaoCaixaApp *-- FuncionarioFrame : composição
GestaoCaixaApp *-- VendaFrame : composição
GestaoCaixaApp o-- EstoqueBD : mantém
GestaoCaixaApp o-- VendasBD : mantém
GestaoCaixaApp --> Usuario : perfil atual
GestaoCaixaApp --> Venda : venda em andamento
AdminFrame ..> EstoqueBD : dependência
AdminFrame ..> VendasBD : dependência
VendaFrame ..> Venda : dependência
```

## Relações representadas

- **Herança:** `Funcionario` e `Gerente` especializam `Usuario`; `EstoqueBD` e `VendasBD` compartilham `BancoDeDados`. As telas também herdam de `tk.Frame`, e a aplicação herda de `tk.Tk`.
- **Polimorfismo:** a aplicação consulta `pode_gerenciar_estoque()` e `pode_cancelar_venda()` no tipo `Usuario`; o resultado muda conforme o objeto concreto (`Funcionario` ou `Gerente`).
- **Composição:** uma `Venda` é formada por seus `ItemVenda`; os itens pertencem à venda em andamento.
- **Associação:** cada `ItemVenda` mantém a referência ao `Produto` correspondente.
- **Dependência:** `Venda` utiliza `VendasBD` para persistir a operação; as telas utilizam os modelos e repositórios para executar as ações solicitadas.

O diagrama não substitui a leitura do código: os métodos e relações podem ser conferidos em `sistema_bd.py` e `gestao_de_caixa.py`.
