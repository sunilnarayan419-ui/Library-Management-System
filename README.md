# 📚 Library Management System (LMS)

A **console-based Library Management System** developed using **Python**, designed to manage basic library operations such as **adding, searching, issuing, returning, and deleting books** through a menu-driven interface.

This project demonstrates **Object-Oriented Programming (OOP)**, **file handling**, and **exception handling**, making it suitable for **hackathons, academic projects, and Python practice**.

---

##  Features

-  Display all books with ID and availability status  
-  Search books by **Book ID** or **Title keyword**  
-  Issue books with **date & time tracking**  
-  Return issued books with timestamp  
-  Add new books (Admin only)  
-  Delete books safely (Admin only)  
-  View summary (Total / Issued / Available books)  
-  Export library report to a text file  
-  Persistent storage using CSV files  
-  Admin-protected operations  

---

##  Technologies Used

- **Python 3**
- Built-in modules:
  - `datetime`
  - `os`
- File handling using **CSV & TXT files**
- Console-based UI

---

---

##  How the System Works

- Each book is assigned a **unique Book ID** starting from `101`
- Book data is stored in a **dictionary during runtime**
- Book titles are saved permanently in `books.csv`
- Issued books store:
  - Lender name
  - Issue date & time
  - Current status (`Available / Already Issued`)
- Admin-only actions require a **password**

---

##  How to Run the Project

1. **Clone the repository**
   ```bash
   git clone https://github.com/sunilnarayan419-ui/Library-Management-System.git





