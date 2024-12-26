# Generated by Django 3.2.15 on 2024-12-25 18:18

from django.db import migrations, models
import user.validators


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_user_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(db_index=True, error_messages={'unique': 'Пользователь с таким ником уже существует.'}, help_text='Введите свой email', max_length=254, unique=True, verbose_name='Электронная почта'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(db_index=True, error_messages={'unique': 'Пользователь с таким ником уже существует.'}, help_text="Допустимы только латинские буквы, цифры и символы @/./+/-/_. Имя пользователя 'me' использовать нельзя!", max_length=150, unique=True, validators=[user.validators.UsernameValidator(), user.validators.validate_username], verbose_name='Имя пользователя'),
        ),
    ]