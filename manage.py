#!/usr/bin/env python
import os
import sys

def main():
    # CAMBIO: Apuntar a 'core.settings.development' por defecto
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed...?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
