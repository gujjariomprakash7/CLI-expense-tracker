Expense Tracker

A simple command-line expense tracker written in Python. Expenses are saved to a JSON file, so they persist between runs. It uses only the Python standard library, so there is nothing to install.

Requirements
Python 3.6 or newer

Check your version with:

python --version
Usage

Run commands from the folder containing expenses.py:

python expenses.py <command>
Command	What it does
add <amount> <category>	Add an expense, e.g. add 250 food
list	Show all expenses with a total and the top 3 categories
total	Show the sum of all expenses
total <category>	Show the sum for one category, e.g. total food
clear	Delete all expenses (asks for confirmation)

Use python expenses.py clear -y to skip the confirmation prompt.

Example
$ python expenses.py add 250 food
Added ₹250.00 to 'food'.

$ python expenses.py add 1200.50 rent
Added ₹1,200.50 to 'rent'.

$ python expenses.py add 180 food
Added ₹180.00 to 'food'.

$ python expenses.py list
ID  Date              Category      Amount
------------------------------------------
 1  2026-11-25 14:19  food         ₹250.00
 2  2026-11-25 14:19  rent       ₹1,200.50
 3  2026-11-25 14:19  food         ₹180.00
------------------------------------------
Total (3 expenses)               ₹1,630.50

Top 3 categories by spending
  #   Category      Total   Share
  --  --------  ---------  ------
  1   rent      ₹1,200.50   73.6%
  2   food        ₹430.00   26.4%

$ python expenses.py total food
Total for 'food': ₹430.00 (2 expenses)
Notes
Categories are not case-sensitive: Food and food are treated as the same category.
Amounts must be positive numbers.
Data is stored in expenses.json next to the script. Use --file path.json or set the EXPENSES_FILE environment variable to store it somewhere else.
To change the currency symbol, edit the CURRENCY line near the top of expenses.py.
If the ₹ symbol looks garbled in Windows PowerShell, run chcp 65001 first.
Project files
expenses.py – the program
expenses.json – created automatically when you add your first expense
README.md – this file
