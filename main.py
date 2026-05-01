import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# Настройки
API_KEY = "YOUR_API_KEY"  # Замените на свой ключ
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
HISTORY_FILE = "history.json"

# Загрузка истории
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

# Сохранение истории
def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

# Получение списка валют
def get_currencies():
    try:
        response = requests.get(API_URL)
        data = response.json()
        return list(data["conversion_rates"].keys())
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить валюты: {e}")
        return ["USD", "EUR", "RUB"]

# Конвертация
def convert():
    from_curr = from_var.get()
    to_curr = to_var.get()
    try:
        amount = float(amount_entry.get())
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Ошибка", "Введите положительное число!")
        return

    try:
        response = requests.get(f"{API_URL}/{from_curr}")
        data = response.json()
        rate = data["conversion_rates"][to_curr]
        result = amount * rate

        result_label.config(text=f"{amount} {from_curr} = {result:.2f} {to_curr}")

        # Сохраняем в историю
        history = load_history()
        history.append({
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "result": result,
            "rate": rate,
            "date": data["time_last_update_utc"]
        })
        save_history(history)
        update_history_table()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось выполнить конвертацию: {e}")

# Обновление таблицы истории
def update_history_table():
    for i in history_treeview.get_children():
        history_treeview.delete(i)
    for item in load_history():
        history_treeview.insert("", "end", values=(
            item["from"],
            item["to"],
            item["amount"],
            item["result"],
            item["rate"],
            item["date"]
        ))

# Создание окна
root = tk.Tk()
root.title("Currency Converter")
root.geometry("600x500")

# Виджеты
tk.Label(root, text="Из:").grid(row=0, column=0, padx=10, pady=10)
tk.Label(root, text="В:").grid(row=1, column=0, padx=10, pady=10)
tk.Label(root, text="Сумма:").grid(row=2, column=0, padx=10, pady=10)

currencies = get_currencies()
from_var = tk.StringVar(value="USD")
to_var = tk.StringVar(value="EUR")
amount_entry = tk.Entry(root)

from_menu = ttk.OptionMenu(root, from_var, *currencies)
to_menu = ttk.OptionMenu(root, to_var, *currencies)

from_menu.grid(row=0, column=1, padx=10, pady=10)
to_menu.grid(row=1, column=1, padx=10, pady=10)
amount_entry.grid(row=2, column=1, padx=10, pady=10)

convert_btn = tk.Button(root, text="Конвертировать", command=convert)
convert_btn.grid(row=3, column=0, columnspan=2, pady=10)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.grid(row=4, column=0, columnspan=2, pady=10)

# Таблица истории
history_treeview = ttk.Treeview(root, columns=("From", "To", "Amount", "Result", "Rate", "Date"), show="headings")
for col in history_treeview["columns"]:
    history_treeview.heading(col, text=col)
    history_treeview.column(col, width=80)
history_treeview.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

update_history_table()

root.mainloop()
 
