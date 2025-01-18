import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ttkthemes import ThemedTk
from auth.login import login
from auth.register import signup
from config.firebase_config import cred
from firebase_admin import initialize_app, firestore

class CurrencyConverter:
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.title("Currency Converter Pro")
        self.root.geometry("800x600") 
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Firebase initialization
        initialize_app(cred)
        
        # Firestore initialization
        self.db = firestore.client()
               
        # Show login page first
        self.show_login_page()

    def show_login_page(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Configure grid weights to enable centering
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main login frame
        self.login_frame = ttk.Frame(self.root, padding="20")
        self.login_frame.grid(row=0, column=0, sticky="")  # Empty sticky parameter for center alignment
        
        # Configure login frame grid weights
        self.login_frame.grid_columnconfigure(1, weight=1)
        
        # Add widgets with proper spacing and alignment
        title_label = ttk.Label(self.login_frame, text="Currency Converter Pro", font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Email field
        email_label = ttk.Label(self.login_frame, text="Email:")
        email_label.grid(row=1, column=0, pady=5, padx=(0, 10), sticky='e')
        self.email_entry_login = ttk.Entry(self.login_frame, width=30)
        self.email_entry_login.grid(row=1, column=1, pady=5)
        
        # Password field
        password_label = ttk.Label(self.login_frame, text="Password:")
        password_label.grid(row=2, column=0, pady=5, padx=(0, 10), sticky='e')
        self.password_entry_login = ttk.Entry(self.login_frame, show="*", width=30)
        self.password_entry_login.grid(row=2, column=1, pady=5)
        
        # Button frame for better button alignment
        button_frame = ttk.Frame(self.login_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        # Login and Register buttons
        login_button = ttk.Button(button_frame, text="Login", 
                                command=lambda: self.login(self.email_entry_login.get(), 
                                                         self.password_entry_login.get()))
        login_button.grid(row=0, column=0, padx=5)
        
        register_button = ttk.Button(button_frame, text="Register", 
                                   command=self.show_signup_page)
        register_button.grid(row=0, column=1, padx=5)

    def show_signup_page(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Configure grid weights to enable centering
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main signup frame
        self.signup_frame = ttk.Frame(self.root, padding="20")
        self.signup_frame.grid(row=0, column=0, sticky="")  # Empty sticky parameter for center alignment
        
        # Configure signup frame grid weights
        self.signup_frame.grid_columnconfigure(1, weight=1)
        
        # Add widgets with proper spacing and alignment
        title_label = ttk.Label(self.signup_frame, text="Currency Converter Pro", font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Email field
        email_label = ttk.Label(self.signup_frame, text="Email:")
        email_label.grid(row=1, column=0, pady=5, padx=(0, 10), sticky='e')
        self.email_entry_signup = ttk.Entry(self.signup_frame, width=30)
        self.email_entry_signup.grid(row=1, column=1, pady=5)
        
        # Password field
        password_label = ttk.Label(self.signup_frame, text="Password:")
        password_label.grid(row=2, column=0, pady=5, padx=(0, 10), sticky='e')
        self.password_entry_signup = ttk.Entry(self.signup_frame, show="*", width=30)
        self.password_entry_signup.grid(row=2, column=1, pady=5)
        
        # Confirm Password field
        confirm_password_label = ttk.Label(self.signup_frame, text="Confirm Password:")
        confirm_password_label.grid(row=3, column=0, pady=5, padx=(0, 10), sticky='e')
        self.confirm_password_entry_signup = ttk.Entry(self.signup_frame, show="*", width=30)
        self.confirm_password_entry_signup.grid(row=3, column=1, pady=5)
        
        # Button frame for better button alignment
        button_frame = ttk.Frame(self.signup_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        # Register and Login buttons
        register_button = ttk.Button(button_frame, text="Register", 
                                   command=lambda: self.signup(self.email_entry_signup.get(),
                                                             self.password_entry_signup.get(),
                                                             self.confirm_password_entry_signup.get()))
        register_button.grid(row=0, column=0, padx=5)
        
        login_button = ttk.Button(button_frame, text="Login", 
                                command=self.show_login_page)
        login_button.grid(row=0, column=1, padx=5)

    def login(self, email, password):
        self.user = login(email, password)
        if self.user:
            if self.user == 'INVALID_EMAIL':
                messagebox.showerror("Error", "Email Address is invalid")
            elif self.user == 'MISSING_PASSWORD':
                messagebox.showerror("Error", "Please enter your password")
            elif self.user == 'INVALID_LOGIN_CREDENTIALS': 
                messagebox.showerror("Error", "Invalid Password")
            else:
                self.doc_ref = self.db.collection("users").document(self.user['localId']).collection('history').order_by('time_created', direction=firestore.Query.DESCENDING)
                docs = self.doc_ref.stream()
                self.entries_array = [{"id": doc.id, **doc.to_dict()} for doc in docs]
                self.show_main_application()

    def signup(self, email, password, confirm_password):
        if password and confirm_password: 
            if password == confirm_password: 
                self.user = signup(email, password)
                if self.user:
                    if self.user == 'EMAIL_EXITS':
                        messagebox.showerror("Error", "Email Already Exists")
                    elif self.user == 'WEAK_PASSWORD':
                        messagebox.showerror("Error", "Password must be at least 6 characters")
                    elif self.user == 'INVALID_EMAIL':
                        messagebox.showerror("Error", "Enter a valid email address")
                    else:
                        self.doc_ref = self.db.collection("users").document(self.user['localId']).collection('history').order_by('time_created', direction=firestore.Query.DESCENDING)
                        docs = self.doc_ref.stream()
                        self.entries_array = [{"id": doc.id, **doc.to_dict()} for doc in docs]
                        self.show_main_application()
            else: 
                messagebox.showerror("Error", "Password does not match")
        else: 
            messagebox.showerror("Error", "Please enter confirm password")

    def on_close(self):
        """Handle the window close event"""
        try:
            self.root.quit()  # Stop the mainloop
            self.root.destroy()  # Destroy the window
        except:
            pass
        finally:
            exit(0)  # Exit the application

    def run(self):
        self.root.mainloop() 
           
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
        for item in self.entries_array:
            self.history_tree.insert("", tk.END, values=tuple([item['time_created'], item['from'], item['to'], item['amount'], item['converted_amount']]))

    def create_graph_widget(self):
        
     self.graph_frame = ttk.LabelFrame(self.main_frame, text="Exchange Rate Trends", padding="10")
     self.graph_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Increase figure size slightly
     self.fig, self.ax = plt.subplots(figsize=(6, 4))
     self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
     self.canvas.get_tk_widget().grid(row=0, column=0, pady=5)

    def setup_rate_notification(self):
    # Create a frame for the notification widget and scrollbar
        notification_frame = ttk.LabelFrame(self.main_frame, text="Rate Notifications", padding="10")
        notification_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(notification_frame, orient=tk.VERTICAL)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Add text widget with scroll support
        self.notification_text = tk.Text(notification_frame, wrap=tk.WORD, height=8, yscrollcommand=scrollbar.set, state=tk.DISABLED)
        self.notification_text.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure the scrollbar to work with the text widget
        scrollbar.config(command=self.notification_text.yview)
        
        # Set weight for resizing
        notification_frame.rowconfigure(0, weight=1)
        notification_frame.columnconfigure(0, weight=1)
        
        # Update the notification text
        self.display_notifications()


    def display_notifications(self):
        # Generate notifications
        notifications = self.generate_notifications()
        
        # Enable the text widget to insert content
        self.notification_text.config(state=tk.NORMAL)
        
        # Clear previous content
        self.notification_text.delete("1.0", tk.END)
        
        # Add each notification on a new line
        for notification in notifications:
            self.notification_text.insert(tk.END, f"{notification}\n")
        
        # Disable the text widget to make it read-only
        self.notification_text.config(state=tk.DISABLED)

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
            self.save_to_history(from_curr, to_curr, amount, converted_amount)
            
            # Update graph
            self.update_graph()

            self.setup_rate_notification()
            
        except Exception as e:
            print(e)
            messagebox.showerror("Error", "Please enter a valid amount")

    def get_exchange_rate(self, from_curr, to_curr):
        # For demonstration, using dummy rates
        rate=self.data[to_curr]/self.data[from_curr]
        return rate

    def save_to_history(self,from_curr, to_curr, amount, converted_amount):
        current_time = datetime.now()
        current_time=current_time.strftime('%Y-%m-%d %H:%M:%S')
        
        data = {
            "time_created": current_time,
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "converted_amount": converted_amount
        }
        # Save to database
        doc_ref = self.doc_ref.add(data)
        doc_id = doc_ref[1].id
        new_entry = data.copy()
        new_entry["id"] = doc_id
        self.entries_array.append(new_entry)
        
        # Insert data into the Treeview
        self.history_tree.insert("", tk.END, values=tuple([data['time_created'], data['from'], data['to'], data['amount'], data['converted_amount']]))
        
        self.generate_notifications()

    def update_graph(self):
     self.ax.clear()
    
    # Specify the 5 currencies we want to show (including INR)
     selected_currencies = ['EUR', 'GBP', 'JPY', 'INR', 'USD']
    
    # Filter currencies and get their rates (excluding USD since it's our base)
     currencies = [curr for curr in selected_currencies if curr != 'USD']
     rates = [self.data[curr]/self.data['USD'] for curr in currencies]
    
    # Create bar graph with light blue color
     bars = self.ax.bar(currencies, rates, color='skyblue', width=0.4)
    
    # Customize the graph
     self.ax.set_title('Exchange Rates of Selected Currencies', pad=15, fontsize=11)
     self.ax.set_xlabel('Currency Code', labelpad=8)
     self.ax.set_ylabel('Exchange Rate', labelpad=8)
    
    # Add grid with dashed lines
     self.ax.grid(True, linestyle='--', alpha=0.5, axis='y')
     self.ax.set_axisbelow(True)
    
    # Format x-axis labels
     plt.xticks(rotation=0)  # No rotation needed for fewer currencies

     self.fig.set_size_inches(4.5, 3.8)
    
    # Adjust y-axis scale to fit the data
     max_rate = max(rates)
     y_max = max_rate * 1.1  # Add 20% padding
     self.ax.set_ylim(0, y_max)
    
    # Format y-axis ticks
     self.ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))
    
    # Remove top and right spines
     self.ax.spines['top'].set_visible(False)
     self.ax.spines['right'].set_visible(False)
    
    # Add value labels on top of each bar
     for bar in bars:
        height = bar.get_height()
        self.ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom',
                    fontsize=9)
    
    # Adjust layout
     plt.tight_layout(pad=1.2)
    
    # Set white background
     self.fig.patch.set_facecolor('white')
     self.ax.set_facecolor('white')
    
    # Update the canvas
     self.canvas.draw()
    
    # Add value labels on top of each bar
     for bar in bars:
        height = bar.get_height()
        self.ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom',
                    fontsize=9)
    
    # Adjust layout
     plt.tight_layout(pad=1.2)
    
    # Set white background
     self.fig.patch.set_facecolor('white')
     self.ax.set_facecolor('white')
    
    # Update the canvas
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
        arr=[]
        for entry in self.entries_array:
            arr.append(entry['from'])
            arr.append(entry['to'])
        arr=list(set(arr))
        print(arr)
        notifications=[]
        for i in arr:
            if p_data[i]!=self.data[i]:
                old_rate=1/p_data[i]
                new_rate=1/self.data[i]
                change=abs(((new_rate-old_rate)/old_rate)*100)
                if p_data[i]<self.data[i]:
                    temp=f'The exchange rate of {i} has decreased by {change:.2} W.R.T USD in this month'
                    notifications.append(temp)
                else:
                    temp=f'The value of {i} has increased by {change:.2} W.R.T USD in this month'
                    notifications.append(temp)

        return notifications

    def run(self):
        self.root.mainloop()
        
    def on_close(self):
        self.root.destroy()
        exit(0)

if __name__ == "__main__":
    app = CurrencyConverter()
    app.run()
