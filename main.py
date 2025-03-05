from customtkinter import *
from tkinter import *
from PIL import ImageTk, Image
from tkinter import font, messagebox, simpledialog
from time import strftime
from tkinter import StringVar, IntVar
from datetime import datetime
import os
import random
import string
import copy
import tkinter as tk
import re
import math
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from fpdf import FPDF  # Ensure correct capitalization

# Main window
window = CTk()
window.geometry("1200x720")
window.resizable(False, False)
window.title("POINT OF SALE")
window.iconbitmap('assets\logo icon.ico')
set_appearance_mode("dark")

# Global numbers
def generate_transaction_number():
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    reference_number = random.randint(1000, 9999)
    return f"{reference_number}-{current_datetime}"

# Global variables
customer_type_var = StringVar(value="None") 

transaction_history_frame = None
total_cost = 0.0
discount_amount = 0.0
vat_amount = 0.0
receipt_items = {}
history = []
transaction_number = generate_transaction_number()
RECEIPTS_DIR = "receipts"
discount_applied = False
reference_number = generate_transaction_number()

# Ensure receipts directories exist
if not os.path.exists(RECEIPTS_DIR):
    os.makedirs(RECEIPTS_DIR)
if not os.path.exists("pdf_receipts"):
    os.makedirs("pdf_receipts")

# Functions
def login():
    user = username_entry.get()
    pwd = password_entry.get()
    
    if (user == "admin" and pwd == "admin") or \
       (user == "coronel" and pwd == "coronel") or \
       (user == "jdr" and pwd == "reviewers"):
        messagebox.showinfo("Login", "Login Successful!")
        welcome_frame.tkraise() 
    else:
        messagebox.showerror("Login", "Invalid username or password.")

def clear_fields():
    username_entry.delete(0, END)
    password_entry.delete(0, END)

def add_to_receipt(item_name, item_price):
    global total_cost, vat_amount
    vat_rate = 0.12  
    vat_amount_per_item = item_price * vat_rate

    total_cost += item_price  
    vat_amount += vat_amount_per_item  

    if item_name in receipt_items:
        receipt_items[item_name]['quantity'] += 1
        receipt_items[item_name]['total_price'] += item_price
        receipt_items[item_name]['total_vat'] += vat_amount_per_item 
    else:
        receipt_items[item_name] = {
            'price': item_price,
            'quantity': 1,
            'total_price': item_price,
            'total_vat': vat_amount_per_item  
        }
    update_receipt()

def show_page(page, title):
    page.tkraise()
    window.title(title)

def update_reference_number():
    global reference_number
    reference_number += 1  

def remove_item(item_name):
    global receipt_items, total_cost, vat_amount
    
    if item_name in receipt_items:
        item_details = receipt_items[item_name]
        item_price = item_details['price']
        item_vat = item_details['total_vat'] / item_details['quantity']
        
        if item_details['quantity'] > 1:
            item_details['quantity'] -= 1
            item_details['total_price'] -= item_price
            item_details['total_vat'] -= item_vat
        else:
            del receipt_items[item_name]
        
        total_cost = sum(item['total_price'] for item in receipt_items.values())
        vat_amount = sum(item['total_vat'] for item in receipt_items.values())
        
        if not receipt_items:
            total_cost = 0
            vat_amount = 0

        update_receipt()

def clear_row(item_name):
    global receipt_items, total_cost, vat_amount
    if item_name in receipt_items:
        item_details = receipt_items[item_name]
        total_cost -= item_details['total_price']
        vat_amount -= item_details['total_vat']
        del receipt_items[item_name]
        update_receipt()

def update_receipt():
    for widget in receipt_frame_2.winfo_children():
        widget.destroy()

    # Headers
    headers_frame = CTkFrame(receipt_frame_2, fg_color="#FFE4B5")
    headers_frame.grid(row=0, column=0, columnspan=5, sticky="ew", padx=10, pady=5)
    
    product_label = CTkLabel(headers_frame, text="Product:", font=("Montserrat", 16, "bold"), text_color="black", fg_color="#FFE4B5")
    product_label.grid(row=0, column=0, padx=(10, 30), pady=2, sticky="w")
    
    quantity_label = CTkLabel(headers_frame, text="QUANTITY", font=("Montserrat", 16, "bold"), text_color="black", fg_color="#FFE4B5")
    quantity_label.grid(row=0, column=1, padx=(10, 35), pady=2, sticky="w")
    
    price_label = CTkLabel(headers_frame, text="PRICE", font=("Montserrat", 16, "bold"), text_color="black", fg_color="#FFE4B5")
    price_label.grid(row=0, column=2, padx=(10, 35), pady=2, sticky="w")

    # Items
    row = 1
    for item_name, item_details in receipt_items.items():
        item_label = CTkLabel(receipt_frame_2, text=f"{item_name}", font=("Montserrat", 14), text_color="black", fg_color="#FFE4B5")
        item_label.grid(row=row, column=0, padx=(10, 30), pady=2, sticky="w")
        
        quantity_label = CTkLabel(receipt_frame_2, text=f"{item_details['quantity']}", font=("Montserrat", 16), text_color="black", fg_color="#FFE4B5")
        quantity_label.grid(row=row, column=1, padx=(10, 30), pady=2, sticky="w")
        
        price_label = CTkLabel(receipt_frame_2, text=f"₱{item_details['total_price']:.2f}", font=("Montserrat", 16), text_color="black", fg_color="#FFE4B5")
        price_label.grid(row=row, column=2, padx=(10, 30), pady=2, sticky="w")
        
        remove_button = CTkButton(receipt_frame_2, text="x", width=20, command=lambda name=item_name: remove_item(name), fg_color="#E2A76F")
        remove_button.grid(row=row, column=3, pady=2, sticky="w")
        
        clear_button = CTkButton(receipt_frame_2, text="Clear", width=20, command=lambda name=item_name: clear_row(name), fg_color="#E2A76F")
        clear_button.grid(row=row, column=4, padx=(10, 30), pady=2, sticky="w")
        
        row += 1
    
    # Total
    total_label = CTkLabel(receipt_frame_2, text=f"Total + VAT: ₱{total_cost + vat_amount:.2f}", font=("Montserrat", 18, "bold"), text_color="black", fg_color="#FFE4B5")
    total_label.grid(row=row, column=0, columnspan=5, sticky="w", padx=10, pady=10)

def apply_discount():
    global total_cost, discount_amount, discount_applied
    discount_amount = total_cost * 0.20
    total_cost -= discount_amount
    update_receipt()
    discount_applied = True

def void_orders():
    global total_cost, receipt_items, vat_amount
    receipt_items.clear()  
    total_cost = 0.0  
    vat_amount = 0.0  
    update_receipt()  

def checkout():
    global total_cost, discount_amount, receipt_items, history, vat_amount, reference_number

    if not receipt_items:
        messagebox.showerror("Checkout Error", "No items in the receipt. Add items before checkout.")
        return

    money_window = CTkToplevel(fg_color="#C19A6B")
    money_window.title("Enter Amount")
    money_window.geometry("400x200")
    money_window.resizable(False, False)

    CTkLabel(money_window, text="Enter the Customer's Money:", font=("Roboto", 15, "bold")).pack(pady=20)

    money_var = StringVar()
    money_entry = CTkEntry(money_window, textvariable=money_var, font=("Roboto", 15))
    money_entry.pack(pady=10)

    def confirm_checkout():
        global total_cost, vat_amount, discount_amount

        try:
            amount_paid = float(money_var.get())
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a valid number.")
            return

        vat_rate = 0.12
        total_vat = sum(item_details['price'] * item_details['quantity'] * vat_rate for item_details in receipt_items.values())
        total_with_vat = total_cost + total_vat

        if amount_paid < total_with_vat:
            messagebox.showerror("Insufficient Funds", "The amount paid is less than the total cost.")
            return

        if discount_applied:
            discount_rate = 0.20
            discount_amount = total_cost * discount_rate
            total_cost -= discount_amount
            update_receipt()

        change = amount_paid - total_with_vat

        transaction_entry = {
            "items": receipt_items.copy(),
            "total_cost": total_cost,
            "discount_amount": discount_amount,
            "vat_amount": total_vat,
            "total_with_vat": total_with_vat,
            "amount_paid": amount_paid,
            "change": change,
            "reference_number": generate_transaction_number()
        }

        history.append(transaction_entry)

        receipt_content = generate_receipt_content(receipt_items, discount_amount, vat_amount, total_with_vat, amount_paid, change, transaction_entry['reference_number'])  # Pass reference_number

        receipt_filename = os.path.join(RECEIPTS_DIR, f"receipt_{transaction_entry['reference_number']}.txt")
        try:
            with open(receipt_filename, "w", encoding="utf-8") as f:
                f.write(receipt_content)
        except Exception as e:
            messagebox.showerror("Receipt Error", f"Error saving receipt: {e}")
            return

        save_receipt_as_pdf(receipt_content, transaction_entry['reference_number'])

        reference_number = transaction_entry['reference_number']

        receipt_items.clear()
        total_cost = 0.0
        discount_amount = 0.0
        vat_amount = 0.0
        update_receipt()

        messagebox.showinfo("Receipt Generated", f"Receipt {transaction_entry['reference_number']} generated successfully.\nChange: P{change:.2f}")

        money_window.destroy()

    confirm_button = CTkButton(money_window, text="Confirm", command=confirm_checkout)
    confirm_button.pack(pady=10)

def generate_receipt_content(receipt_items, discount_amount, vat_amount, total_with_vat, amount_paid, change, reference_number):  # Modify function definition
    discount_type = customer_type_var.get()
    receipt_content = f"""
          THE BREAD PROJECT
========================================
              Receipt:
========================================
"""

    # List all items with their prices
    for item_name, item_details in receipt_items.items():
        price = item_details['price']
        quantity = item_details['quantity']
        subtotal = price * quantity
        receipt_content += f"{item_name}: {quantity} x P{price:.2f} = P{subtotal:.2f}\n"

    receipt_content += f"""
========================================
Subtotal: P{total_cost:.2f}
Discount ({discount_type}): -P{discount_amount:.2f}
Total + VAT: P{total_with_vat:.2f}

Cash Payment:
Amount Paid: P{amount_paid:.2f}
Change: P{change:.2f}
========================================
Date/Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Ref #: {reference_number}
========================================
This serves as your Official Receipt
Customer Care: +34-397-423
Email us at: jcoronel@breadproject.com / justine.coronel2@cvsu.edu.ph

"Indulge your senses, one delicious bite at a time."
"""

    return receipt_content

def save_receipt_as_pdf(receipt_content, transaction_number):
    pdf_filename = os.path.join("pdf_receipts", f"receipt_{transaction_number}.pdf")
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter
    text = c.beginText(50, height - 50)
    text.setFont("Helvetica", 12)

    for line in receipt_content.split("\n"):
        text.textLine(line)

    c.drawText(text)
    c.save()

# UI
receipt_frame = CTkFrame(window, width=400, height=500, corner_radius=20, fg_color="#C19A6B", bg_color="#FFE4B5")
receipt_frame.place(x=780, y=100)

receipt_frame_2 = CTkScrollableFrame(receipt_frame, width=405, height=430, fg_color="#FFE4B5", bg_color="#C19A6B", corner_radius=20, scrollbar_button_color="#C19A6B")
receipt_frame_2.place(x=10, y=10)

# Login Frame
logins = CTkFrame(window, width=1200, height=720)
logins.place(x=0, y=0)

login_bg_image = Image.open("assets/login_bg.png").resize((1200, 720))
login_bg_image_tk = ImageTk.PhotoImage(login_bg_image)
login_bg_image = CTkLabel(logins, text="", image=login_bg_image_tk)
login_bg_image.place(x=0,y=0)

login_image = Image.open("assets/login.png").resize((100, 100))
login_image_tk = ImageTk.PhotoImage(login_image)
login_lbl = CTkLabel(logins, text="", image=login_image_tk, fg_color="#c2b19c", bg_color="#c2b19c")
login_lbl.place(x=570, y=130)

username_label=CTkLabel(logins, text="Username:", font=("Montserrat", 20, "bold"), fg_color="#c2b19c", bg_color="#FFE4B5", text_color="#000000")
username_label.place(x=450, y=300)

crew_label=CTkLabel(logins, text="LOG IN AS CREW", font=("Montserrat", 20, "bold"), fg_color="#c2b19c", bg_color="#FFE4B5", text_color="#000000")
crew_label.place(x=530, y=250)

username_entry=CTkEntry(logins, placeholder_text="Username", placeholder_text_color="black", fg_color="#E2A76F", bg_color="#c2b19c", width=190)
username_entry.place(x=580, y=300)

password_label=CTkLabel(logins, text="Password:", font=("Montserrat", 20, "bold"), fg_color="#c2b19c", bg_color="#FFE4B5", text_color="#000000")
password_label.place(x=450, y=350)

password_entry=CTkEntry(logins, placeholder_text="Password",  fg_color="#E2A76F", show="*", placeholder_text_color="black", bg_color="#c2b19c", width=190)
password_entry.place(x=580, y=350)

login_button=CTkButton(logins, text="LOGIN", font=("Montserrat", 15, "bold"), corner_radius=15, fg_color="#E2A76F", bg_color="#c2b19c", border_width=0, width=35, height=35, command=login, text_color="#000000")
login_button.place(x=630, y=400)

clear_button=CTkButton(logins, text="CLEAR", font=("Montserrat", 15, "bold"), corner_radius=15, fg_color="#E2A76F", bg_color="#c2b19c", border_width=0, width=35, height=35, command=clear_fields, text_color="#000000")
clear_button.place(x=530, y=400)

# TOP FRAME
welcome_frame = CTkFrame(window, fg_color="#FFE4B5", width=1280, height=720, corner_radius=0)
welcome_frame.place(x=0, y=0)

# header
header_frame = CTkFrame(welcome_frame, fg_color="#E2A76F", height=100, width=1280, corner_radius=0)
header_frame.place(x=0, y=0)

# receipt frame
receipt_frame = CTkFrame(welcome_frame, width=460, height=490, corner_radius=20, fg_color="#C19A6B", bg_color="#FFE4B5")
receipt_frame.place(x=20, y=110)

# ADD ONS DRINKS
drinks_frame = CTkFrame(welcome_frame, fg_color="#C19A6B", bg_color="#FFE4B5", height=105, width=685, corner_radius=10)
drinks_frame.place(x=520, y=615)

# product frame
scroll_frame = CTkScrollableFrame(welcome_frame, width=670, height=455, corner_radius=20, scrollbar_button_color="#C19A6B")
scroll_frame.place(x=500, y=110)

#receipt 2 frame
receipt_frame_2 = CTkScrollableFrame(receipt_frame, width=405, height=430, fg_color="#FFE4B5", bg_color="#C19A6B", corner_radius=20, scrollbar_button_color="#C19A6B" )
receipt_frame_2.place(x=10, y=10)

logo_image = Image.open("assets/logo.png").resize((100, 80))
logo_image_tk = ImageTk.PhotoImage(logo_image)
logo_button = CTkButton(header_frame, image=logo_image_tk, text="", command=lambda:logins.tkraise(), fg_color="#e8a46c", hover_color="#e8a46c")
logo_button.place(x=0, y=6)

title_label = CTkLabel(header_frame, text="THE BREAD PROJECT", font=("Times New Roman", 50, "bold"), text_color="#3B2F2F", fg_color="#FFCBA4", padx=15, pady=0, corner_radius=15)
title_label.place(x=130, y=20)

def load_transaction_history():
    global transaction_history_frame
    if 'transaction_history_frame' in globals() and transaction_history_frame:
        transaction_history_frame.destroy()

    transaction_history_frame = CTkFrame(window, fg_color="#e8a46c")
    transaction_history_frame.grid(row=0, column=0, sticky="nsew")

    transaction_scrollable_frame = CTkScrollableFrame(transaction_history_frame, width=1200, height=610, orientation="horizontal", fg_color="#e8a46c", scrollbar_button_color="#ffcca4")
    transaction_scrollable_frame.pack(pady=10)

    receipts_folder = "receipts"
    if not os.path.exists(receipts_folder):
        messagebox.showerror("Error", "Receipts folder not found.")
        return

    receipt_files = sorted(os.listdir(receipts_folder))

    for index, receipt_file in enumerate(receipt_files):
        receipt_path = os.path.join(receipts_folder, receipt_file)
        with open(receipt_path, "r") as file:
            receipt_content = file.read()

        reference_number = "Unknown"
        for line in receipt_content.split("\n"):
            if line.startswith("Ref #:"):
                reference_number = line.split(":")[1].strip()
                break

        receipt_frame = CTkFrame(transaction_scrollable_frame, width=1000, height=550, corner_radius=20, fg_color="#ffcca4")
        receipt_frame.pack(side="left", padx=10, pady=10)

        CTkLabel(receipt_frame,text_color="black", text=f"RECEIPT #{reference_number}", font=("Roboto", 16, "bold")).pack(anchor="w", padx=10, pady=5)
        CTkLabel(receipt_frame, text_color="black", text=receipt_content, justify="left", font=("Roboto", 12), wraplength=980).pack(anchor="w", padx=10, pady=5)

    previous_button = CTkButton(transaction_history_frame, text="Previous", width=100, height=50, fg_color="#ffcca4", hover_color="#c2b19c", font=("Roboto", 12, "bold"), text_color="black", command=lambda: welcome_frame.tkraise())
    previous_button.pack(side="bottom", pady=10)

def login1():
    def login2():
        user1 = username1_entry.get()
        pwd1 = password1_entry.get()
    
    
        if (user1 == "admin" and pwd1 == "admin") or \
        (user1 == "jdr" and pwd1 == "reviewers"):
            messagebox.showinfo("Login", "Login Successful!")
            load_transaction_history()
        else:
            messagebox.showerror("Login", "Invalid username or password.")

    logins1 = CTkFrame(window, width=1200, height=720)
    logins1.place(x=0, y=0)

    login1_bg_image = Image.open("assets/login_bg.png").resize((1200, 720))
    login1_bg_image_tk = ImageTk.PhotoImage(login1_bg_image)
    login1_bg_image = CTkLabel(logins1, text="", image=login1_bg_image_tk)
    login1_bg_image.place(x=0,y=0)

    login1_image = Image.open("assets/login.png").resize((100, 100))
    login1_image_tk = ImageTk.PhotoImage(login1_image)
    login1_lbl = CTkButton(logins1, text="", image=login1_image_tk, fg_color="#c2b19c", bg_color="#c2b19c", command=lambda: welcome_frame.tkraise())
    login1_lbl.place(x=570, y=130)

    username1_label=CTkLabel(logins1, text="Username:", font=("Montserrat", 20, "bold"), fg_color="#c2b19c", bg_color="#FFE4B5", text_color="#000000")
    username1_label.place(x=450, y=300)

    crew1_label=CTkLabel(logins1, text="LOG IN AS ADMIN", font=("Montserrat", 20, "bold"), fg_color="#c2b19c", bg_color="#FFE4B5", text_color="#000000")
    crew1_label.place(x=530, y=250)

    username1_entry=CTkEntry(logins1, placeholder_text="Username", placeholder_text_color="black", fg_color="#E2A76F", bg_color="#c2b19c", width=190)
    username1_entry.place(x=580, y=300)

    password1_label=CTkLabel(logins1, text="Password:", font=("Montserrat", 20, "bold"), fg_color="#c2b19c", bg_color="#FFE4B5", text_color="#000000")
    password1_label.place(x=450, y=350)

    password1_entry=CTkEntry(logins1, placeholder_text="Password",  fg_color="#E2A76F", show="*", placeholder_text_color="black", bg_color="#c2b19c", width=190)
    password1_entry.place(x=580, y=350)

    login1_button=CTkButton(logins1, text="LOGIN", font=("Montserrat", 15, "bold"), corner_radius=15, fg_color="#E2A76F", bg_color="#c2b19c", border_width=0, width=35, height=35, command=login2, text_color="#000000")
    login1_button.place(x=630, y=400)

    clear1_button=CTkButton(logins1, text="CLEAR", font=("Montserrat", 15, "bold"), corner_radius=15, fg_color="#E2A76F", bg_color="#c2b19c", border_width=0, width=35, height=35, command=clear_fields, text_color="#000000")
    clear1_button.place(x=530, y=400)
    logins1.tkraise()

pwd_radio_btn = CTkRadioButton(header_frame, text="PWD", variable=customer_type_var, value="PWD", font=("Roboto", 15), fg_color="#ffcca4", hover_color="#A72413")
pwd_radio_btn.place(x=750, y=20)

senior_radio_btn = CTkRadioButton(header_frame, text="Senior Citizen", variable=customer_type_var, value="Senior Citizen", font=("Roboto", 15), fg_color="#ffcca4", hover_color="#A72413")
senior_radio_btn.place(x=750, y=50)

admin_mode = CTkButton(header_frame, text="ADMIN MODE", width=20, font=("Roboto", 18), fg_color="#ffcca4", hover_color="#c2b19c", text_color="black", command=login1)
admin_mode.place(x=890, y=35)

time_header = CTkLabel(header_frame, text=strftime("%I:%M %p"), font=("Montserrat", 30, "bold"), text_color="#3B2F2F")
time_header.place(x=1030, y=30)

#mga product
# Product 1
product1_image = Image.open("assets/product1.png").resize((130, 130))
product1_image_tk = ImageTk.PhotoImage(product1_image)
product1_button = CTkButton(
    scroll_frame,
    image=product1_image_tk,
    text="",
    height=200,
    width=200,
    fg_color="#493D26",
    hover_color="#3B2F2F",
    command=lambda: add_to_receipt("Sourdough", 35)
)
product1_button.grid(column=0, row=0, padx=10, pady=10)
product1_label = CTkLabel(product1_button, text="Harvest Sun \n Sourdough ", font=("Helvetica", 20, "bold"), fg_color="#9F8C76", pady=0, padx=40, corner_radius=5)
product1_label.place(x=100, y=200, anchor="s")
product1_price = CTkLabel(product1_button, text="₱35", font=("Roboto", 25), text_color="black", fg_color="#e8a46c", corner_radius=5)
product1_price.place(x=145, y=0, anchor="nw")

# Product 2
product2_image = Image.open("assets/product2.png").resize((150, 110))
product2_image_tk = ImageTk.PhotoImage(product2_image)
product2_button = CTkButton(
    scroll_frame,
    image=product2_image_tk,
    compound="right",
    text="",
    font=("Roboto", 16),
    height=200,
    width=200,
    fg_color="#493D26",
    hover_color="#3B2F2F",
    command=lambda: add_to_receipt("Almond Croissant", 80)
)
product2_button.grid(column=1, row=0, padx=10, pady=10)
product2_label = CTkLabel(product2_button, text="Parisian Delight\nAlmond Croissant", font=("Helvetica", 18, "bold"), fg_color="#9F8C76", pady=0, padx=40, corner_radius=5)
product2_label.place(x=100, y=200, anchor="s")
product2_price = CTkLabel(product2_button, text="₱80", font=("Roboto", 25), text_color="black", fg_color="#e8a46c", corner_radius=5)
product2_price.place(x=145, y=0, anchor="nw")

# Product 3
product3_image = Image.open("assets/product3.png").resize((110, 110))
product3_image_tk = ImageTk.PhotoImage(product3_image)
product3_button = CTkButton(
    scroll_frame,
    image=product3_image_tk,
    compound="right",
    text="",
    font=("Roboto", 17),
    height=200,
    width=200,
    fg_color="#493D26",
    hover_color="#3B2F2F",
    command=lambda: add_to_receipt("Dream Cake", 120)
)
product3_button.grid(column=2, row=0, padx=10, pady=10)
product3_label = CTkLabel(product3_button, text="Scarlet Velvet\nDream Cake", font=("Helvetica", 18, "bold"), fg_color="#9F8C76", pady=0, padx=40, corner_radius=5)
product3_label.place(x=100, y=200, anchor="s")
product3_price = CTkLabel(product3_button, text="₱120", font=("Roboto", 25), text_color="black", fg_color="#e8a46c", corner_radius=5)
product3_price.place(x=135, y=0, anchor="nw")

# Product 4
product4_image = Image.open("assets/product4.png").resize((110, 110))
product4_image_tk = ImageTk.PhotoImage(product4_image)
product4_button = CTkButton(
    scroll_frame,
    image=product4_image_tk,
    compound="right",
    text="",
    font=("Roboto", 17),
    height=200,
    width=200,
    fg_color="#493D26",
    hover_color="#3B2F2F",
    command=lambda: add_to_receipt("Chocolate Cookie", 70)
)
product4_button.grid(column=0, row=1, padx=10, pady=10)
product4_label = CTkLabel(product4_button, text="Midnight Indulgence\nChocolate Chip Cookie", font=("Helvetica", 17, "bold"), fg_color="#9F8C76", pady=0, padx=40, corner_radius=5)
product4_label.place(x=100, y=200, anchor="s")
product4_price = CTkLabel(product4_button, text="₱70", font=("Roboto", 25), text_color="black", fg_color="#e8a46c", corner_radius=5)
product4_price.place(x=145, y=0, anchor="nw")

# Product 5
product5_image = Image.open("assets/product5.png").resize((145, 140))
product5_image_tk = ImageTk.PhotoImage(product5_image)
product5_button = CTkButton(
    scroll_frame,
    image=product5_image_tk,
    compound="right",
    text="",
    font=("Roboto", 16),
    height=200,
    width=200,
    fg_color="#493D26",
    hover_color="#3B2F2F",
    command=lambda: add_to_receipt("Blueberry Muffin", 35)
)
product5_button.grid(column=1, row=1, padx=10, pady=10)
product5_label = CTkLabel(product5_button, text="Morning Bliss\nBlueberry Muffin", font=("Helvetica", 18, "bold"), fg_color="#9F8C76", pady=0, padx=40, corner_radius=5)
product5_label.place(x=100, y=200, anchor="s")
product5_price = CTkLabel(product5_button, text="₱35", font=("Roboto", 25), text_color="black", fg_color="#e8a46c", corner_radius=5)
product5_price.place(x=145, y=0, anchor="nw")

# Product 6
product6_image = Image.open("assets/product6.png").resize((150, 150))
product6_image_tk = ImageTk.PhotoImage(product6_image)
product6_button = CTkButton(
    scroll_frame,
    image=product6_image_tk,
    compound="right",
    text="",
    font=("Roboto", 16),
    height=200,
    width=200,
    fg_color="#493D26",
    hover_color="#3B2F2F",
    command=lambda: add_to_receipt("Apple Pie", 149)
)
product6_button.grid(column=2, row=1, padx=10, pady=10)
product6_label = CTkLabel(product6_button, text="Granny’s Secret\nApple Pie", font=("Helvetica", 18, "bold"), fg_color="#9F8C76", pady=0, padx=40, corner_radius=5)
product6_label.place(x=100, y=200, anchor="s")
product6_price = CTkLabel(product6_button, text="₱149", font=("Roboto", 25), text_color="black", fg_color="#e8a46c", corner_radius=5)
product6_price.place(x=135, y=0, anchor="nw")

# Product 7
product7_image = Image.open("assets/product7.png").resize((130, 140))
product7_image_tk = ImageTk.PhotoImage(product7_image)
product7_button = CTkButton(
    scroll_frame,
    image=product7_image_tk,
    compound="right",
    text="",
    font=("Roboto", 16),
    height=200,
    width=200,
    fg_color="#493D26",
    hover_color="#3B2F2F",
    command=lambda: add_to_receipt("Wheat Bread", 330)
)
product7_button.grid(column=0, row=2, padx=10, pady=10)
product7_label = CTkLabel(product7_button, text="Golden Honey \n Wheat Bread", font=("Helvetica", 18, "bold"), fg_color="#9F8C76", pady=0, padx=40, corner_radius=5)
product7_label.place(x=100, y=200, anchor="s")
product7_price = CTkLabel(product7_button, text="₱330", font=("Roboto", 25), text_color="black", fg_color="#e8a46c", corner_radius=5)
product7_price.place(x=135, y=0, anchor="nw")

# Product 8
product8_image = Image.open("assets/product8.png").resize((140, 140))
product8_image_tk = ImageTk.PhotoImage(product8_image)
product8_button = CTkButton(
    scroll_frame,
    image=product8_image_tk,
    compound="right",
    text="",
    font=("Roboto", 16),
    height=200,
    width=200,
    fg_color="#493D26",
    hover_color="#3B2F2F",
    command=lambda: add_to_receipt("Cinnamon Roll", 50)
)
product8_button.grid(column=1, row=2, padx=10, pady=10)
product8_label = CTkLabel(product8_button, text="Caramel Bliss\nCinnamon Roll", font=("Helvetica", 18, "bold"), fg_color="#9F8C76", pady=0, padx=40, corner_radius=5)
product8_label.place(x=100, y=200, anchor="s")
product8_price = CTkLabel(product8_button, text="₱50", font=("Roboto", 25), text_color="black", fg_color="#e8a46c", corner_radius=5)
product8_price.place(x=135, y=0, anchor="nw")

# Product 9
product9_image = Image.open("assets/product9.png").resize((140, 130))
product9_image_tk = ImageTk.PhotoImage(product9_image)
product9_button = CTkButton(
    scroll_frame,
    image=product9_image_tk,
    compound="right",
    text="",
    font=("Roboto", 16),
    height=200,
    width=200,
    fg_color="#493D26",
    hover_color="#3B2F2F",
    command=lambda: add_to_receipt("Marshmallow Brownie", 99)
)
product9_button.grid(column=2, row=2, padx=10, pady=10)
product9_label = CTkLabel(product9_button, text="Campfire Toasted\nMarshmallow Brownie", font=("Helvetica", 18, "bold"), fg_color="#9F8C76", pady=0, padx=40, corner_radius=5)
product9_label.place(x=100, y=200, anchor="s")
product9_price = CTkLabel(product9_button, text="₱99", font=("Roboto", 25), text_color="black", fg_color="#e8a46c", corner_radius=5)
product9_price.place(x=135, y=0, anchor="nw")

# Add-ons
addons1_image = Image.open("assets/addons1.png").resize ((80, 80))
addons1_image_tk = ImageTk.PhotoImage(addons1_image)
addons1_button = CTkButton(
    drinks_frame,
    image =  addons1_image_tk,
    text="",
    height=70,
    width=130,
    hover_color="#3B2F2F",
    fg_color= "#493D26",
    command=lambda: add_to_receipt("Espresso Bliss Shot", 110)
)
addons1_button.grid(column=0, row=0, padx=15, pady=5)
addons1_price = CTkLabel(addons1_button, text="₱110", font=("Roboto", 15), text_color="black", fg_color="#e8a46c", corner_radius=5)
addons1_price.place(x=130, y=0, anchor="ne")

#d22 2 2 2222 
addons2_image = Image.open("assets/addons2.png").resize ((80, 80))
addons2_image_tk = ImageTk.PhotoImage(addons2_image)
addons2_button = CTkButton(
    drinks_frame,
    image =  addons2_image_tk,
    text="",
    height=70,
    width=130,
    hover_color="#3B2F2F",
    fg_color= "#493D26",
    command=lambda: add_to_receipt("Vanilla Caramel", 150)
)
addons2_button.grid(column=1, row=0, padx=15, pady=5)
addons2_price = CTkLabel(addons2_button, text="₱150", font=("Roboto", 15), text_color="black", fg_color="#e8a46c", corner_radius=5)
addons2_price.place(x=130, y=0, anchor="ne")

#d3 3 33333
addons3_image = Image.open("assets/addons3.png").resize ((80, 80))
addons3_image_tk = ImageTk.PhotoImage(addons3_image)
addons3_button = CTkButton(
    drinks_frame,
    image =  addons3_image_tk,
    text="",
    height=70,
    width=130,
    hover_color="#3B2F2F",
    fg_color= "#493D26",
    command=lambda: add_to_receipt("Hazelnut Delight", 180)
)
addons3_button.grid(column=2, row=0, padx=15, pady=5)
addons3_price = CTkLabel(addons3_button, text="₱180", font=("Roboto", 15), text_color="black", fg_color="#e8a46c", corner_radius=5)
addons3_price.place(x=130, y=0, anchor="ne")

#d 4 44444
addons4_image = Image.open("assets/addons4.png").resize ((80, 80))
addons4_image_tk = ImageTk.PhotoImage(addons4_image)
addons4_button = CTkButton(
    drinks_frame,
    image =  addons4_image_tk,
    text="",
    height=70,
    width=130,
    hover_color="#3B2F2F",
    fg_color= "#493D26",
    command=lambda: add_to_receipt("Classic Capuccino", 120)
)
addons4_button.grid(column=3, row=0, padx=15, pady=5)
addons4_price = CTkLabel(addons4_button, text="₱120", font=("Roboto", 15), text_color="black", fg_color="#e8a46c", corner_radius=5)
addons4_price.place(x=130, y=0, anchor="ne")

# BUTTONS
discount_button = CTkButton(welcome_frame, text="Discount", height=80, width=125, fg_color="#C19A6B", bg_color="#FFE4B5", font=("Montserrat", 25, "bold"), hover_color="#3B2F2F", command=apply_discount)
discount_button.place(x=20, y=620)
discount_button.configure(command=apply_discount)

void_button = CTkButton(welcome_frame, text="Void All", height=80, width=125, fg_color="#C19A6B", bg_color="#FFE4B5", font=("Montserrat", 25, "bold"), hover_color="#3B2F2F", command=void_orders)
void_button.place(x=180, y=620)

co_button = CTkButton(welcome_frame, text="Check Out", height=80, width=125, fg_color="#C19A6B", bg_color="#FFE4B5", font=("Montserrat", 25, "bold"), hover_color="#3B2F2F", command=checkout)
co_button.place(x=340, y=620)

logins.tkraise()
window.mainloop()