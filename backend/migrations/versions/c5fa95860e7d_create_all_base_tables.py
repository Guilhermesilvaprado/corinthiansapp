from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250926_create_all_base_tables"
down_revision = "b7f4cb2c516e"
branch_labels = None
depends_on = None


def upgrade():
    # RFE000EMP - Empresa
    op.create_table(
        "rfe000emp",
        sa.Column("codemp", sa.Integer(), nullable=False),
        sa.Column("nomemp", sa.String(length=100), nullable=False),
        sa.Column("fanemp", sa.String(length=100), nullable=True),
        sa.Column("endemp", sa.String(length=100), nullable=True),
        sa.Column("numemp", sa.String(length=10), nullable=True),
        sa.Column("baiemp", sa.String(length=50), nullable=True),
        sa.Column("cplemp", sa.String(length=50), nullable=True),
        sa.Column("cepemp", sa.String(length=9), nullable=True),
        sa.Column("telemp", sa.String(length=15), nullable=True),
        sa.Column("faxemp", sa.String(length=15), nullable=True),
        sa.Column("celemp", sa.String(length=16), nullable=True),
        sa.Column("recemp", sa.String(length=15), nullable=True),
        sa.Column("obsemp", sa.String(length=1000), nullable=True),
        sa.Column("cnpemp", sa.String(length=18), nullable=True),
        sa.Column("iesemp", sa.String(length=18), nullable=True),
        sa.Column("estemp", sa.String(length=2), nullable=True),
        sa.Column("cidemp", sa.String(length=100), nullable=True),
        sa.Column("sitemp", sa.String(length=7), nullable=True),
        sa.Column("dtacad", sa.Date(), nullable=True),
        sa.Column("dtaalt", sa.Date(), nullable=True),
        sa.Column("tipseg", sa.Integer(), nullable=True),
        sa.Column("em1emp", sa.String(length=500), nullable=True),
        sa.Column("em2emp", sa.String(length=500), nullable=True),
        sa.Column("conemp", sa.String(length=50), nullable=True),
        sa.Column("cpfemp", sa.String(length=11), nullable=True),
        sa.Column("imgemp", sa.String(length=500), nullable=True),
        sa.Column("codfil", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("codemp", name="pk_rfe000emp"),
    )
    op.create_index("ix_rfe000emp_sitemp", "rfe000emp", ["sitemp"])
    op.create_index("ix_rfe000emp_cidade_uf",
                    "rfe000emp", ["cidemp", "estemp"])

    # RFE000FIL - Filial (PK composta + FK para EMP)
    op.create_table(
        "rfe000fil",
        sa.Column("codfil", sa.Integer(), nullable=False),
        sa.Column("codemp", sa.Integer(), nullable=False),
        sa.Column("nomfil", sa.String(length=100), nullable=False),
        sa.Column("fanfil", sa.String(length=100), nullable=True),
        sa.Column("endfil", sa.String(length=100), nullable=True),
        sa.Column("numfil", sa.String(length=10), nullable=True),
        sa.Column("baifil", sa.String(length=50), nullable=True),
        sa.Column("cplfil", sa.String(length=50), nullable=True),
        sa.Column("cepfil", sa.String(length=9), nullable=True),
        sa.Column("telfil", sa.String(length=15), nullable=True),
        sa.Column("faxfil", sa.String(length=15), nullable=True),
        sa.Column("celfil", sa.String(length=16), nullable=True),
        sa.Column("recfil", sa.String(length=15), nullable=True),
        sa.Column("obsfil", sa.String(length=1000), nullable=True),
        sa.Column("cnpfil", sa.String(length=18), nullable=True),
        sa.Column("iesfil", sa.String(length=18), nullable=True),
        sa.Column("estfil", sa.String(length=2), nullable=True),
        sa.Column("cidfil", sa.String(length=100), nullable=True),
        sa.Column("sitfil", sa.String(length=7), nullable=True),
        sa.Column("dtacad", sa.Date(), nullable=True),
        sa.Column("dtaalt", sa.Date(), nullable=True),
        sa.Column("tipseg", sa.Integer(), nullable=True),
        sa.Column("em1fil", sa.String(length=500), nullable=True),
        sa.Column("em2fil", sa.String(length=500), nullable=True),
        sa.Column("confil", sa.String(length=50), nullable=True),
        sa.Column("cpffil", sa.String(length=11), nullable=True),
        sa.Column("imgfil", sa.String(length=500), nullable=True),
        sa.Column("pagfil", sa.String(length=500), nullable=True),
        sa.Column("codibg", sa.String(length=10), nullable=True),
        sa.Column("codcuf", sa.Integer(), nullable=True),
        sa.Column("numcer", sa.String(length=32), nullable=True),
        sa.Column("codcrt", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("codemp", "codfil", name="pk_rfe000fil"),
        sa.ForeignKeyConstraint(
            ["codemp"], ["rfe000emp.codemp"], name="fk_rfe000fil_emp", ondelete="RESTRICT"),
    )
    op.create_index("ix_rfe000fil_tenant", "rfe000fil", ["codemp", "sitfil"])

    # RFE998USU - Usuário
    op.create_table(
        "rfe998usu",
        sa.Column("codusu", sa.Integer(), nullable=False),
        sa.Column("nomusu", sa.String(length=100), nullable=False),
        sa.Column("logusu", sa.String(length=100), nullable=True),
        sa.Column("pwdusu", sa.String(length=255),
                  nullable=True),  # aumentado para hash
        sa.Column("emausu", sa.String(length=200), nullable=True),
        sa.Column("situsu", sa.String(length=8), nullable=True),
        sa.Column("setusu", sa.Integer(), nullable=True),
        sa.Column("codemp", sa.Integer(), nullable=True),
        sa.Column("codfil", sa.Integer(), nullable=True),
        sa.Column("codpes", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("codusu", name="pk_rfe998usu"),
    )
    op.create_index("i998usu_codusu", "rfe998usu", ["codusu"])
    op.create_index("ix_rfe998usu_tenant", "rfe998usu", ["codemp", "codfil"])
    op.create_index("i998usu_logusu", "rfe998usu", ["logusu"], unique=True)

    # RFE000PPT - Proprietária
    op.create_table(
        "rfe000ppt",
        sa.Column("codppt", sa.Integer(), nullable=False),
        sa.Column("nomppt", sa.String(length=100), nullable=False),
        sa.Column("fanppt", sa.String(length=100), nullable=True),
        sa.Column("endppt", sa.String(length=100), nullable=True),
        sa.Column("numppt", sa.String(length=10), nullable=True),
        sa.Column("baippt", sa.String(length=50), nullable=True),
        sa.Column("cplppt", sa.String(length=50), nullable=True),
        sa.Column("cepppt", sa.String(length=9), nullable=True),
        sa.Column("telppt", sa.String(length=15), nullable=True),
        sa.Column("faxppt", sa.String(length=15), nullable=True),
        sa.Column("celppt", sa.String(length=16), nullable=True),
        sa.Column("recppt", sa.String(length=15), nullable=True),
        sa.Column("obsppt", sa.String(length=1000), nullable=True),
        sa.Column("cnpppt", sa.String(length=18), nullable=True),
        sa.Column("iesppt", sa.String(length=18), nullable=True),
        sa.Column("estppt", sa.String(length=2), nullable=True),
        sa.Column("cidppt", sa.String(length=100), nullable=True),
        sa.Column("sitppt", sa.String(length=7), nullable=True),
        sa.Column("dtacad", sa.Date(), nullable=True),
        sa.Column("dtaalt", sa.Date(), nullable=True),
        sa.Column("tipseg", sa.Integer(), nullable=True),
        sa.Column("em1ppt", sa.String(length=500), nullable=True),
        sa.Column("em2ppt", sa.String(length=500), nullable=True),
        sa.Column("licppt", sa.String(length=20), nullable=True),
        sa.Column("vallic", sa.Date(), nullable=True),
        sa.Column("conppt", sa.String(length=50), nullable=True),
        sa.Column("cpfppt", sa.String(length=11), nullable=True),
        sa.Column("codfil", sa.Integer(), nullable=True),
        sa.Column("codemp", sa.Integer(), nullable=True),
        sa.Column("imgppt", sa.String(length=400), nullable=True),
        sa.Column("qtdemp", sa.Integer(), nullable=True),
        sa.Column("qtdfil", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("codppt", name="pk_rfe000ppt"),
    )
    op.create_index("i000ppt_codemp", "rfe000ppt", ["codemp"], unique=True)
    op.create_index("i000ppt_codfil", "rfe000ppt", ["codfil"], unique=True)

    # RFE997PAR - Parâmetros
    op.create_table(
        "rfe997par",
        sa.Column("codpar", sa.Integer(), nullable=False),
        sa.Column("despar", sa.String(length=100), nullable=False),
        sa.Column("sitpar", sa.String(length=7), nullable=True),
        sa.Column("sispar", sa.String(length=1), nullable=True),
        sa.PrimaryKeyConstraint("codpar", name="pk_rfe997par"),
    )

    # RFE996MOD - Módulos
    op.create_table(
        "rfe996mod",
        sa.Column("codmod", sa.Integer(), nullable=False),
        sa.Column("nmmenu", sa.String(length=100), nullable=False),
        sa.Column("acesso", sa.String(length=9), nullable=True),
        sa.Column("nommod", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("codmod", name="pk_rfe996mod"),
    )

    # RFE990DIR - Direitos
    op.create_table(
        "rfe990dir",
        sa.Column("coddir", sa.Integer(), nullable=False),
        sa.Column("desdir", sa.String(length=100), nullable=False),
        sa.Column("catdir", sa.String(length=10), nullable=True),
        sa.PrimaryKeyConstraint("coddir", name="pk_rfe990dir"),
    )

    # RFE990DUS - Direitos x Usuário (tabela de associação)
    op.create_table(
        "rfe990dus",
        sa.Column("codusu", sa.Integer(), nullable=False),
        sa.Column("coddir", sa.String(length=100),
                  nullable=False),  # Note: VARCHAR no seu DDL
        sa.PrimaryKeyConstraint("codusu", "coddir", name="pk_rfe990dus"),
        sa.ForeignKeyConstraint(
            ["codusu"], ["rfe998usu.codusu"], name="fk_rfe990dus_usu", ondelete="CASCADE"),
        # FK para RFE990DIR seria ideal, mas CODDIR é INTEGER lá e VARCHAR(100) aqui
        # Ajuste conforme necessário se quiser manter consistência
    )

    # RFE000CFG - Configurações (estrutura básica, ajuste conforme necessário)
    op.create_table(
        "rfe000cfg",
        sa.Column("codcfg", sa.Integer(), nullable=False),
        sa.Column("descfg", sa.String(length=100), nullable=False),
        sa.Column("valcfg", sa.String(length=500), nullable=True),
        # STRING, INTEGER, BOOLEAN, etc.
        sa.Column("tipcfg", sa.String(length=10), nullable=True),
        sa.Column("codemp", sa.Integer(), nullable=True),
        sa.Column("codfil", sa.Integer(), nullable=True),
        sa.Column("sitcfg", sa.String(length=7), nullable=True),
        sa.Column("dtacad", sa.Date(), nullable=True),
        sa.Column("dtaalt", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("codcfg", name="pk_rfe000cfg"),
    )
    op.create_index("ix_rfe000cfg_tenant", "rfe000cfg", ["codemp", "codfil"])


def downgrade():
    # Drop na ordem reversa das dependências
    op.drop_index("ix_rfe000cfg_tenant", table_name="rfe000cfg")
    op.drop_table("rfe000cfg")

    op.drop_table("rfe990dus")
    op.drop_table("rfe990dir")
    op.drop_table("rfe996mod")
    op.drop_table("rfe997par")

    op.drop_index("i000ppt_codfil", table_name="rfe000ppt")
    op.drop_index("i000ppt_codemp", table_name="rfe000ppt")
    op.drop_table("rfe000ppt")

    op.drop_index("i998usu_logusu", table_name="rfe998usu")
    op.drop_index("ix_rfe998usu_tenant", table_name="rfe998usu")
    op.drop_index("i998usu_codusu", table_name="rfe998usu")
    op.drop_table("rfe998usu")

    op.drop_index("ix_rfe000fil_tenant", table_name="rfe000fil")
    op.drop_table("rfe000fil")

    op.drop_index("ix_rfe000emp_cidade_uf", table_name="rfe000emp")
    op.drop_index("ix_rfe000emp_sitemp", table_name="rfe000emp")
    op.drop_table("rfe000emp")
