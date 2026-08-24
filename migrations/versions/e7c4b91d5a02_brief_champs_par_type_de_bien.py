"""Brief : des champs qui dependent du type de bien, et trois standings

Revision ID: e7c4b91d5a02
Revises: badf5ba02059
Create Date: 2026-08-22 10:12:03.114509

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7c4b91d5a02'
down_revision = 'badf5ba02059'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('briefs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('etat_local', sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column('nb_lots', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('viabilisation', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('topographie', sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column('zone_urbanisme', sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column('constructibilite', sa.String(length=60), nullable=True))

    # Cinq niveaux de standing sont ramenés à trois : les deux extrêmes se
    # plaidaient toujours par rapport aux autres. Les briefs déjà saisis sont
    # rapatriés vers le niveau voisin plutôt que vidés — un critère du client
    # ne se perd pas au passage d'une migration.
    op.execute("UPDATE briefs SET standing = 'Économique' WHERE standing = 'Social'")
    op.execute("UPDATE briefs SET standing = 'Haut standing' WHERE standing = 'Luxe'")

    # Un terrain n'a pas de standing, et ne s'achète ni construit ni sur plan :
    # les valeurs héritées du formulaire précédent n'ont pas d'objet.
    op.execute("UPDATE briefs SET standing = NULL WHERE type_bien = 'Terrain'")
    op.execute(
        "UPDATE briefs SET type_acquisition = 'terrain_nu' "
        "WHERE type_bien = 'Terrain' AND type_acquisition IN ('existant', 'vefa')"
    )


def downgrade():
    # Le standing d'origine — « social », « luxe » — n'est pas reconstituable :
    # la migration inverse rend les colonnes, pas les nuances perdues.
    with op.batch_alter_table('briefs', schema=None) as batch_op:
        batch_op.drop_column('constructibilite')
        batch_op.drop_column('zone_urbanisme')
        batch_op.drop_column('topographie')
        batch_op.drop_column('viabilisation')
        batch_op.drop_column('nb_lots')
        batch_op.drop_column('etat_local')

    op.execute(
        "UPDATE briefs SET type_acquisition = 'existant' "
        "WHERE type_acquisition IN ('terrain_nu', 'terrain_viabilise', "
        "'lot_lotissement', 'bail', 'neuf')"
    )
