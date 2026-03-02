"""seed_rpas_dimensions

Revision ID: 5105a59342db
Revises: 4fc40386fe85
Create Date: 2026-02-26 20:21:52.603444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5105a59342db'
down_revision: Union[str, Sequence[str], None] = '4fc40386fe85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        INSERT INTO rpas.produtos (nome)
        VALUES ('Saúde'), ('Vida'), ('Odonto')
        ON CONFLICT (nome) DO NOTHING;

        INSERT INTO rpas.tipos_contrato (nome)
        VALUES ('PJ'), ('PME'), ('Adesão'), ('Individual')
        ON CONFLICT (nome) DO NOTHING;

        INSERT INTO rpas.processos (nome)
        VALUES ('Saúde'), ('Vida'), ('Odonto')
        ON CONFLICT (nome) DO NOTHING;

        INSERT INTO rpas.tipos_rpa (nome)
        VALUES ('Faturamento'), ('Movimentação')
        ON CONFLICT (nome) DO NOTHING;

        INSERT INTO rpas.status (nome)
        VALUES ('Funcionando'), ('Manutenção'), ('Pausado'), ('Dep. Operadora')
        ON CONFLICT (nome) DO NOTHING;

        INSERT INTO rpas.retencao_carteirinhas (nome)
        VALUES ('Automático'), ('Manual')
        ON CONFLICT (nome) DO NOTHING;

        INSERT INTO rpas.formas_operacao (nome)
        VALUES ('Online'), ('Batch'), ('Híbrido'), ('Manual')
        ON CONFLICT (nome) DO NOTHING;

        INSERT INTO rpas.status_acessos (nome)
        VALUES ('Ativo'), ('Pendente'), ('Bloqueado')
        ON CONFLICT (nome) DO NOTHING;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DELETE FROM rpas.status_acessos
        WHERE nome IN ('Ativo', 'Pendente', 'Bloqueado');

        DELETE FROM rpas.formas_operacao
        WHERE nome IN ('Online', 'Batch', 'Híbrido', 'Manual');

        DELETE FROM rpas.retencao_carteirinhas
        WHERE nome IN ('Automático', 'Manual');

        DELETE FROM rpas.status
        WHERE nome IN ('Funcionando', 'Manutenção', 'Pausado', 'Dep. Operadora');

        DELETE FROM rpas.tipos_rpa
        WHERE nome IN ('Faturamento', 'Movimentação');

        DELETE FROM rpas.processos
        WHERE nome IN ('Saúde', 'Vida', 'Odonto');

        DELETE FROM rpas.tipos_contrato
        WHERE nome IN ('PJ', 'PME', 'Adesão', 'Individual');

        DELETE FROM rpas.produtos
        WHERE nome IN ('Saúde', 'Vida', 'Odonto');
        """
    )
