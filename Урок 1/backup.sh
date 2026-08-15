#!/bin/bash
# Приклад bash-скрипта з уроку: копіює папку проєкту в папку з сьогоднішньою датою.
# Запуск (Git Bash / macOS / Linux):
#   chmod +x backup.sh
#   ./backup.sh

echo "Резервне копіювання файлів..."
cp -r my_project "backup_$(date +%Y-%m-%d)"
echo "Готово!"
