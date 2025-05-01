import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# Initialize the database

def initialize_database():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(Books)")
    # Create Books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Books (
            BookID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT NOT NULL,
            Author TEXT NOT NULL,
            Quantity INTEGER NOT NULL,
            IssuedCount INTEGER DEFAULT 0
        )
    ''')

    # Create IssuedBooks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS IssuedBooks (
            IssueID INTEGER PRIMARY KEY AUTOINCREMENT,
            BookID INTEGER NOT NULL,
            UserName TEXT NOT NULL,
            IssueDate TEXT NOT NULL,
            FOREIGN KEY (BookID) REFERENCES Books(BookID)
        )
    ''')

    conn.commit()
    conn.close()

# Add Book Window
def open_add_book_window():
    add_window = tk.Toplevel(root)
    add_window.title("Add Book")
    add_window.geometry("400x300")

    tk.Label(add_window, text="Title:").grid(row=0, column=0, pady=10, padx=10)
    book_title_entry = tk.Entry(add_window)
    book_title_entry.grid(row=0, column=1, pady=10, padx=10)

    tk.Label(add_window, text="Author:").grid(row=1, column=0, pady=10, padx=10)
    book_author_entry = tk.Entry(add_window)
    book_author_entry.grid(row=1, column=1, pady=10, padx=10)

    tk.Label(add_window, text="Quantity:").grid(row=2, column=0, pady=10, padx=10)
    book_quantity_entry = tk.Entry(add_window)
    book_quantity_entry.grid(row=2, column=1, pady=10, padx=10)

    def add_book():
        title = book_title_entry.get()
        author = book_author_entry.get()
        quantity = book_quantity_entry.get()

        if not title or not author or not quantity:
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Error", "Quantity must be an integer!")
            return

        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Books (Title, Author, Quantity) VALUES (?, ?, ?)", (title, author, quantity))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Book '{title}' added successfully!")
        book_title_entry.delete(0, tk.END)
        book_author_entry.delete(0, tk.END)
        book_quantity_entry.delete(0, tk.END)

    tk.Button(add_window, text="Add Book", command=add_book).grid(row=3, column=0, columnspan=2, pady=20)

# Issue Book Window
def open_issue_book_window():
    issue_window = tk.Toplevel(root)
    issue_window.title("Issue Book")
    issue_window.geometry("400x300")

    tk.Label(issue_window, text="Book ID:").grid(row=0, column=0, pady=10, padx=10)
    book_id_entry = tk.Entry(issue_window)
    book_id_entry.grid(row=0, column=1, pady=10, padx=10)

    tk.Label(issue_window, text="User Name:").grid(row=1, column=0, pady=10, padx=10)
    user_name_entry = tk.Entry(issue_window)
    user_name_entry.grid(row=1, column=1, pady=10, padx=10)

    def issue_book():
        book_id = book_id_entry.get()
        user_name = user_name_entry.get()

        if not book_id or not user_name:
            messagebox.showerror("Error", "All fields are required!")
            return

        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()

        cursor.execute("SELECT Quantity, IssuedCount FROM Books WHERE BookID = ?", (book_id,))
        book = cursor.fetchone()

        if book is None:
            messagebox.showerror("Error", "Book ID not found!")
            conn.close()
            return

        quantity, issued_count = book
        if issued_count < quantity:
            cursor.execute("INSERT INTO IssuedBooks (BookID, UserName, IssueDate) VALUES (?, ?, date('now'))", (book_id, user_name))
            cursor.execute("UPDATE Books SET IssuedCount = IssuedCount + 1 WHERE BookID = ?", (book_id,))
            conn.commit()
            messagebox.showinfo("Success", "Book issued successfully!")
        else:
            messagebox.showerror("Error", "No copies available!")

        conn.close()
        book_id_entry.delete(0, tk.END)
        user_name_entry.delete(0, tk.END)

    tk.Button(issue_window, text="Issue Book", command=issue_book).grid(row=2, column=0, columnspan=2, pady=20)

# View Books with Search
def open_view_books_window():
    view_window = tk.Toplevel(root)
    view_window.title("View Books")
    view_window.geometry("600x400")

    tk.Label(view_window, text="Search:").pack(pady=10)
    search_entry = tk.Entry(view_window)
    search_entry.pack(pady=10)

    book_list = ttk.Treeview(view_window, columns=("BookID", "Title", "Author", "Quantity", "IssuedCount"), show="headings")
    book_list.pack(fill=tk.BOTH, expand=True)
    for col in ("BookID", "Title", "Author", "Quantity", "IssuedCount"):
        book_list.heading(col, text=col)

    def search_books():
        search_term = search_entry.get()
        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Books WHERE Title LIKE ? OR Author LIKE ?", (f"%{search_term}%", f"%{search_term}%"))
        books = cursor.fetchall()
        conn.close()

        book_list.delete(*book_list.get_children())
        for book in books:
            book_list.insert("", tk.END, values=book)

    tk.Button(view_window, text="Search", command=search_books).pack(pady=10)

# Return Book
def open_return_book_window():
    return_window = tk.Toplevel(root)
    return_window.title("Return Book")
    return_window.geometry("400x300")

    tk.Label(return_window, text="Issue ID:").grid(row=0, column=0, pady=10, padx=10)
    issue_id_entry = tk.Entry(return_window)
    issue_id_entry.grid(row=0, column=1, pady=10, padx=10)

    def return_book():
        issue_id = issue_id_entry.get()
        if not issue_id:
            messagebox.showerror("Error", "Issue ID is required!")
            return

        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()

        cursor.execute("SELECT BookID, IssueDate FROM IssuedBooks WHERE IssueID = ?", (issue_id,))
        issued_book = cursor.fetchone()

        if issued_book is None:
            messagebox.showerror("Error", "Issue ID not found!")
            conn.close()
            return

        book_id, issue_date = issued_book

        # Calculate overdue fine
        cursor.execute("SELECT julianday('now') - julianday(?) AS Days FROM IssuedBooks WHERE IssueID = ?", (issue_date, issue_id))
        days = cursor.fetchone()[0]
        overdue_fine = max(0, int(days - 14) * 2)  # ₹2 per day after 14 days

        cursor.execute("DELETE FROM IssuedBooks WHERE IssueID = ?", (issue_id,))
        cursor.execute("UPDATE Books SET IssuedCount = IssuedCount - 1 WHERE BookID = ?", (book_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Book returned successfully! Overdue fine: ₹{overdue_fine}")
        issue_id_entry.delete(0, tk.END)

    tk.Button(return_window, text="Return Book", command=return_book).grid(row=1, column=0, columnspan=2, pady=20)

# View Issued Books
def open_view_issued_books_window():
    issued_window = tk.Toplevel(root)
    issued_window.title("Issued Books")
    issued_window.geometry("600x400")

    issued_list = ttk.Treeview(issued_window, columns=("IssueID", "BookID", "UserName", "IssueDate"), show="headings")
    issued_list.pack(fill=tk.BOTH, expand=True)
    for col in ("IssueID", "BookID", "UserName", "IssueDate"):
        issued_list.heading(col, text=col)

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM IssuedBooks")
    issued_books = cursor.fetchall()
    conn.close()

    issued_list.delete(*issued_list.get_children())
    for book in issued_books:
        issued_list.insert("", tk.END, values=book)

# Main Window
initialize_database()
root = tk.Tk()
root.title("Library Management System")
root.geometry("400x400")

tk.Label(root, text="Library Management System", font=("Arial", 16)).pack(pady=20)

tk.Button(root, text="Add Book", command=open_add_book_window, width=20).pack(pady=10)
tk.Button(root, text="Issue Book", command=open_issue_book_window, width=20).pack(pady=10)
tk.Button(root, text="View Books", command=open_view_books_window, width=20).pack(pady=10)
tk.Button(root, text="Return Book", command=open_return_book_window, width=20).pack(pady=10)
tk.Button(root, text="View Issued Books", command=open_view_issued_books_window, width=20).pack(pady=10)

root.mainloop()
