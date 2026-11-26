from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='circle',
            name='topic_value_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='circle',
            name='featured_movies',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='circle',
            name='featured_cached_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
