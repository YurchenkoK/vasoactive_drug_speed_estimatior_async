from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drugs_estimation', '0002_remove_async_calculation_result'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Order',
            new_name='EstimationRequest',
        ),
        migrations.RenameModel(
            old_name='DrugInOrder',
            new_name='DrugInEstimation',
        ),
        migrations.RenameField(
            model_name='druginestimation',
            old_name='order',
            new_name='estimation_request',
        ),
        migrations.AlterUniqueTogether(
            name='druginestimation',
            unique_together={('estimation_request', 'drug')},
        ),
    ]
