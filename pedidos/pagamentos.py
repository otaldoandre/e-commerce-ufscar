from dataclasses import dataclass
from decimal import Decimal

from .models import Pedido


@dataclass(frozen=True)
class ResultadoAutorizacao:
    autorizado: bool
    mensagem: str


def autorizar_pagamento(
    forma_pagamento: str,
    valor: Decimal,
) -> ResultadoAutorizacao:
    formas_validas = {forma for forma, _ in Pedido.FormaPagamento.choices}
    if forma_pagamento not in formas_validas:
        return ResultadoAutorizacao(False, 'A forma de pagamento selecionada é inválida.')
    if valor <= 0:
        return ResultadoAutorizacao(False, 'O valor do pagamento deve ser maior que zero.')

    return ResultadoAutorizacao(
        True,
        'Pagamento autorizado pela simulação. Nenhuma cobrança real foi realizada.',
    )
