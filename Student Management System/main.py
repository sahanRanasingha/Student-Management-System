import tkinter as tkinter
from tkinter import ttk
import customtkinter
from PIL import Image, ImageTk
from tkinter import messagebox
import sqlite3
import hashlib

# Custom Tkinter setup
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")

# Define functions for database operations
class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY,
                                username TEXT,
                                email TEXT,
                                password TEXT
                            )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                                id INTEGER PRIMARY KEY,
                                registration_number TEXT UNIQUE,
                                first_name TEXT,
                                last_name TEXT,
                                email TEXT,
                                gender TEXT,
                                phone_number TEXT,
                                date_of_birth TEXT,
                                address TEXT
                            )''')
        self.connection.commit()

    def insert_user(self, username, email, password):
        try:
            # Hash the password before inserting it into the database
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute('''INSERT INTO users (username, email, password)
                                    VALUES (?, ?, ?)''', (username, email, hashed_password))
            self.connection.commit()
            return True  # Registration successful
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error occurred: {e}")
            return False  # Registration failed
        
    def insert_student_details(self, registration_number, first_name, last_name, email,gender, phone_number, date_of_birth, address):
        try:
            self.cursor.execute('''INSERT INTO students (registration_number, first_name, last_name, email, gender, phone_number, date_of_birth, address)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (registration_number, first_name, last_name, email, gender, phone_number, date_of_birth, address))
            self.connection.commit()
            return True  # Insertion successful
        except sqlite3.Error as e:
            return False  # Insertion failed
    
    def update_student_details(self, student_id, registration_number, first_name, last_name, email, gender, phone_number, date_of_birth, address):
        try:
            self.cursor.execute('''UPDATE students
                                    SET registration_number=?, first_name=?, last_name=?, email=?, gender=?, phone_number=?, date_of_birth=?, address=?
                                    WHERE id=?''', (registration_number, first_name, last_name, email, gender, phone_number, date_of_birth, address, student_id))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error occurred: {e}")
            return False
    
    def delete_student(self, student_id):
        try:
            self.cursor.execute('''DELETE FROM students
                                    WHERE id=?''', (student_id,))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error occurred: {e}")
            return False

    def get_user(self, username, password):
        # Hash the password before querying the database
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute('''SELECT * FROM users
                                WHERE username=? AND password=?''', (username, hashed_password))
        return self.cursor.fetchone()

    def update_password(self, username, email, password):
        # Hash the new password before updating it in the database
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            self.cursor.execute('''UPDATE users
                                    SET password=?
                                    WHERE username=? AND email=?''', (hashed_password, username, email))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            return False


# Login window
class LoginWindow(tkinter.Tk):
    def __init__(self, db):
        self.db = db
        super().__init__()

        # Center the window on the screen
        self.center_window()

        self.geometry("600x400")
        self.title("Login")
        self.iconbitmap("Assets/icon.ico")
        self.configure(bg="#333333")

        img1 = Image.open("Assets/background.jpg")
        self.bg_image = ImageTk.PhotoImage(img1)
        l1 = customtkinter.CTkLabel(master=self, image=self.bg_image)
        l1.pack()

        frame = customtkinter.CTkFrame(master=l1, width=320, height=360, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        l2 = customtkinter.CTkLabel(master=frame, text="Log into your Account", font=("Arial", 20))
        l2.place(x=60, y=45)

        self.username_entry = customtkinter.CTkEntry(master=frame, width=220, placeholder_text="Username")
        self.username_entry.place(x=50, y=110)

        self.password_entry = customtkinter.CTkEntry(master=frame, width=220, placeholder_text="Password", show="*")
        self.password_entry.place(x=50, y=160)

        forgotPassword_link = customtkinter.CTkLabel(master=frame, text="Forgot Password?", width=22, cursor="hand2")
        forgotPassword_link.place(x=165, y=190)
        forgotPassword_link.bind("<Button-1>", lambda e: self.on_forgot_password_click())

        login_button = customtkinter.CTkButton(master=frame, text="Login", width=220, cursor="hand2", command=self.authenticate_user)
        login_button.place(x=50, y=230)

        register_button = customtkinter.CTkButton(master=frame, text="Register", width=220, cursor="hand2", command=self.on_register_click)
        register_button.place(x=50, y=280)

    def center_window(self):
        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate position x and y coordinates to center the window
        x = (screen_width / 2) - (600 / 2)
        y = (screen_height / 2) - (400 / 2)

        # Set the window's position
        self.geometry(f"600x400+{int(x)}+{int(y)}")

    def authenticate_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = self.db.get_user(username, password)
        if user:
            # User authenticated, proceed with login
            messagebox.showinfo("Success", "Login successful")
            self.open_dashboard_window()
        else:
            # Authentication failed, show error message
            messagebox.showerror("Error", "Invalid username or password")  

    def on_register_click(self):
        self.withdraw()  # Hide the login window
        register_window = RegisterWindow(self, self.db)
        register_window.mainloop()
    
    def on_forgot_password_click(self):
        self.withdraw()  # Hide the login window
        forgot_window = ForgotWindow(self, self.db)
        forgot_window.mainloop()
    
    def open_dashboard_window(self):
        self.withdraw()  # Hide the login window
        # Create and open the dashboard window
        dashboard_window = StudentManagementSystem(self, self.db)  
        dashboard_window.mainloop()

# Register window
class RegisterWindow(tkinter.Toplevel):
    def __init__(self, parent, db):
        self.db = db
        super().__init__(parent)

        #Center the window on the screen
        self.center_window()

        self.geometry("600x400")
        self.title("Register")
        self.iconbitmap("Assets/icon.ico")
        self.configure(bg="#333333")

        img1 = Image.open("Assets/background.jpg")
        self.bg_image = ImageTk.PhotoImage(img1)
        l1 = customtkinter.CTkLabel(master=self, image=self.bg_image)
        l1.pack()

        frame = customtkinter.CTkFrame(master=l1, width=320, height=360, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        l2 = customtkinter.CTkLabel(master=frame, text="Create an Account", font=("Arial", 20))
        l2.place(x=80, y=45)

        self.username_entry = customtkinter.CTkEntry(master=frame, width=220, placeholder_text="Username")
        self.username_entry.place(x=50, y=110)

        self.email_entry = customtkinter.CTkEntry(master=frame, width=220, placeholder_text="Email")
        self.email_entry.place(x=50, y=160)

        self.password_entry = customtkinter.CTkEntry(master=frame, width=220, placeholder_text="Password", show="*")
        self.password_entry.place(x=50, y=210)

        register_button = customtkinter.CTkButton(master=frame, text="Register", width=220, cursor="hand2", command=self.register_user)
        register_button.place(x=50, y=260)

        login_button = customtkinter.CTkButton(master=frame, text="Login", width=220, cursor="hand2", command=self.on_login_click)
        login_button.place(x=50, y=310)

    def center_window(self):
        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate position x and y coordinates to center the window
        x = (screen_width / 2) - (600 / 2)
        y = (screen_height / 2) - (400 / 2)

        # Set the window's position
        self.geometry(f"600x400+{int(x)}+{int(y)}")

    def register_user(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        # Check if any of the fields are empty
        if not username or not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        # Insert user data into the database
        if self.db.insert_user(username, email, password):
            messagebox.showinfo("Success", "Registration successful!")
        else:
            messagebox.showerror("Error", "Registration failed!")

    def on_login_click(self):
        self.destroy()  # Close the register window
        self.master.deiconify()  # Re-show the login window

# Forgot password window
class ForgotWindow(tkinter.Toplevel):
    def __init__(self, parent, db):
        self.db = db
        super().__init__(parent)

        #Center the window on the screen
        self.center_window()

        self.geometry("600x400")
        self.title("Forgot Password")
        self.iconbitmap("Assets/icon.ico")
        self.configure(bg="#333333")

        img1 = Image.open("Assets/background.jpg")
        self.bg_image = ImageTk.PhotoImage(img1)
        l1 = customtkinter.CTkLabel(master=self, image=self.bg_image)
        l1.pack()

        frame = customtkinter.CTkFrame(master=l1, width=320, height=360, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        l2 = customtkinter.CTkLabel(master=frame, text="Forgot Password", font=("Arial", 20))
        l2.place(x=80, y=45)

        self.username_entry = customtkinter.CTkEntry(master=frame, width=220, placeholder_text="Username")
        self.username_entry.place(x=50, y=110)

        self.email_entry = customtkinter.CTkEntry(master=frame, width=220, placeholder_text="Email")
        self.email_entry.place(x=50, y=160)

        self.password_entry = customtkinter.CTkEntry(master=frame, width=220, placeholder_text="Password", show="*")
        self.password_entry.place(x=50, y=210)

        reset_button = customtkinter.CTkButton(master=frame, text="Reset", width=220, cursor="hand2", command=self.reset_password)
        reset_button.place(x=50, y=260)

        login_button = customtkinter.CTkButton(master=frame, text="Login", width=220, cursor="hand2", command=self.on_login_click)
        login_button.place(x=50, y=310)

    def center_window(self):
        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate position x and y coordinates to center the window
        x = (screen_width / 2) - (600 / 2)
        y = (screen_height / 2) - (400 / 2)

        # Set the window's position
        self.geometry(f"600x400+{int(x)}+{int(y)}")

    # Update the password in the database
    def reset_password(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        # Check if any of the fields are empty
        if not username or not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Attempt to update the password in the database
        if self.db.update_password(username, email, password):
            # Check if any rows were affected, indicating a successful update
            if self.db.cursor.rowcount > 0:
                messagebox.showinfo("Success", "Password reset successful!")
            else:
                messagebox.showerror("Error", "User not found or incorrect credentials!")
        else:
            messagebox.showerror("Error", "Password reset unsuccessful!")


    def on_login_click(self):
        self.destroy()  # Close the register window
        self.master.deiconify()  # Re-show the login window

class StudentManagementSystem(tkinter.Toplevel):
    def __init__(self, parent, db):
        self.db = db
        super().__init__(parent)

        self.geometry("1366x720")
        self.title("Dashboard")
        self.iconbitmap("Assets/icon.ico")
        self.configure(bg="#333333")

        img1 = Image.open("Assets/background.jpg")
        self.bg_image = ImageTk.PhotoImage(img1)
        l1 = customtkinter.CTkLabel(master=self, image=self.bg_image)
        l1.pack()

        frame1 = customtkinter.CTkFrame(master=l1, width=1350, height=100, corner_radius=15)
        frame1.place(x=10, y=10)

        l2 = customtkinter.CTkLabel(master=frame1, text="Student Management System", font=("Arial", 40, "bold"))
        l2.place(x=400, y=30)

        frame2 = customtkinter.CTkFrame(master=l1, width=430, height=590, corner_radius=15)
        frame2.place(x=10, y=120)

        l3 = customtkinter.CTkLabel(master=frame2, text="Enter Details", font=("Arial", 30, "bold"))
        l3.place(x=120, y=30)

        self.first_name_entry = customtkinter.CTkEntry(master=frame2, width=200, placeholder_text="First Name")
        self.first_name_entry.place(x=10, y=100)

        self.last_name_entry = customtkinter.CTkEntry(master=frame2, width=200, placeholder_text="Second Name")
        self.last_name_entry.place(x=220, y=100)

        self.registration_number_entry = customtkinter.CTkEntry(master=frame2, width=410, placeholder_text="Registration Number")
        self.registration_number_entry.place(x=10, y=150)

        self.email_entry = customtkinter.CTkEntry(master=frame2, width=410, placeholder_text="Email")
        self.email_entry.place(x=10, y=200)

        self.phone_entry = customtkinter.CTkEntry(master=frame2, width=410, placeholder_text="Phone Number")
        self.phone_entry.place(x=10, y=250)

        self.dateofbirth_entry = customtkinter.CTkEntry(master=frame2, width=200, placeholder_text="Date of Birth (YYYY-MM-DD)")
        self.dateofbirth_entry.place(x=10, y=300)

        self.gender_entry = customtkinter.CTkOptionMenu(master=frame2, values=["Male","Female"], width=200)
        self.gender_entry.place(x=220, y=300)

        self.address_entry = customtkinter.CTkEntry(master=frame2, width=410, placeholder_text="Address")
        self.address_entry.place(x=10, y=350)

        save_button = customtkinter.CTkButton(master=frame2, text="Save", width=200, cursor="hand2", command=self.student_details)
        save_button.place(x=10, y=450)

        update_button = customtkinter.CTkButton(master=frame2, text="Update", width=200, cursor="hand2", command=self.update_student_details)
        update_button.place(x=220, y=450)

        delete_button = customtkinter.CTkButton(master=frame2, text="Delete", width=200, cursor="hand2", command=self.delete_student)
        delete_button.place(x=10, y=500)

        clear_button = customtkinter.CTkButton(master=frame2, text="Clear", width=200, cursor="hand2", command=self.clear_fields)
        clear_button.place(x=220, y=500)

        frame3 = customtkinter.CTkFrame(master=l1, width=900, height=590, corner_radius=15)
        frame3.place(x=450, y=120)

        l4 = customtkinter.CTkLabel(master=frame3, text="Student Details", font=("Arial", 30, "bold"))
        l4.place(x=340, y=30)

        l5 = customtkinter.CTkLabel(master=frame3, text="Search : ", font=("Arial", 20, "bold"))
        l5.place(x=10, y=100)

        self.search_entry = customtkinter.CTkEntry(master=frame3, width=200, placeholder_text="Search Data")
        self.search_entry.place(x=100, y=100)

        self.search_option = customtkinter.CTkOptionMenu(master=frame3, values=["First Name","Last Name","Registration Number","Email","Mobile Number","Gender"], width=150)
        self.search_option.place(x=310, y=100)

        search_button = customtkinter.CTkButton(master=frame3, text="Search", width=150, cursor="hand2", command=self.search_student)
        search_button.place(x=470, y=100)

        update_table_button = customtkinter.CTkButton(master=frame3, text="Refresh Table", width=150, cursor="hand2", command=self.populate_table)
        update_table_button.place(x=630, y=100)

        # Create the table to display student details
        self.create_table(frame3)

        # Bind the destroy method to the window's destroy event
        self.bind("<Destroy>", self.destroy)

    def create_table(self,frame3):
        frame4 = customtkinter.CTkFrame(master=frame3, width=850, height=430, corner_radius=15)
        frame4.place(x=25, y=150)

        # create a table to display student details
        self.student_details_table = ttk.Treeview(master=frame4, columns=("ID", "Registration Number", "First Name", "Last Name", "Email", "Gender", "Mobile No.", "D.O.B", "Address"), show="headings")
        self.student_details_table.place(x=10, y=10, width=830, height=400)

        # Add headings to the table
        self.student_details_table.heading("ID", text="ID")
        self.student_details_table.heading("Registration Number", text="Registration Number")
        self.student_details_table.heading("First Name", text="First Name")
        self.student_details_table.heading("Last Name", text="Last Name")
        self.student_details_table.heading("Email", text="Email")
        self.student_details_table.heading("Gender", text="Gender")
        self.student_details_table.heading("Mobile No.", text="Mobile No.")
        self.student_details_table.heading("D.O.B", text="D.O.B")
        self.student_details_table.heading("Address", text="Address")

        # create a scrollbar for the table
        vertical_scrollbar = ttk.Scrollbar(master=frame4, orient="vertical", command=self.student_details_table.yview)
        vertical_scrollbar.place(x=830, y=10, height=400)

        horizontal_scrollbar = ttk.Scrollbar(master=frame4, orient="horizontal", command=self.student_details_table.xview)
        horizontal_scrollbar.place(x=10, y=410, width=830)

        # Fetch data from the database
        self.populate_table()

        self.student_details_table.bind("<<TreeviewSelect>>", self.on_select)


    # send data to the database
    def student_details(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        registration_number = self.registration_number_entry.get()
        email = self.email_entry.get()
        phone_number = self.phone_entry.get()
        date_of_birth = self.dateofbirth_entry.get()
        gender = self.gender_entry.get()
        address = self.address_entry.get()

        # Check if any of the fields are empty
        if not first_name or not last_name or not registration_number or not email or not phone_number or not date_of_birth or not gender or not address:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        # Insert student data into the database
        # insertdata pattern --->  registration_number, first_name, second_name, email, gender, phone_number, date_of_birth, address
        if self.db.insert_student_details(registration_number, first_name, last_name, email, gender, phone_number, date_of_birth, address):
            messagebox.showinfo("Success", "Data added successfully!")
        else:
            messagebox.showerror("Error", "Failed to add data!")
    
    def populate_table(self):
        # Clear existing data from the table
        for row in self.student_details_table.get_children():
            self.student_details_table.delete(row)

        # Fetch data from the database
        self.db.cursor.execute("SELECT * FROM students")
        data = self.db.cursor.fetchall()

        # Populate the table with the fetched data
        for row in data:
            self.student_details_table.insert("", "end", values=row)

    def on_select(self, event):
        if self.student_details_table.selection():
            # Get the selected item from the table
            selected_item = self.student_details_table.selection()[0]
            
            # Retrieve the values of the selected item
            values = self.student_details_table.item(selected_item, "values")

            # Update entry fields with the selected values
            self.registration_number_entry.delete(0, tkinter.END)
            self.first_name_entry.delete(0, tkinter.END)
            self.last_name_entry.delete(0, tkinter.END)
            self.email_entry.delete(0, tkinter.END)
            self.phone_entry.delete(0, tkinter.END)
            self.dateofbirth_entry.delete(0, tkinter.END)
            self.address_entry.delete(0, tkinter.END)
            
            # Clear the option menu
            self.gender_entry.set("")  # Set it to an empty string or a default value

            # Fill entry fields with the selected values
            if values:
                self.registration_number_entry.insert(tkinter.END, values[1])
                self.first_name_entry.insert(tkinter.END, values[2])
                self.last_name_entry.insert(tkinter.END, values[3])
                self.email_entry.insert(tkinter.END, values[4])
                self.gender_entry.set(values[5])
                self.phone_entry.insert(tkinter.END, values[6])
                self.dateofbirth_entry.insert(tkinter.END, values[7])
                self.address_entry.insert(tkinter.END, values[8])
    
    def update_student_details(self):
        if self.student_details_table.selection():
            # Get the ID of the selected student
            selected_item = self.student_details_table.selection()[0]
            student_id = self.student_details_table.item(selected_item, "values")[0]

            # Get updated values from entry fields
            first_name = self.first_name_entry.get()
            last_name = self.last_name_entry.get()
            registration_number = self.registration_number_entry.get()
            email = self.email_entry.get()
            phone_number = self.phone_entry.get()
            date_of_birth = self.dateofbirth_entry.get()
            gender = self.gender_entry.get()
            address = self.address_entry.get()

            # Check if any of the fields are empty
            if not first_name or not last_name or not registration_number or not email or not phone_number or not date_of_birth or not gender or not address:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            # Update student data in the database
            if self.db.update_student_details(student_id, registration_number, first_name, last_name, email, gender, phone_number, date_of_birth, address):
                messagebox.showinfo("Success", "Data updated successfully!")
                # Refresh the table to reflect the changes
                self.populate_table()
            else:
                messagebox.showerror("Error", "Failed to update data!")
        
        else:
            messagebox.showerror("Error", "Please select a student to update")
        
    def delete_student(self):
        # Check if a student is selected in the table
        if not self.student_details_table.selection():
            messagebox.showerror("Error", "Please select a student to delete")
            return

        # Get the ID of the selected student
        selected_item = self.student_details_table.selection()[0]
        student_id = self.student_details_table.item(selected_item, "values")[0]

        # Confirm deletion with the user
        confirmation = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this student record?")

        if confirmation:
            # Attempt to delete the student from the database
            if self.db.delete_student(student_id):
                messagebox.showinfo("Success", "Student record deleted successfully!")
                # Refresh the table to reflect the changes
                self.populate_table()
            else:
                messagebox.showerror("Error", "Failed to delete student record!")

    def clear_fields(self):
        self.registration_number_entry.delete(0, tkinter.END)
        self.first_name_entry.delete(0, tkinter.END)
        self.last_name_entry.delete(0, tkinter.END)
        self.email_entry.delete(0, tkinter.END)
        self.phone_entry.delete(0, tkinter.END)
        self.dateofbirth_entry.delete(0, tkinter.END)
        self.address_entry.delete(0, tkinter.END)

    def search_student(self):
        search_text = self.search_entry.get()
        search_option = self.search_option.get()

        # set the database column name
        if search_option == "First Name":
            search_option = "first_name"
        elif search_option == "Last Name":
            search_option = "last_name"
        elif search_option == "Registration Number":
            search_option = "registration_number"
        elif search_option == "Email":
            search_option = "email"
        elif search_option == "Mobile Number":
            search_option = "phone_number"
        elif search_option == "Gender":
            search_option = "gennder"

        # Check if the search query is empty
        if not search_text:
            messagebox.showerror("Error", "Please enter a search query")
            return

        try:
            # Fetch data from the database
            query = f'SELECT * FROM students WHERE `{search_option}`=?'
            self.db.cursor.execute(query, (search_text,))
            data = self.db.cursor.fetchall()

            # Clear existing data from the table
            for row in self.student_details_table.get_children():
                self.student_details_table.delete(row)

            # Populate the table with the fetched data
            for row in data:
                self.student_details_table.insert("", "end", values=row)
        except Exception as e:
            print("Error:", e)
            messagebox.showerror("Error", f"An error occurred: {e}")

    def destroy(self, event=None):
        # Close the database connection when the window is destroyed
        self.db.connection.close()
        self.quit()

if __name__ == "__main__":
    db = Database("student_details.db")  # Connect to the database
    app = LoginWindow(db)
    #app = StudentManagementSystem(None, db)
    app.mainloop()
