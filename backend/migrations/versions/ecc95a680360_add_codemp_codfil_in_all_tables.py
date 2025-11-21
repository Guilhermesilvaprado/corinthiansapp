from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "ecc95a680360"  # <= 12 chars, ok para VARCHAR(32)
down_revision = "20250926_create_all_base_tables"  # 31 chars, cabe
branch_labels = None
depends_on = None


def upgrade():
    """
    Adiciona codemp e codfil nas tabelas que ainda não possuem,
    verificando antes se as colunas já existem para evitar erros.
    """
    bind = op.get_bind()
    insp = Inspector.from_engine(bind)

    def ensure_tenant_columns_and_index(table_name):
        """Garante que a tabela tenha codemp, codfil e índice tenant"""
        # Verifica colunas existentes
        existing_columns = {col["name"]
                            for col in insp.get_columns(table_name)}

        # Adiciona codemp se não existir
        if "codemp" not in existing_columns:
            op.add_column(
                table_name,
                sa.Column("codemp", sa.Integer(),
                          nullable=False, server_default="0")
            )
            print(f"✅ Adicionada coluna 'codemp' na tabela {table_name}")
        else:
            print(f"⚠️  Coluna 'codemp' já existe na tabela {table_name}")

        # Adiciona codfil se não existir
        if "codfil" not in existing_columns:
            op.add_column(
                table_name,
                sa.Column("codfil", sa.Integer(),
                          nullable=False, server_default="0")
            )
            print(f"✅ Adicionada coluna 'codfil' na tabela {table_name}")
        else:
            print(f"⚠️  Coluna 'codfil' já existe na tabela {table_name}")

        # Verifica índices existentes
        existing_indexes = {idx["name"]
                            for idx in insp.get_indexes(table_name)}
        index_name = f"ix_{table_name}_tenant"

        # Cria índice tenant se não existir
        if index_name not in existing_indexes:
            op.create_index(index_name, table_name, ["codemp", "codfil"])
            print(f"✅ Criado índice '{index_name}' na tabela {table_name}")
        else:
            print(
                f"⚠️  Índice '{index_name}' já existe na tabela {table_name}")

    # Lista de tabelas que precisam ser verificadas/ajustadas
    tables_to_check = [
        "rfe997par",    # Parâmetros
        "rfe996mod",    # Módulos
        "rfe990dir",    # Direitos
        "rfe990dus",    # Direitos x Usuário
        "rfe000cfg",    # Configurações
    ]

    print("🔧 Iniciando ajuste de colunas tenant (codemp/codfil)...")

    for table in tables_to_check:
        try:
            # Verifica se a tabela existe antes de tentar modificá-la
            if insp.has_table(table):
                print(f"\n📋 Processando tabela: {table}")
                ensure_tenant_columns_and_index(table)
            else:
                print(f"❌ Tabela {table} não encontrada no banco")
        except Exception as e:
            print(f"❌ Erro ao processar tabela {table}: {str(e)}")
            raise

    print("\n🎉 Migração concluída com sucesso!")


def downgrade():
    """
    Remove as colunas codemp e codfil das tabelas onde foram adicionadas,
    verificando antes se existem para evitar erros.
    """
    bind = op.get_bind()
    insp = Inspector.from_engine(bind)

    def remove_tenant_columns_and_index(table_name):
        """Remove codemp, codfil e índice tenant se existirem"""
        # Verifica índices existentes
        existing_indexes = {idx["name"]
                            for idx in insp.get_indexes(table_name)}
        index_name = f"ix_{table_name}_tenant"

        # Remove índice se existir
        if index_name in existing_indexes:
            op.drop_index(index_name, table_name=table_name)
            print(f"✅ Removido índice '{index_name}' da tabela {table_name}")

        # Verifica colunas existentes
        existing_columns = {col["name"]
                            for col in insp.get_columns(table_name)}

        # Remove codfil se existir
        if "codfil" in existing_columns:
            op.drop_column(table_name, "codfil")
            print(f"✅ Removida coluna 'codfil' da tabela {table_name}")

        # Remove codemp se existir
        if "codemp" in existing_columns:
            op.drop_column(table_name, "codemp")
            print(f"✅ Removida coluna 'codemp' da tabela {table_name}")

    # Lista de tabelas para reverter (mesma ordem do upgrade)
    tables_to_revert = [
        "rfe997par",
        "rfe996mod",
        "rfe990dir",
        "rfe990dus",
        "rfe000cfg",
    ]

    print("🔄 Iniciando reversão de colunas tenant...")

    for table in tables_to_revert:
        try:
            if insp.has_table(table):
                print(f"\n📋 Revertendo tabela: {table}")
                remove_tenant_columns_and_index(table)
            else:
                print(f"❌ Tabela {table} não encontrada no banco")
        except Exception as e:
            print(f"❌ Erro ao reverter tabela {table}: {str(e)}")
            raise

    print("\n🎉 Reversão concluída com sucesso!")
