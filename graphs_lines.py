import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

# Функция для создания линейного графика
def cr_diag_line_chart(df):
    # Подготовка данных для графика
    df['date'] = pd.to_datetime(df['date'])  # Приведение столбца даты к datetime
    df = df.pivot(index='date', columns='category', values='amount').fillna(0)
    
    # Построение линейного графика
    fig, ax = plt.subplots(figsize=(16, 9), dpi=80)
    df.plot(ax=ax, linewidth=2)
    
    # Настройка осей и легенды
    ax.legend(fontsize=10, ncol=4, title="Категории")
    ax.set_xlabel("Дата", fontsize=12)
    ax.set_ylabel("Сумма расходов", fontsize=12)
    plt.title("Динамика трат по категориям", fontsize=14)
    plt.xticks(fontsize=10, rotation=45)
    plt.yticks(fontsize=10)
    
    # Настройка стилей границ
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    plt.grid(alpha=0.3)  # Лёгкая сетка для удобства восприятия
    plt.tight_layout()
    plt.show()

# Параметры для SQL-запроса
user_id = 381360580
since_date = "2025-01-23 00:00:35"

# Подключение к базе данных
conn = sqlite3.connect('expenses.db', check_same_thread=False)

# SQL-запрос для получения данных
query = """
SELECT category, SUM(amount) as amount, date 
FROM expenses 
WHERE user_id = ? AND date >= ? 
GROUP BY category, date
ORDER BY date;
"""

df = pd.read_sql_query(query, conn, params=(user_id, since_date))

# Проверяем данные и строим график
if not df.empty:
    cr_diag_line_chart(df)
else:
    print("У вас нет записей за выбранный период.")
