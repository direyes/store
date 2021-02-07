# Generated by Django 3.1.6 on 2021-02-07 20:49

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=140, verbose_name='name')),
                ('value', models.PositiveIntegerField(verbose_name='value')),
                ('image', models.FileField(upload_to='', verbose_name='image')),
            ],
            options={
                'verbose_name': 'product',
                'verbose_name_plural': 'products',
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tpaga_status', models.CharField(blank=True, max_length=140, null=True, verbose_name='tpaga status')),
                ('status', models.CharField(choices=[('new', 'new'), ('paid', 'paid'), ('reversed', 'reversed')], default='new', max_length=140, verbose_name='status')),
                ('idempotency_token', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='idempotency token')),
                ('payment_token', models.CharField(blank=True, max_length=140, null=True, verbose_name='payment token')),
                ('payment_url', models.CharField(blank=True, max_length=240, null=True, verbose_name='payment url')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='expires_at')),
            ],
            options={
                'verbose_name': 'purchase',
                'verbose_name_plural': 'purchases',
            },
        ),
        migrations.CreateModel(
            name='PurchaseItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(verbose_name='quantity')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='purchase.product', verbose_name='product')),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='purchase.purchase', verbose_name='purchase')),
            ],
            options={
                'verbose_name': 'purchase item',
                'verbose_name_plural': 'purchase items',
            },
        ),
        migrations.AddField(
            model_name='purchase',
            name='items',
            field=models.ManyToManyField(through='purchase.PurchaseItem', to='purchase.Product', verbose_name='items'),
        ),
    ]
