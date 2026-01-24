# This is The Python Program of Library Management System.
# Author : Sunil Mandloi 
# Email : sunilnarayan419@gmail.com 

import datetime
import os

class LMS:
    """ This class is used to keep record of books in a library management system.
    It has total four module: "Display books","Issue books", "Add books","Delete Books", "Return books" """

    def __init__(self, list_of_books, library_name):
        self.list_of_books = "books.csv"
        self.library_name = library_name
        self.books_dict = {}
        Id = 101

        with open(self.list_of_books) as bk:
            content = bk.readlines()
            for line in content:
                self.books_dict.update({
                    str(Id): {
                        "books_title": line.strip(),
                        "lender_name": "",
                        "Issue_date": "",
                        "Status": "Available"
                    }
                })
                Id += 1

    def display_books(self):
        print("______________List of books___________________")
        print("Book Id\t\tTitle\t\tStatus")
        print("_______________________________________________")
        for key, value in self.books_dict.items():
            print(key, "\t\t", value["books_title"], "[", value["Status"], "]")

    def Issue_books(self):
        books_id = input("Enter book ID: ")
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if books_id not in self.books_dict:
            print("Book ID not found !!")
            return

        if self.books_dict[books_id]["Status"] != "Available":
            print(
                f"This book is already issued to {self.books_dict[books_id]['lender_name']} "
                f"on {self.books_dict[books_id]['Issue_date']}"
            )
            return

        your_name = input("Enter your name: ")
        self.books_dict[books_id]["lender_name"] = your_name
        self.books_dict[books_id]["Issue_date"] = current_date
        self.books_dict[books_id]["Status"] = "Already Issued"
        print("Books Issued Successfully !!")

    def add_books(self):
        new_book = input("Enter book title: ").strip()

        if new_book == "":
            print("Title cannot be empty!")
            return

        if len(new_book) > 25:
            print("Book title too long! Max 25 chars.")
            return

        with open(self.list_of_books, "a") as bk:
            bk.write(new_book + "\n")

        new_id = str(int(max(self.books_dict.keys(), default="100")) + 1)

        self.books_dict[new_id] = {
            "books_title": new_book,
            "lender_name": "",
            "Issue_date": "",
            "Status": "Available"
        }

        print(f"Book '{new_book}' added successfully!")
        
    def delete_books(self):
        book_id = input("Enter book ID to delete: ").strip()

        if book_id == "":
            print("Book ID cannot be empty!")
            return

        if book_id not in self.books_dict:
            print("Book ID not found!")
            return

        deleted_book = self.books_dict[book_id]["books_title"]
        del self.books_dict[book_id]
        
        with open(self.list_of_books, "w") as bk:
            for value in self.books_dict.values():
                bk.write(value["books_title"] + "\n")

        print(f"Book '{deleted_book}' deleted successfully!")

    def return_books(self):
        book_id = input("Enter your book ID: ")

        if book_id not in self.books_dict:
            print("Book ID not found!")
            return

        if self.books_dict[book_id]["Status"] == "Available":
            print("Book already available in library.")
            return

        self.books_dict[book_id]["lender_name"] = ""
        self.books_dict[book_id]["Issue_date"] = ""
        self.books_dict[book_id]["Status"] = "Available"
        print("Book returned successfully!")


try:
    myLMS = LMS("list_of_book.csv", "Central Library UOH")

    press_key_list = {
        "D": "Display Books",
        "I": "Issue Books",
        "A": "Add Books",
        "B": "Delete Books",
        "R": "Return Books",
        "Q": "Quit"
    }

    while True:
        print(f"\n__________ Welcome To {myLMS.library_name} __________")

        for key, value in press_key_list.items():
            print("Press", key, "To", value)

        key_press = input("Press Key: ").lower()

        if key_press == "i":
            myLMS.Issue_books()

        elif key_press == "a":
            myLMS.add_books()
            
        elif key_press == "b":
            myLMS.delete_books() 

        elif key_press == "d":
            myLMS.display_books()

        elif key_press == "r":
            myLMS.return_books()

        elif key_press == "q":
            print("Exiting LMS. Goodbye!")
            break

        input("\nPress Enter to continue...")

except Exception as e:
    print("Something went wrong:", e)
