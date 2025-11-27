# Combined initial migration
from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        # Tables ssr_inDb_drug, ssr_inDb_order, ssr_inDb_druginorder already exist
        # This is a fake migration to establish Django's migration baseline
        
        # Drop Django auth tables (not used with Redis auth)
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS "auth_user_user_permissions" CASCADE;',
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS "auth_user_groups" CASCADE;',
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS "auth_permission" CASCADE;',
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS "auth_group_permissions" CASCADE;',
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS "auth_group" CASCADE;',
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS "auth_user" CASCADE;',
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS "django_admin_log" CASCADE;',
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Drop empty duplicate tables created by Django
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS "stocks_druginorder" CASCADE;',
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS "stocks_order" CASCADE;',
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.RunSQL(
            sql='DROP TABLE IF EXISTS "stocks_drug" CASCADE;',
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Note: Columns creator_username and moderator_username already exist in database
    ]
