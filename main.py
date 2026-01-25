# This is The Python Program of Library Management System.
# Author : Sunil Mandloi 
# Email : sunilnarayan419@gmail.com 

# This is The Python Program of Library Management System.
# Author : Sunil Mandloi 
# Email : sunilnarayan419@gmail.com 
import datetime
import os
class LMS:
    """ This class is used to keep record of book library.
    It has total six module: "Display Books", "Search Books", "Issue Books" ,
    "Add Books", "Delete Books", "Return Books" """
    def __init__(self, list_of_books, library_name):
        self.list_of_books = "books.csv"
        self.issued_file = "issued_books.csv"
        self.log_file = "issue_log.txt"
        self.library_name = library_name
        self.books_dict = {}
        Id = 101
        for file in [self.list_of_books, self.issued_file, self.log_file]:
            if not os.path.exists(file):
                open(file, "w").close()
        with open(self.list_of_books) as bk:
            for line in bk.readlines():
                self.books_dict[str(Id)] = {
                    "books_title": line.strip(),
                    "lender_name": "",
                    "Issue_date": "",
                    "Status": "Available"
                }
                Id += 1
    # DISPLAY
    def display_books(self, sort_by_title=False):
        books = sorted(
            self.books_dict.items(),
            key=lambda x: x[1]["books_title"]
        ) if sort_by_title else self.books_dict.items()
        print("\nID\tTitle\t\t\tStatus")
        print("-" * 45)
        for key, value in books:
            print(key, value["books_title"], "[", value["Status"], "]")
    # SEARCH
    def search_books(self):
        query = input("Enter Book ID or Title keyword: ").lower()
        found = False
        for key, value in self.books_dict.items():
            if query == key or query in value["books_title"].lower():
                print(key, value["books_title"], "[", value["Status"], "]")
                found = True
        if not found:
            print("No matching book found.")
    # ISSUE
    def Issue_books(self):
        book_id = input("Enter book ID: ")
        if book_id not in self.books_dict:
            print("Invalid Book ID")
            return
        if self.books_dict[book_id]["Status"] != "Available":
            print("Book already issued!")
            return
        name = input("Enter your name: ")
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.books_dict[book_id]["lender_name"] = name
        self.books_dict[book_id]["Issue_date"] = date
        self.books_dict[book_id]["Status"] = "Already Issued"
        with open(self.issued_file, "a") as f:
            f.write(f"{book_id},{name},{date}\n")
        with open(self.log_file, "a") as log:
            log.write(
                f"{name} issued '{self.books_dict[book_id]['books_title']}' on {date}\n"
            )
        print(f"Book issued successfully on {date}")
    # ADD
    def add_books(self):
        title = input("Enter book title: ").strip()
        if not title:
            print("Empty title not allowed")
            return
        new_id = str(int(max(self.books_dict.keys(), default="100")) + 1)
        self.books_dict[new_id] = {
            "books_title": title,
            "lender_name": "",
            "Issue_date": "",
            "Status": "Available"
        }
        with open(self.list_of_books, "a") as f:
            f.write(title + "\n")
        print("Book added successfully!")
    # DELETE
    def delete_books(self):
        book_id = input("Enter book ID to delete: ")
        if book_id not in self.books_dict:
            print("Book ID not found")
            return
        if self.books_dict[book_id]["Status"] != "Available":
            print("Cannot delete issued book!")
            return
        confirm = input("Are you sure? (y/n): ").lower()
        if confirm != "y":
            print("Delete cancelled")
            return
        del self.books_dict[book_id]
        with open(self.list_of_books, "w") as f:
            for v in self.books_dict.values():
                f.write(v["books_title"] + "\n")
        print("Book deleted successfully!")
    # RETURN
    def return_books(self):
        book_id = input("Enter book ID: ")
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if book_id not in self.books_dict:
            print("Invalid Book ID")
            return
        self.books_dict[book_id]["Status"] = "Available"
        self.books_dict[book_id]["lender_name"] = ""
        self.books_dict[book_id]["Issue_date"] = ""
        print(f"Book returned successfully on {date}")
    # SUMMARY
    def show_summary(self):
        total = len(self.books_dict)
        issued = sum(
            1 for b in self.books_dict.values()
            if b["Status"] != "Available"
        )
        print(f"Total: {total} | Issued: {issued} | Available: {total - issued}")
    # REPORT
    def export_report(self):
        with open("library_report.txt", "w") as r:
            r.write("Library Report\n")
            r.write("=" * 20 + "\n")
            for k, v in self.books_dict.items():
                r.write(f"{k} - {v['books_title']} [{v['Status']}]\n")
        print("Report exported!")

# MAIN
try:
    lms = LMS("books.csv", "Central Library UOH")
    ADMIN_PASSWORD = "admin123"
    while True:
        print(f"\nWelcome to {lms.library_name}")
        print("""
D - Display Books
S - Search Books
I - Issue Book
A - Add Book (Admin)
B - Delete Book (Admin)
R - Return Book
C - Summary
E - Export Report
Q - Quit
""")
        choice = input("Enter choice: ").lower()
        if choice == "a" or choice == "b":
            pwd = input("Enter admin password: ")
            if pwd != ADMIN_PASSWORD:
                print("Wrong password!")
                continue
        if choice == "d":
            lms.display_books()
        elif choice == "s":
            lms.search_books()
        elif choice == "i":
            lms.Issue_books()
        elif choice == "a":
            lms.add_books()
        elif choice == "b":
            lms.delete_books()
        elif choice == "r":
            lms.return_books()
        elif choice == "c":
            lms.show_summary()
        elif choice == "e":
            lms.export_report()
        elif choice == "q":
            print("Thank you!")
            break
        else:
            input("Press Enter to continue...")
except Exception as e:
    print("Something went wrong. Please check your input!!")
