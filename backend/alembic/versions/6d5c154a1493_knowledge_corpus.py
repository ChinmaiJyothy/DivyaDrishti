"""Knowledge Corpus, candidate rules, review audit log, and knowledge graph

Revision ID: 6d5c154a1493
Revises: f85818966903
Create Date: 2026-07-14 17:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '6d5c154a1493'
down_revision: Union[str, None] = 'f85818966903'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'corpora',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('corpus_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('authority_weight', sa.Float(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_corpora_id'), 'corpora', ['id'], unique=False)
    op.create_index(op.f('ix_corpora_slug'), 'corpora', ['slug'], unique=True)

    with op.batch_alter_table('uploaded_books') as batch_op:
        batch_op.add_column(sa.Column('corpus_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('publisher', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('edition', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('isbn', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('publication_year', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('source', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('ingestion_report_json', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.create_index(op.f('ix_uploaded_books_corpus_id'), ['corpus_id'], unique=False)
        batch_op.create_foreign_key(
            'fk_uploaded_books_corpus_id', 'corpora', ['corpus_id'], ['id']
        )

    op.create_table(
        'candidate_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_rule_id', sa.String(length=100), nullable=False),
        sa.Column('corpus_id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('source_book_title', sa.String(length=255), nullable=False),
        sa.Column('language', sa.String(length=50), nullable=False),
        sa.Column('chapter', sa.String(length=100), nullable=True),
        sa.Column('verse', sa.String(length=100), nullable=True),
        sa.Column('page', sa.Integer(), nullable=True),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('translated_text', sa.Text(), nullable=True),
        sa.Column('topic', sa.String(length=100), nullable=False),
        sa.Column('subtopic', sa.String(length=100), nullable=True),
        sa.Column('astrological_factors_json', sa.JSON(), nullable=False),
        sa.Column('candidate_conditions_json', sa.JSON(), nullable=False),
        sa.Column('candidate_interpretation', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('chunk_id', sa.String(length=100), nullable=True),
        sa.Column('approved_rule_id', sa.String(length=100), nullable=True),
        sa.Column('merged_into_candidate_id', sa.Integer(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['corpus_id'], ['corpora.id']),
        sa.ForeignKeyConstraint(['book_id'], ['uploaded_books.id']),
        sa.ForeignKeyConstraint(['merged_into_candidate_id'], ['candidate_rules.id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_candidate_rules_id'), 'candidate_rules', ['id'], unique=False)
    op.create_index(
        op.f('ix_candidate_rules_candidate_rule_id'), 'candidate_rules', ['candidate_rule_id'], unique=True
    )
    op.create_index(op.f('ix_candidate_rules_corpus_id'), 'candidate_rules', ['corpus_id'], unique=False)
    op.create_index(op.f('ix_candidate_rules_book_id'), 'candidate_rules', ['book_id'], unique=False)
    op.create_index(op.f('ix_candidate_rules_status'), 'candidate_rules', ['status'], unique=False)
    op.create_index(op.f('ix_candidate_rules_chunk_id'), 'candidate_rules', ['chunk_id'], unique=False)

    op.create_table(
        'rule_review_audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('candidate_rule_id', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('previous_state_json', sa.JSON(), nullable=True),
        sa.Column('new_state_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['candidate_rule_id'], ['candidate_rules.id']),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_rule_review_audit_log_id'), 'rule_review_audit_log', ['id'], unique=False)
    op.create_index(
        op.f('ix_rule_review_audit_log_candidate_rule_id'),
        'rule_review_audit_log', ['candidate_rule_id'], unique=False,
    )
    op.create_index(
        op.f('ix_rule_review_audit_log_created_at'), 'rule_review_audit_log', ['created_at'], unique=False
    )

    op.create_table(
        'knowledge_graph_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('corpus_id', sa.Integer(), nullable=False),
        sa.Column('node_type', sa.String(length=50), nullable=False),
        sa.Column('ref_id', sa.String(length=255), nullable=False),
        sa.Column('label', sa.String(length=255), nullable=False),
        sa.Column('node_metadata_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['corpus_id'], ['corpora.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_knowledge_graph_nodes_id'), 'knowledge_graph_nodes', ['id'], unique=False)
    op.create_index(
        op.f('ix_knowledge_graph_nodes_corpus_id'), 'knowledge_graph_nodes', ['corpus_id'], unique=False
    )
    op.create_index(
        op.f('ix_knowledge_graph_nodes_node_type'), 'knowledge_graph_nodes', ['node_type'], unique=False
    )
    op.create_index(
        op.f('ix_knowledge_graph_nodes_ref_id'), 'knowledge_graph_nodes', ['ref_id'], unique=False
    )

    op.create_table(
        'knowledge_graph_edges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('corpus_id', sa.Integer(), nullable=False),
        sa.Column('source_node_id', sa.Integer(), nullable=False),
        sa.Column('target_node_id', sa.Integer(), nullable=False),
        sa.Column('relation', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['corpus_id'], ['corpora.id']),
        sa.ForeignKeyConstraint(['source_node_id'], ['knowledge_graph_nodes.id']),
        sa.ForeignKeyConstraint(['target_node_id'], ['knowledge_graph_nodes.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_knowledge_graph_edges_id'), 'knowledge_graph_edges', ['id'], unique=False)
    op.create_index(
        op.f('ix_knowledge_graph_edges_source_node_id'),
        'knowledge_graph_edges', ['source_node_id'], unique=False,
    )
    op.create_index(
        op.f('ix_knowledge_graph_edges_target_node_id'),
        'knowledge_graph_edges', ['target_node_id'], unique=False,
    )
    op.create_index(
        op.f('ix_knowledge_graph_edges_relation'), 'knowledge_graph_edges', ['relation'], unique=False
    )


def downgrade() -> None:
    op.drop_table('knowledge_graph_edges')
    op.drop_table('knowledge_graph_nodes')
    op.drop_table('rule_review_audit_log')
    op.drop_table('candidate_rules')

    with op.batch_alter_table('uploaded_books') as batch_op:
        batch_op.drop_constraint('fk_uploaded_books_corpus_id', type_='foreignkey')
        batch_op.drop_index(op.f('ix_uploaded_books_corpus_id'))
        batch_op.drop_column('processed_at')
        batch_op.drop_column('ingestion_report_json')
        batch_op.drop_column('source')
        batch_op.drop_column('publication_year')
        batch_op.drop_column('isbn')
        batch_op.drop_column('edition')
        batch_op.drop_column('publisher')
        batch_op.drop_column('corpus_id')

    op.drop_table('corpora')
