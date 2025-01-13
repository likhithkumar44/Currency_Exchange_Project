import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from ttkthemes import ThemedTk
import bcrypt

class CurrencyConverter:
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.title("Currency Converter Pro")
        self.root.geometry("800x600")
        
        # Database initialization
        self.init_database()
        
        # Show login page first
        self.show_login_page()
        
    def init_database(self):
        self.conn = sqlite3.connect('db_for_cc.db')
        self.cursor = self.conn.cursor()
        
        # Create users table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
        ''')
        
        # Create conversion history table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversion_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            from_currency TEXT,
            to_currency TEXT,
            amount REAL,
            converted_amount REAL,
            date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(username)
        )
        ''')
        self.conn.commit()

    def show_login_page(self):
        self.login_frame = ttk.Frame(self.root, padding="20")
        self.login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(self.login_frame, text="Currency Converter Pro", font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
        
        ttk.Label(self.login_frame, text="Username:").grid(row=1, column=0, pady=5)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(self.login_frame, text="Password:").grid(row=2, column=0, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)
        
        ttk.Button(self.login_frame, text="Login", command=self.login).grid(row=3, column=0, pady=20)
        ttk.Button(self.login_frame, text="Register", command=self.register).grid(row=3, column=1, pady=20)

    def login(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        
        self.cursor.execute('SELECT password FROM users WHERE username=?', (self.username,))
        result = self.cursor.fetchone()
        
        if result and bcrypt.checkpw(self.password.encode('utf-8'), result[0]):
            self.current_user = self.username
            self.login_frame.destroy()
            self.show_main_application()

            self.cursor.execute(f"SELECT * FROM user_{self.username} ORDER BY date DESC")
            rows = self.cursor.fetchall()

            for row in rows:
                self.history_tree.insert("", tk.END, values=row)

        else:
            messagebox.showerror("Error", "Invalid username or password")

    def register(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        
        if self.username and self.password:
            hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt())
            try:
                self.cursor.execute('INSERT INTO users VALUES (?, ?)', (self.username, hashed_password))
                self.conn.commit()
                query=f'''CREATE TABLE IF NOT EXISTS user_{self.username} (date TIMESTAMP,
                    from_currency TEXT,
                    to_currency TEXT,
                    amount REAL,
                    converted_amount REAL
                    )'''
                self.cursor.execute(query)
                messagebox.showinfo("Success", "Registration successful!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists")
        else:
            messagebox.showerror("Error", "Please fill all fields")

    def show_main_application(self):
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Currency selection
        self.from_currency_var = tk.StringVar()
        self.to_currency_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        
        # Get supported currencies
        self.currencies = self.get_supported_currencies()
        
        # Create widgets
        self.create_converter_widgets()
        self.create_history_widget()
        self.create_graph_widget()
        
        # Set up rate notification
        self.setup_rate_notification()

    def get_supported_currencies(self):
        # Using Exchange Rate API
        url = 'https://api.frankfurter.dev/v1/latest?base=USD'
        
        try:
            response = requests.get(url)
            self.data = response.json()
            self.data=self.data['rates']
            self.data['USD']=1
            return list(self.data.keys())
        except:
            return ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR']

    def create_converter_widgets(self):
        # Converter frame
        converter_frame = ttk.LabelFrame(self.main_frame, text="Currency Converter", padding="10")
        converter_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # From currency
        ttk.Label(converter_frame, text="From:").grid(row=0, column=0, padx=5, pady=5)
        from_currency_cb = ttk.Combobox(converter_frame, textvariable=self.from_currency_var, values=self.currencies)
        from_currency_cb.grid(row=0, column=1, padx=5, pady=5)
        from_currency_cb.set('USD')
        
        # To currency
        ttk.Label(converter_frame, text="To:").grid(row=1, column=0, padx=5, pady=5)
        to_currency_cb = ttk.Combobox(converter_frame, textvariable=self.to_currency_var, values=self.currencies)
        to_currency_cb.grid(row=1, column=1, padx=5, pady=5)
        to_currency_cb.set('EUR')
        
        # Amount
        ttk.Label(converter_frame, text="Amount:").grid(row=2, column=0, padx=5, pady=5)
        amount_entry = ttk.Entry(converter_frame, textvariable=self.amount_var)
        amount_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Convert button
        ttk.Button(converter_frame, text="Convert", command=self.convert_currency).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Result
        self.result_label = ttk.Label(converter_frame, text="")
        self.result_label.grid(row=4, column=0, columnspan=2, pady=5)

    def create_history_widget(self):
        history_frame = ttk.LabelFrame(self.main_frame, text="Conversion History", padding="10")
        history_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.history_tree = ttk.Treeview(history_frame, columns=('Date', 'From', 'To', 'Amount', 'Converted'), show='headings')
        self.history_tree.heading('Date', text='Date')
        self.history_tree.heading('From', text='From')
        self.history_tree.heading('To', text='To')
        self.history_tree.heading('Amount', text='Amount')
        self.history_tree.heading('Converted', text='Converted')
        self.history_tree.grid(row=0, column=0, pady=5)

    def create_graph_widget(self):
        self.graph_frame = ttk.LabelFrame(self.main_frame, text="Exchange Rate Trends", padding="10")
        self.graph_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.fig, self.ax = plt.subplots(figsize=(4.5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, pady=5)

    def setup_rate_notification(self):
        self.notification_var = tk.StringVar()
        notification_frame = ttk.LabelFrame(self.main_frame, text="Rate Notifications", padding="10")
        notification_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(notification_frame, textvariable=self.notification_var).grid(row=0, column=0, pady=5)
        self.notification_var.set("No new rate alerts")

    def convert_currency(self):
        try:
            amount = float(self.amount_var.get())
            from_curr = self.from_currency_var.get()
            to_curr = self.to_currency_var.get()
            
            # Get conversion rate (you should implement actual API call here)
            rate = self.get_exchange_rate(from_curr, to_curr)
            converted_amount = amount * rate
            
            # Update result
            self.result_label.config(text=f"{amount} {from_curr} = {converted_amount:.2f} {to_curr}")
            
            # Save to history
            self.save_to_history(from_curr, to_curr, amount, converted_amount,self.username)
            
            # Update graph
            self.update_graph()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")

    def get_exchange_rate(self, from_curr, to_curr):
        # For demonstration, using dummy rates
        rate=self.data[to_curr]/self.data[from_curr]
        return rate

    def save_to_history(self,from_curr, to_curr, amount, converted_amount,username):
        current_time = datetime.now()
        current_time=current_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Save to database
        query=f'''INSERT INTO user_{username} (date,from_currency,to_currency,amount,converted_amount)
        VALUES (?, ?, ?, ?, ?)'''
        self.cursor.execute(query, (str(current_time),from_curr, to_curr, amount, converted_amount))
        self.conn.commit()
        
        # Update history display
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)

        query=f'SELECT * FROM user_{username} ORDER BY date DESC'
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        # Insert data into the Treeview
        for row in rows:
            self.history_tree.insert("", tk.END, values=row)

        self.generate_notifications()

    def update_graph(self):
        self.ax.clear()
        # Add actual historical data plotting here
        # For demonstration, plotting dummy data
        dates = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
        rates = [1.1, 1.12, 1.15, 1.13, 1.14]
        
        self.ax.plot(dates, rates)
        self.ax.set_title(f"{self.from_currency_var.get()}/{self.to_currency_var.get()} Exchange Rate Trend")
        self.canvas.draw()


    def generate_notifications(self):
        date=datetime.now()
        date=date.replace(day=1)-timedelta(days=1)
        date=date.strftime('%Y-%m-%d')
        url=f'https://api.frankfurter.dev/v1/{date}?base=USD'
        response=requests.get(url)
        p_data=response.json()
        p_data=p_data['rates']
        p_data['USD']=1

        query=f'SELECT from_currency from user_{self.username}'
        self.cursor.execute(query)
        cur=self.cursor.fetchall()
        arr=[]
        for i in cur:
            arr.append(i[0])
        query=f'SELECT to_currency from user_{self.username}'
        self.cursor.execute(query)
        cur=self.cursor.fetchall()
        for i in cur:
            arr.append(i[0])
        arr=list(set(arr))
        notifications=[]
        for i in arr:
            if p_data[i]!=self.data[i]:
                old_rate=1/p_data[i]
                new_rate=1/self.data[i]
                change=abs(((new_rate-old_rate)/old_rate)*100)
                if p_data[i]<self.data[i]:
                    temp=f'The exchange rate of {i} has decreased by {change:.2} W.R.T USD'
                    notifications.append(temp)
                else:
                    temp=f'The value of {i} has increased by {change:.2} W.R.T USD'
                    notifications.append(temp)

        return notifications


    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CurrencyConverter()
    app.run()
