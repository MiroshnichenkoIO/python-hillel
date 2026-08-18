#!/bin/bash

echo "=== Калькулятор ==="
echo "Для виходу введи q замість числа."

while true; do
    read -p $'\nПерше число: ' a || break

    if [ "$a" = "q" ]; then
        echo "Бувай!"
        break
    fi

    read -p "Друге число: " b || break

    if ! [[ "$a" =~ ^-?[0-9]+$ ]] || ! [[ "$b" =~ ^-?[0-9]+$ ]]; then
        echo "Потрібні цілі числа, спробуй ще раз."
        continue
    fi

    read -p "Дія (+ - * /): " op || break

    case "$op" in
        +) echo "Результат: $((a + b))" ;;
        -) echo "Результат: $((a - b))" ;;
        \*) echo "Результат: $((a * b))" ;;
        /)
            if [ "$b" -eq 0 ]; then
                echo "На нуль ділити не можна!"
            else
                echo "Результат: $((a / b)) (ціла частина), залишок: $((a % b))"
            fi
            ;;
        *) echo "Невідома дія '$op'. Доступні: + - * /" ;;
    esac
done
