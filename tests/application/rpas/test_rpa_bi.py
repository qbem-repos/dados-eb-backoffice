import pytest

from src.application.rpas.rpa import RPAService
from tests._tests_config import (
    create_rpa_dependencies,
    cleanup_rpa_dependencies,
    delete_rpa,
    make_nome,
)


@pytest.mark.asyncio
async def test_rpa_bi_returns_aggregates(db_session, user_scope):
    deps = await create_rpa_dependencies(db_session)
    data = RPAService.Create.Input(
        nome=make_nome("rpa_bi"),
        operadora_nome=deps.operadora.nome,
        produto_nome=deps.produto.nome,
        tipo_contrato_nome=deps.tipo_contrato.nome,
        processo_nome=deps.processo.nome,
        tipo_rpa_nome=deps.tipo_rpa.nome,
        status_nome=deps.status.nome,
        status_detalhe=None,
        status_last_update=None,
        retencao_carteirinha_nome=deps.retencao.nome,
        doc_baixa=None,
        forma_operacao_nome=deps.forma_operacao.nome,
        status_acesso_nome=deps.status_acessos.nome,
        status_acesso_detalhe=None,
        status_acesso_last_update=None,
    )
    model = await RPAService.Create.create_rpa(
        data=data,
        user_scope=user_scope,
        session=db_session,
        user_id=user_scope.user_id,
    )

    try:
        table = await RPAService.BI.list_full_table(
            RPAService.BI.ListTableInput(id=model.id),
            user_scope,
            db_session,
        )
        assert any(item.id == model.id for item in table)

        total = await RPAService.BI.total_rpas(user_scope, db_session)
        assert total >= 1

        total_por_status = await RPAService.BI.total_por_status(user_scope, db_session)
        assert any(row["status_nome"] == deps.status.nome and row["total"] >= 1 for row in total_por_status)

        total_por_status_acesso = await RPAService.BI.total_por_status_acesso(user_scope, db_session)
        assert any(
            row["status_acesso_nome"] == deps.status_acessos.nome and row["total"] >= 1
            for row in total_por_status_acesso
        )

        total_por_produto = await RPAService.BI.total_por_produto(user_scope, db_session)
        assert any(row["produto_nome"] == deps.produto.nome and row["total"] >= 1 for row in total_por_produto)

        total_por_processo = await RPAService.BI.total_por_processo(user_scope, db_session)
        assert any(row["processo_nome"] == deps.processo.nome and row["total"] >= 1 for row in total_por_processo)
    finally:
        await delete_rpa(db_session, model.nome)
        await cleanup_rpa_dependencies(db_session, deps)
