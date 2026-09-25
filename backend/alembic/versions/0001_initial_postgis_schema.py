"""Initial PostGIS schema for SIH 2026 Disaster Management

Revision ID: 0001_initial_postgis_schema
Revises: 
Create Date: 2026-09-25 12:57:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = '0001_initial_postgis_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable PostGIS Extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")

    # 2. Habitations Table
    op.create_table(
        'habitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('district', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('population', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('vulnerable_population', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='GEOMETRY', srid=4326, spatial_index=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_habitations_id', 'habitations', ['id'])
    op.create_index('idx_habitations_name', 'habitations', ['name'])
    op.create_index('idx_habitations_district', 'habitations', ['district'])
    op.create_index('idx_habitations_state', 'habitations', ['state'])
    op.create_index('idx_habitations_district_state', 'habitations', ['district', 'state'])
    op.create_index('idx_habitations_geometry', 'habitations', ['geometry'], postgresql_using='gist')

    # 3. Hazard Zones Table
    op.create_table(
        'hazard_zones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('hazard_type', sa.String(length=50), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='GEOMETRY', srid=4326, spatial_index=False), nullable=False),
    )
    op.create_index('idx_hazard_zones_id', 'hazard_zones', ['id'])
    op.create_index('idx_hazard_zones_type', 'hazard_zones', ['hazard_type'])
    op.create_index('idx_hazard_zones_severity', 'hazard_zones', ['severity'])
    op.create_index('idx_hazard_zones_timestamp', 'hazard_zones', ['timestamp'])
    op.create_index('idx_hazard_zones_type_severity', 'hazard_zones', ['hazard_type', 'severity'])
    op.create_index('idx_hazard_zones_time_type', 'hazard_zones', ['timestamp', 'hazard_type'])
    op.create_index('idx_hazard_zones_geometry', 'hazard_zones', ['geometry'], postgresql_using='gist')

    # 4. Rainfall Observations Table
    op.create_table(
        'rainfall_observations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('rainfall_mm', sa.Float(), nullable=False),
        sa.Column('observation_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, spatial_index=False), nullable=True),
    )
    op.create_index('idx_rainfall_id', 'rainfall_observations', ['id'])
    op.create_index('idx_rainfall_time', 'rainfall_observations', ['observation_time'])
    op.create_index('idx_rainfall_time_source', 'rainfall_observations', ['observation_time', 'source'])
    op.create_index('idx_rainfall_geometry', 'rainfall_observations', ['geometry'], postgresql_using='gist')

    # 5. River Observations Table
    op.create_table(
        'river_observations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('station_name', sa.String(length=150), nullable=False),
        sa.Column('water_level', sa.Float(), nullable=False),
        sa.Column('danger_level', sa.Float(), nullable=False),
        sa.Column('observation_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, spatial_index=False), nullable=False),
    )
    op.create_index('idx_river_id', 'river_observations', ['id'])
    op.create_index('idx_river_station', 'river_observations', ['station_name'])
    op.create_index('idx_river_time', 'river_observations', ['observation_time'])
    op.create_index('idx_river_station_time', 'river_observations', ['station_name', 'observation_time'])
    op.create_index('idx_river_geometry', 'river_observations', ['geometry'], postgresql_using='gist')

    # 6. Disaster Events Table
    op.create_table(
        'disaster_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('disaster_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('event_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='GEOMETRY', srid=4326, spatial_index=False), nullable=False),
    )
    op.create_index('idx_disaster_id', 'disaster_events', ['id'])
    op.create_index('idx_disaster_type', 'disaster_events', ['disaster_type'])
    op.create_index('idx_disaster_severity', 'disaster_events', ['severity'])
    op.create_index('idx_disaster_time', 'disaster_events', ['event_time'])
    op.create_index('idx_disaster_type_time', 'disaster_events', ['disaster_type', 'event_time'])
    op.create_index('idx_disaster_geometry', 'disaster_events', ['geometry'], postgresql_using='gist')

    # 7. Relocation Sites Table
    op.create_table(
        'relocation_sites',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('available_area', sa.Float(), nullable=False),
        sa.Column('current_population', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('estimated_capacity', sa.Integer(), nullable=False),
        sa.Column('available_capacity', sa.Integer(), nullable=False),
        sa.Column('water_score', sa.Float(), nullable=False),
        sa.Column('road_access_score', sa.Float(), nullable=False),
        sa.Column('healthcare_score', sa.Float(), nullable=False),
        sa.Column('hazard_score', sa.Float(), nullable=False),
        sa.Column('suitability_score', sa.Float(), nullable=False),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='GEOMETRY', srid=4326, spatial_index=False), nullable=False),
    )
    op.create_index('idx_relocation_sites_id', 'relocation_sites', ['id'])
    op.create_index('idx_relocation_sites_name', 'relocation_sites', ['name'])
    op.create_index('idx_relocation_sites_capacity', 'relocation_sites', ['available_capacity'])
    op.create_index('idx_relocation_sites_suitability', 'relocation_sites', ['suitability_score'])
    op.create_index('idx_relocation_sites_geometry', 'relocation_sites', ['geometry'], postgresql_using='gist')

    # 8. Relocation Recommendations Table
    op.create_table(
        'relocation_recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('habitation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('habitations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relocation_site_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('relocation_sites.id', ondelete='CASCADE'), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('priority_score', sa.Float(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_recs_id', 'relocation_recommendations', ['id'])
    op.create_index('idx_recs_habitation', 'relocation_recommendations', ['habitation_id'])
    op.create_index('idx_recs_site', 'relocation_recommendations', ['relocation_site_id'])
    op.create_index('idx_recs_priority', 'relocation_recommendations', ['priority'])
    op.create_index('idx_recs_created_at', 'relocation_recommendations', ['created_at'])
    op.create_index('idx_recs_priority_score', 'relocation_recommendations', ['priority', 'priority_score'])


def downgrade() -> None:
    op.drop_table('relocation_recommendations')
    op.drop_table('relocation_sites')
    op.drop_table('disaster_events')
    op.drop_table('river_observations')
    op.drop_table('rainfall_observations')
    op.drop_table('hazard_zones')
    op.drop_table('habitations')
