from __future__ import annotations

from django import forms
from django.contrib.auth.forms import PasswordResetForm


class ConfiguracoesPasswordResetForm(PasswordResetForm):
    """Formulario de reset com validacao explicita de e-mail utilizavel."""

    error_messages = {
        'email_nao_encontrado': 'Nao encontramos um usuario ativo com este e-mail.',
    }

    def clean_email(self):
        email = self.cleaned_data['email']
        usuarios = list(self.get_users(email))
        if not usuarios:
            raise forms.ValidationError(
                self.error_messages['email_nao_encontrado'],
                code='email_nao_encontrado',
            )
        return email
