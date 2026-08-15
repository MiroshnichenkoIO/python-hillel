#!/bin/bash
# Скрипт 2: створює заготовку Python-проєкту за назвою, яку ввів користувач.
# Показує: перевірку вводу, створення папок і файлів, питання «так/ні».
#
# Запуск:  bash new_project.sh

echo "=== Створення нового проєкту ==="

read -p "Назва проєкту: " project

if [ -z "$project" ]; then
    echo "Назва не може бути порожньою. Спробуй ще раз."
    exit 1
fi

# -d перевіряє «чи існує така папка»
if [ -d "$project" ]; then
    echo "Папка '$project' уже існує. Обери іншу назву."
    exit 1
fi

read -p "Створити папку для тестів tests/? (y/n) " answer

mkdir -p "$project"
touch "$project/main.py"
echo "# $project" > "$project/README.md"

if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    mkdir -p "$project/tests"
    touch "$project/tests/test_main.py"
    echo "Папку tests/ створено."
fi

echo
echo "Готово! Ось що вийшло:"
ls -R "$project"
echo
echo "Далі: cd $project && python -m venv venv"
