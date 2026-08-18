#!/bin/bash

echo "=== Знайомство ==="

read -p "Як тебе звати? " name

if [ -z "$name" ]; then
    name="незнайомець"
fi

read -p "Скільки тобі років? $name, вкажи число: " age

if ! [[ "$age" =~ ^[0-9]+$ ]]; then
    echo "Це не схоже на число. Наступного разу введи, наприклад, 12."
    exit 1
fi

year=$(date +%Y)
born=$((year - age))

echo
echo "Привіт, $name!"
echo "Тобі $age років, отже ти народився приблизно у $born році."

if [ "$age" -lt 18 ]; then
    echo "Ти ще школяр — саме час вчити Python."
else
    echo "Дорослий програміст — теж чудово!"
fi
