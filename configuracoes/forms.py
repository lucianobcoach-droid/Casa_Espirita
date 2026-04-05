from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, UserChangeForm, UserCreationForm

from .models import PerfilAcesso


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


class UsuarioAdminBaseFormMixin:
    """Regras V1 de e-mail e perfil-base para operacao de usuarios no admin."""

    perfil_base = forms.ModelChoiceField(
        label='Perfil base',
        queryset=PerfilAcesso.objects.filter(ativo=True).order_by('nome'),
        required=False,
        help_text=(
            'Obrigatorio para usuario funcional ativo. '
            'Superusuario tecnico pode ficar sem perfil, mas sem acesso funcional.'
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vinculo = getattr(getattr(self.instance, 'vinculo_perfil_acesso', None), 'perfil', None)
        if vinculo is not None:
            self.fields['perfil_base'].initial = vinculo
        if 'email' in self.fields:
            self.fields['email'].required = False
            self.fields['email'].help_text = 'Obrigatorio para usuarios ativos ou administradores tecnicos.'

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()

        if email:
            conflito = (
                get_user_model()
                .objects.exclude(pk=self.instance.pk)
                .filter(email__iexact=email)
                .exists()
            )
            if conflito:
                raise forms.ValidationError(
                    'Ja existe outro usuario com este e-mail. Use um e-mail unico para o acesso.'
                )

        return email

    def clean(self):
        cleaned_data = super().clean()
        email = (cleaned_data.get('email') or '').strip()
        email_informado = (self.data.get('email') or '').strip()
        perfil_base = cleaned_data.get('perfil_base')
        is_active = cleaned_data.get('is_active')
        is_staff = cleaned_data.get('is_staff')
        is_superuser = cleaned_data.get('is_superuser')

        if (is_active or is_staff or is_superuser) and not email_informado:
            self.add_error(
                'email',
                'Informe um e-mail valido para usuarios ativos ou administradores tecnicos.',
            )

        if is_active and not is_staff and not is_superuser and perfil_base is None:
            self.add_error(
                'perfil_base',
                'Usuario funcional ativo precisa de um perfil base. '
                'Se for apenas um acesso tecnico, use um administrador tecnico sem perfil funcional.',
            )

        return cleaned_data


class ConfiguracoesUserCreationForm(UsuarioAdminBaseFormMixin, UserCreationForm):
    """Formulario de criacao de usuario com regras minimas de acesso."""

    perfil_base = UsuarioAdminBaseFormMixin.perfil_base

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'is_staff',
            'is_superuser',
        )


class ConfiguracoesUserChangeForm(UsuarioAdminBaseFormMixin, UserChangeForm):
    """Formulario de edicao de usuario com regras minimas de acesso."""

    perfil_base = UsuarioAdminBaseFormMixin.perfil_base

    class Meta(UserChangeForm.Meta):
        model = get_user_model()
        fields = '__all__'
