import ast
import sys
import io
import contextlib
from flask import Flask, jsonify, request
from flask_cors import CORS
import builtins
from unittest.mock import patch

# --- 1. Safe Loader for LMS Class ---
def load_lms_class(file_path):
    """
    Reads main.py, extracts the LMS class definition, and executes it
    so we can use the class without running the main loop.
    """
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    
    # Filter for only Import/ImportFrom and ClassDef nodes
    # We strictly want the class and necessary imports
    body_nodes = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.ClassDef)):
            body_nodes.append(node)
    
    # Create a new module with just these nodes
    module_ast = ast.Module(body=body_nodes, type_ignores=[])
    
    # Execute in a new namespace
    namespace = {}
    code = compile(module_ast, filename=file_path, mode='exec')
    exec(code, namespace)
    
    return namespace['LMS']

# Load the class
try:
    LMS = load_lms_class('main.py')
    print("Successfully loaded LMS class from main.py")
except Exception as e:
    print(f"Error loading LMS class: {e}")
    sys.exit(1)

# Initialize App and LMS
app = Flask(__name__)
CORS(app) # Enable CORS for frontend

# We maintain a single instance, matching the logic in main.py
lms = LMS("books.csv", "Central Library UOH")

# --- 2. Helper to Run Interactive Methods ---
def run_interactive_method(method, inputs):
    """
    Runs an interactive LMS method by mocking input() and capturing print() output.
    """
    input_iterator = iter(inputs)
    
    def side_effect(prompt=""):
        try:
            val = next(input_iterator)
            return val
        except StopIteration:
            raise ValueError("Not enough inputs provided for this operation")

    captured_output = io.StringIO()
    
    try:
        with patch('builtins.input', side_effect=side_effect):
            with contextlib.redirect_stdout(captured_output):
                method()
    except Exception as e:
        return False, str(e), captured_output.getvalue()

    return True, "Success", captured_output.getvalue()


# --- 3. API Endpoints ---

@app.route('/api/books', methods=['GET'])
def get_books():
    """Returns the books dictionary directly."""
    # Convert internal dict to list for easier frontend consumption
    # Structure: {id: {details...}}
    books_list = []
    for book_id, details in lms.books_dict.items():
        books_list.append({
            "id": book_id,
            **details
        })
    return jsonify(books_list)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    total = len(lms.books_dict)
    issued = sum(1 for b in lms.books_dict.values() if b["Status"] != "Available")
    return jsonify({
        "total_books": total,
        "issued_books": issued,
        "available_books": total - issued,
        "members": 150 # Mock value since member tracking isn't in backend
    })

@app.route('/api/issue', methods=['POST'])
def issue_book():
    data = request.json
    book_id = data.get('book_id')
    user_name = data.get('user_name')
    
    if not book_id or not user_name:
        return jsonify({"success": False, "message": "Missing book_id or user_name"}), 400

    # LMS.Issue_books asks for: Book ID, Name.
    inputs = [str(book_id), str(user_name)]
    
    success, error, logs = run_interactive_method(lms.Issue_books, inputs)
    
    # Check if logic succeeded by parsing logs or checking state (simple naive check for now)
    if "Book issued successfully" in logs:
        return jsonify({"success": True, "message": "Book Issued", "logs": logs})
    elif "Invalid Book ID" in logs:
        return jsonify({"success": False, "message": "Invalid Book ID", "logs": logs}), 404
    elif "Book already issued" in logs:
        return jsonify({"success": False, "message": "Book Already Issued", "logs": logs}), 409
    
    return jsonify({"success": success, "message": "Operation completed", "logs": logs})

@app.route('/api/return', methods=['POST'])
def return_book():
    data = request.json
    book_id = data.get('book_id')
    
    if not book_id:
        return jsonify({"success": False, "message": "Missing book_id"}), 400

    # LMS.return_books asks for: Book ID
    inputs = [str(book_id)]
    
    success, error, logs = run_interactive_method(lms.return_books, inputs)
    
    if "Book returned successfully" in logs:
        return jsonify({"success": True, "message": "Book Returned", "logs": logs})
    
    return jsonify({"success": success, "message": "Operation completed", "logs": logs})

@app.route('/api/add', methods=['POST'])
def add_book():
    data = request.json
    title = data.get('title')
    
    if not title:
        return jsonify({"success": False, "message": "Missing title"}), 400

    # LMS.add_books asks for: Title
    inputs = [str(title)]
    
    success, error, logs = run_interactive_method(lms.add_books, inputs)
    
    return jsonify({"success": True, "message": "Book Added", "logs": logs})

@app.route('/api/delete', methods=['POST'])
def delete_book():
    data = request.json
    book_id = data.get('book_id')
    confirm = data.get('confirm', 'y')
    
    # Check simple auth token mockup (optional)
    if request.headers.get('role') != 'admin':
         return jsonify({"success": False, "message": "Unauthorized"}), 403

    if not book_id:
        return jsonify({"success": False, "message": "Missing book_id"}), 400

    inputs = [str(book_id), str(confirm)]
    success, error, logs = run_interactive_method(lms.delete_books, inputs)
    
    if "Book deleted successfully" in logs:
        return jsonify({"success": True, "message": "Book Deleted", "logs": logs})
        
    return jsonify({"success": False, "message": "Delete Failed", "logs": logs})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    role = data.get('role') # 'admin' or 'student'
    
    if role == 'admin':
        password = data.get('password')
        # We know main.py uses "admin123" (hardcoded in line 150 of main.py, though local to try-block)
        # Since we load LMS class, we don't have access to the local var in 'try' block of main.py
        # BUT we can just duplicate this knowledge or try to read it. 
        # For robustness and "Hackathon Quality", let's match the legacy password.
        if password == "admin123":
             return jsonify({
                 "success": True, 
                 "user": {"name": "Administrator", "role": "admin", "id": "ADMIN-001"}
             })
        else:
             return jsonify({"success": False, "message": "Invalid Admin Password"}), 401
             
    elif role == 'librarian':
        password = data.get('password')
        if password == "lib123":
             return jsonify({
                 "success": True, 
                 "user": {"name": "Librarian", "role": "librarian", "id": "LIB-001"}
             })
        else:
             return jsonify({"success": False, "message": "Invalid Librarian Password"}), 401
              
    elif role == 'student':
        email = data.get('email')
        mobile = data.get('mobile')
        
        # Validation
        if not email or not mobile:
             return jsonify({"success": False, "message": "Email and Mobile required"}), 400
             
        # Regex check for email
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
             return jsonify({"success": False, "message": "Invalid Email Format"}), 400
             
        # Mobile check (10 digits)
        if not mobile.isdigit() or len(mobile) != 10:
             return jsonify({"success": False, "message": "Mobile must be 10 digits"}), 400
             
        # Success - Return a student user object
        # We derive a name from email for display
        name = email.split('@')[0].title()
        return jsonify({
            "success": True,
            "user": {"name": name, "role": "student", "email": email, "id": f"STD-{mobile[-4:]}"}
        })

    return jsonify({"success": False, "message": "Invalid Role"}), 400

    return jsonify({"success": False, "message": "Invalid Role"}), 400

# --- 3.1 History Endpoint ---
@app.route('/api/history', methods=['GET'])
def get_history():
    """Parses issue_log.txt to return structured history data."""
    if not hasattr(lms, 'log_file'):
        return jsonify([])

    history = []
    try:
        with open(lms.log_file, 'r') as f:
            for line in f:
                import re
                match = re.match(r"(.*?) (issued|returned) \'(.*?)\' on (.*)", line.strip())
                if match:
                    history.append({
                        "user": match.group(1),
                        "action": match.group(2),
                        "book": match.group(3),
                        "date": match.group(4)
                    })
                # Fallback for simple lines
                elif "issued" in line:
                    history.append({"raw": line.strip(), "action": "issued"})
    except FileNotFoundError:
        pass
    
    return jsonify(history[::-1])

# --- 4. AI Chatbot Logic ---

# In-Memory Knowledge Base for "Semantic" Search
# Maps keywords/concepts -> Book Title or ID hints
KNOWLEDGE_BASE = {
    "sherlock": ["Sherlock Holmes", "detective", "mystery", "client", "watson"],
    "holmes": ["Sherlock Holmes", "detective", "mystery", "client", "watson"],
    "watson": ["Sherlock Holmes"],
    "detective": ["Sherlock Holmes", "Case of the Lame Canary", "Agatha Christie"],
    "dinosaur": ["Jurassic Park"],
    "jurassic": ["Jurassic Park"],
    "langdon": ["Angels & Demons"],
    "illuminati": ["Angels & Demons"],
    "vatican": ["Angels & Demons"],
    "raskolnikov": ["Crime and Punishment"],
    "murder": ["Crime and Punishment", "Sherlock Holmes"],
    "napoleon": ["Animal Farm"],
    "pig": ["Animal Farm"],
    "communis": ["Animal Farm", "Karl Marx"],
    "big brother": ["1984" , "Animal Farm"], # 1984 might not be in csv, but good for chat
    "wizard": ["Harry Potter"], # If in CSV
    "magic": ["Harry Potter", "The Amulet of Samarkand"],
    "hobbit": ["Lord of the Rings"],
    "ring": ["Lord of the Rings"],
    "economics": ["Wealth of Nations", "Freakonomics", "Superfreakonomics"],
    "freak": ["Freakonomics"],
    "physics": ["Physics & Philosophy", "Tao of Physics", "Feynman"],
    "feynman": ["Surely You're Joking Mr Feynman"],
    "joking": ["Surely You're Joking Mr Feynman"],
    "wavelet": ["Fundamentals of Wavelets"],
    "signal": ["Fundamentals of Wavelets", "Signals and Systems"],
    "india": ["Discovery of India", "Integration of the Indian States", "India from Midnight to Milennium"],
    "nehru": ["Discovery of India"],
    "gandhi": ["My Experiments with Truth"],
    "hitler": ["Mein Kampf"],
    "war": ["Mein Kampf", "War and Peace", "Farewell to Arms", "Once There Was a War"],
    "hemingway": ["Farewell to Arms"],
    "steinbeck": ["Grapes of Wrath", "Russian Journal", "Moon is Down"],
    "grapes": ["Grapes of Wrath"],
    "monk": ["The Monk Who Sold His Ferrari"],
    "ferrari": ["The Monk Who Sold His Ferrari"],
    "kalam": ["Wings of Fire"],
    "fire": ["Wings of Fire", "Harry Potter", "Girl who played with Fire"],
    "girl": ["Girl with the Dragon Tattoo", "Girl who played with Fire"],
    "dragon": ["Girl with the Dragon Tattoo"],
    "tattoo": ["Girl with the Dragon Tattoo"],
    "vampire": ["Twilight", "Dracula"],
    "potter": ["Harry Potter"],
}

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '').lower()
    
    if not message:
        return jsonify({"response": "I'm listening! Ask me about any book, character, or topic."})

    # 1. Direct Search in Books (Title/Author)
    found_books = []
    for bid, info in lms.books_dict.items():
        if message in info['books_title'].lower() or message in info.get('author', '').lower():
            found_books.append(f"{info['books_title']} (ID: {bid})")

    # 2. Semantic Search in Knowledge Base
    # Check if any keyword in message exists in our KB
    related_concepts = []
    
    # Simple tokenization
    import re
    tokens = re.findall(r'\w+', message)
    
    for token in tokens:
        # Check direct matches in KB keys
        for key, values in KNOWLEDGE_BASE.items():
            if key in token: # e.g. "dinosaurs" matches "dinosaur"
                related_concepts.extend(values)
        
        # Check against mapped values (reverse lookup extremely simple)
        # (Skip for now to keep it fast)

    # Dedup
    found_books = list(set(found_books))
    related_concepts = list(set(related_concepts))
    
    response_text = ""
    
    if found_books:
        response_text += f"I found these books matching '{message}': " + ", ".join(found_books[:3]) + ". "
    
    if related_concepts:
        # Filter related concepts to see if they are actually in our library
        # This implementation assumes the KB values are Titles.
        # Let's find IDs for them.
        valid_recommendations = []
        for concept in related_concepts:
            # check if this concept title exists in books_dict values
            for bid, info in lms.books_dict.items():
                if concept.lower() in info['books_title'].lower():
                    valid_recommendations.append(f"{info['books_title']} (#{bid})")
        
        valid_recommendations = list(set(valid_recommendations))
        
        if valid_recommendations:
            response_text += f"Based on your interest in '{message}', you might like: " + ", ".join(valid_recommendations[:3]) + "."
        elif not found_books:
            response_text += f"I think you're looking for something related to {', '.join(related_concepts[:2])}, but I don't see it in stock right now."

    if not response_text:
        response_text = "I'm not sure which book you mean. Try mentioning a character, genre, or title keyword!"

    return jsonify({"response": response_text})

@app.route('/')
def index():
    try:
        from flask import render_template
        return render_template('index.html')
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask Adapter on port {port}...")
    # Debug mode should be False in production, but keeping True for demo unless ENV set.
    debug_mode = os.environ.get("FLASK_ENV") != "production"
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
