# Generated migration - combined initial setup
import django.db.models.deletion
from django.db import migrations, models

from ._backup_data import restore_from_backup


def populate_descriptions(apps, schema_editor):
    Drug = apps.get_model('drugs_estimation', 'Drug')
    descriptions = {
        'Допамин': 'Применяется при шоковых состояниях и острой сердечной недостаточности.',
        'Норадреналин': 'Используется при выраженной артериальной гипотензии и септическом шоке.',
        'Адреналин': 'Показан при анафилактическом шоке, остановке сердца и тяжёлых аллергических реакциях.',
        'Добутамин': 'Применяется при острой сердечной недостаточности и кардиогенном шоке.',
        'Фенилэфрин': 'Используется при симптоматической артериальной гипотензии.',
        'Эпинефрин': 'Альтернативное название — адреналин; применяется при анафилаксии.',
        'Изопреналин': 'Применяется при брадикардии и некоторых формах блокады сердца.',
        'Милринон': 'Применяется при острой декомпенсации сердечной недостаточности.',
        'Левосимендан': 'Используют при острой и хронической сердечной недостаточности.',
        'Нитроглицерин': 'Применяется для сужения боли в грудной клетке при ишемии.',
        'Нитропруссид': 'Используется при гипертонических кризах.',
        'Эсмолол': 'Короткодействующий бета-блокатор, применяемый при тахикардии.',
        'Метопролол': 'Бета-блокатор, используемый при артериальной гипертензии.',
        'Верапамил': 'Кальциевый антагонист, применяемый при суправентрикулярной тахикардии.',
    }
    for name, text in descriptions.items():
        qs = Drug.objects.filter(name=name)
        for obj in qs:
            if not obj.description or str(obj.description).strip() == '':
                obj.description = text
                obj.save()


def backwards_descriptions(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    
    operations = [
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Показания')),
                ('image_url', models.URLField(blank=True, max_length=500, null=True, verbose_name='URL изображения')),
                ('concentration', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Концентрация (мг/мл)')),
                ('volume', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Объём ампулы (мл)')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
            ],
            options={
                'verbose_name': 'Препарат',
                'verbose_name_plural': 'Препараты',
                'db_table': 'drugs',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creator', models.CharField(max_length=150, verbose_name='Создатель (username)')),
                ('moderator', models.CharField(blank=True, max_length=150, null=True, verbose_name='Модератор (username)')),
                ('status', models.CharField(choices=[('DRAFT', 'Черновик'), ('DELETED', 'Удалён'), ('FORMED', 'Сформирован'), ('COMPLETED', 'Завершён'), ('REJECTED', 'Отклонён')], default='DRAFT', max_length=10, verbose_name='Статус')),
                ('creation_datetime', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('formation_datetime', models.DateTimeField(blank=True, null=True, verbose_name='Дата формирования')),
                ('completion_datetime', models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения')),
                ('ampoules_count', models.IntegerField(blank=True, null=True, verbose_name='Количество ампул')),
                ('solvent_volume', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Объём растворителя (мл)')),
                ('patient_weight', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Масса пациента (кг)')),
            ],
            options={
                'verbose_name': 'Заявка',
                'verbose_name_plural': 'Заявки',
                'db_table': 'estimation_request',
                'ordering': ['-creation_datetime'],
            },
        ),
        migrations.CreateModel(
            name='DrugInOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ampoule_volume', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Объём ампулы (мл)')),
                ('infusion_speed', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Скорость введения (мг/кг/час)')),
                ('async_calculation_result', models.CharField(blank=True, max_length=100, null=True, verbose_name='Результат асинхронного расчета')),
                ('drug', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='drugs_estimation.drug', verbose_name='Препарат')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='drugs_estimation.order', verbose_name='Заявка')),
            ],
            options={
                'verbose_name': 'Препарат в заявке',
                'verbose_name_plural': 'Препараты в заявках',
                'db_table': 'drug_in_estimation',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='drugs',
            field=models.ManyToManyField(through='drugs_estimation.DrugInOrder', to='drugs_estimation.drug', verbose_name='Препараты'),
        ),
        migrations.AlterUniqueTogether(
            name='druginorder',
            unique_together={('order', 'drug')},
        ),
        migrations.RunPython(populate_descriptions, backwards_descriptions),
        migrations.RunPython(restore_from_backup, migrations.RunPython.noop),
    ]
