#!/usr/bin/env python
import os
import sys


def main() -> None:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'casa_espirita.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar Django. Certifique-se de que está instalado e disponível no ambiente."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
