from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")  # Replace with your MongoDB URI
db = client["library_db"]  # Replace with your database name
books = db["books"] 



# Hardcoded credentials for demo purposes
# users = {
#     'admin': {'password': 'admin123', 'role': 'admin'},
#     'user': {'password': 'user123', 'role': 'user'}
# }

@app.route('/')
def home():
    # Render index.html for the main login page
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.users.find_one({"username": username, "password": password})
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            
            if user['role'] == 'user':
                return redirect(url_for('user_page'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin_page'))
        else:
            flash('Invalid Credentials. Please try again.')
            return redirect(url_for('home'))

    return render_template('index.html')
@app.route('/admin')
def admin_page():
    if session.get('role') == 'admin':
        books = list(db.books.find())

        return render_template('admin.html', books= books, username=session['username'])
    else:
        flash('Unauthorized access!')
        return redirect(url_for('home'))
    

@app.route('/user')
def user_page():
    # Check if the user's role is 'user'
    if session.get('role') == 'user':
        # Fetch books from the database
        books = list(db.books.find())
        
        # Render the admin page with books data (if applicable)
        return render_template('user.html', books=books, username=session['username'])
    else:
        # Flash unauthorized access message and redirect
        flash('Unauthorized access!')
        return redirect(url_for('home'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/home')
def home_redirect():
    if 'username' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_page'))
        elif role == 'user':
            return redirect(url_for('user_page'))
    return redirect(url_for('home'))

@app.route('/admin_book_issue')
def admin_book_issue():
    if session.get('role') == 'admin':
        return render_template('admin_bookIssue.html')
    else:
        flash('Unauthorized access!')
        return redirect(url_for('home'))
#user issue book
@app.route('/user_book_issue', methods=['POST', 'GET'])
def user_book_issue():
    if session.get('role') == 'user':
        if request.method == 'POST':
            Code = int(request.form.get('Code'))
            bookName = request.form.get('BookName')
            issue_date = request.form.get('issueDate')
            return_date = request.form.get('returnDate')
            Remarks = request.form.get('remarks')
            username = session.get('username')


            if bookName and issue_date and return_date:
                db.Issued_books.insert_one({
            # "user_id": session['username'],
                "Code":Code,
                "book_name": bookName,
                "issue_date": issue_date,
                "return_date": return_date,
                "remarks": Remarks,
                "username": username,
                })

            # Decrease the book quantity by 1
                result = db.books.update_one(
                    {"Code": Code},  # Find the book by Code_No
                    {"$inc": {"quantity": -1}}  # Decrease quantity
                )

            # Check if the update was successful
                if result.matched_count > 0 and result.modified_count > 0:
                    flash("Book issued successfully!", "success")
                else:
                    flash("Book issue failed: Book not found or insufficient quantity.", "error")
                return redirect(url_for('user_page'))

        flash("Unauthorized access!", "error")
        return render_template('user_bookIssue.html')

@app.route('/transactions')
def transactions_page():
    if 'role' in session:
        role = session['role']
        print(f"User role: {role}")  # Debugging line to ensure role is set
        if role == 'admin':
            return render_template('admin_transactions.html')
        elif role == 'user':
            return render_template('user_transactions.html')
    flash('Please log in to access transactions.')
    return redirect(url_for('home'))


@app.route('/search_results', methods=['POST', 'GET'])
def search_results():
    return render_template('search_results.html')

#return Book
@app.route('/admin/returnbook', methods=['GET', 'POST'])
def admin_returnbook():
    if request.method == 'POST':
        book_name = request.form.get('bookName')
        return_date = request.form.get('returnDate')
        remarks = request.form.get('remarks')

        return redirect(url_for('admin_transactions'))

    return render_template('admin_returnbook.html')

@app.route('/user_return_book', methods=['GET', 'POST'])
def user_return_book():
    if request.method == 'POST':
        # Fetch form data for returning the book
        book_name = request.form.get('returnBookDropdown')
        return_date = request.form.get('returnDate')
        remarks = request.form.get('remarks')

        # Perform return book logic (e.g., check if the book is eligible for return, process return, etc.)

        if not book_name or not return_date:
            flash('Please provide all mandatory fields!', 'error')
            return redirect(url_for('user_return_book'))

        # If successful:
        flash(f'Book "{book_name}" returned successfully!', 'success')
        return redirect(url_for('user_transactions'))
    
    # Render the return book page
    return render_template('user_returnbook.html')
#payfine

@app.route('/admin/payfine', methods=['GET', 'POST'])
def admin_payfine():
    if request.method == 'POST':
        user_id = request.form.get('userId')
        fine_amount = request.form.get('fineAmount')
        remarks = request.form.get('remarks')

        # Process the fine payment as needed

        return redirect(url_for('admin_page'))  # Or another endpoint
    return render_template('admin_payfine.html')

@app.route('/user_payfine', methods=['GET', 'POST'])
def user_payfine():
    if session.get('role') == 'user':
        if request.method == 'POST':
            book_name = request.form.get('bookName')
            author = request.form.get('author')
            serial_no = request.form.get('serialNo')
            issue_date = request.form.get('issueDate')
            return_date = request.form.get('returnDate')
            actual_return_date = request.form.get('actualReturnDate')
            fine_calculated = request.form.get('fineCalculated')
            fine_paid = 'finePaid' in request.form  # Checkbox

            # Add logic to handle fine payment submission
            if not book_name or not serial_no or not fine_calculated:
                flash('Please fill all mandatory fields!', 'error')
                return render_template('user_payfine.html')

            # Process the fine payment
            flash('Fine payment recorded successfully!', 'success')
            return redirect(url_for('user_page'))

        return render_template('user_payfine.html')
    else:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('home'))

@app.route('/maintenance', methods=['GET'])
def maintenance_home():
    return render_template('maintenance_home.html')
@app.route('/add_membership', methods=['GET', 'POST'])
def add_membership():
    if request.method == 'POST':
        membership_Type = request.form.get('membershipType')
        start_Date = request.form.get('startDate')
        End_Date = request.form.get('endDate')
        User_Name = request.form.get('username')
        Email = request.form.get('email')
        Phone_Number = request.form.get('phone')

        if membership_Type and start_Date and End_Date and User_Name and Email and Phone_Number:
            db.Membership_dt.insert_one({
                "membership_type": membership_Type,
                "start_Date": start_Date,
                "End_Date": End_Date,
                "User_Name": User_Name,
                "Email": Email,
                "Phone_Number": Phone_Number
            })
            return redirect(url_for('admin_page'))
                   
    return render_template('add_membership.html')

@app.route('/update_membership', methods=['GET', 'POST'])
def update_membership():
    username = request.form.get('username') 
    # membership = db.Membership_dt.find_one({"User_Name": username})
    if request.method == 'POST':
        membership_Type = request.form.get('membershipType')
        start_Date = request.form.get('startDate')
        End_Date = request.form.get('endDate')
        User_Name = request.form.get('username')
        Email = request.form.get('email')
        Phone_Number = request.form.get('phone')

        if membership_Type and start_Date and End_Date and User_Name and Email and Phone_Number:
            db.Membership_dt.update_one(
                {"User_Name": username}, 
                {"$set": {
                    "membership_type": membership_Type,
                    "start_Date": start_Date,
                    "End_Date": End_Date,
                    "User_Name": User_Name,
                    "Email": Email,
                    "Phone_Number": Phone_Number
                }}
            )
            return redirect(url_for('admin_page'))

    return render_template('update_membership.html')
@app.route('/add_update_media', methods=['GET', 'POST'])

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # Retrieve form data
        Code = int(request.form.get("Code"))
        Book_Name = request.form.get('bookName')
        procurement_date = request.form.get('procurementDate')
        quantity = int(request.form.get('quantity'))

        # Check if all fields are filled and quantity is valid
        if  Book_Name and procurement_date and int(quantity) > 0:
            db.books.insert_one({
                "Code": Code,
                "Book_Name": Book_Name,
                "procurement_date": procurement_date,
                "quantity": quantity 
            })
            # flash("Book added successfully!", "success")
            return redirect(url_for('admin_page'))           
         # Redirect to a success page or another route after processing# Change 'success_page' to your actual success rout
        # else:
            # If validation fails, reload the form with an error message
            # error_message = "Please fill all the fields correctly."
            # return render_template('add_book.html', error_message=error_message)
            # flash("Please fill all fields correctly.", "error")
    # Render the form for GET requests
    return render_template('add_book.html')

# Route to display success message or handle success logic
@app.route('/success')
def success_page():
    return "Successfull!"
@app.route('/update')
def update_page():
    return "Successfull!"

@app.route('/update_book', methods=['GET', 'POST'])
def update_book():
    if request.method == 'POST':
        # Retrieve form data
        Code = int(request.form.get("Code"))
        Book_Name = request.form.get('bookName')
        procurement_date = request.form.get('procurementDate')
        quantity = int(request.form.get('quantity'))

        # Check if all fields are filled
        if Book_Name and procurement_date and quantity:
            db.books.update_one({"Code": Code},{"$set": {"Book_Name": Book_Name, "procurement_date": procurement_date, "quantity": quantity}})
            return redirect(url_for('admin_page'))
        else:
            # If validation fails, reload the form with an error message
            error_message = "Please fill all the required fields."
            return render_template('update_book.html', error_message=error_message)
    
    # Render the form for GET requests
    return render_template('update_book.html')
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        # Retrieve form data
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        role = request.form.get('role')
        # Validate required fields
        if not full_name or not username or not email or not phone_number or not password or not role:
            flash('All required fields must be filled!', 'error')
            return render_template('add_user.html')

        # Check if the username or email already exists
        if db.Add_user.find_one({'username': username}) or db.Add_user.find_one({'email': email}):
            flash('Username or email already exists!', 'error')
            return render_template('add_user.html')

        # Hash the password for secure storage
        # hashed_password = generate_password_hash(password)

        # Insert the user data into the database
        user_data = {
            "full_name": full_name,
            "username": username,
            "email": email,
            "phone_number": phone_number,
            "password": password,
            "role": role,
        }

        db.Add_user.insert_one(user_data)
        db.users.insert_one(user_data)
        flash('User added successfully!', 'success')
        return redirect(url_for('admin_page'))

    return render_template('add_user.html')


@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
    if request.method == 'POST':
        username = request.form.get('username') 
        # Retrieve form data
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        role = request.form.get('role')
    
        # Check if all required fields are filled
        if full_name and username and email and phone_number and password and role:
            db.Add_user.update_one(
                {"username": username}, 
                {"$set": {
                    "full_name": full_name,
                    "email": email,
                    "phone_number": phone_number,
                    "password": password,
                    "role": role,
                }}
            )
            return redirect(url_for('admin_page'))
        
    return render_template('update_user.html')
    

books = [
    {"name": "Book A", "author": "Author A", "serial": 12345, "available": "Y"},
    {"name": "Book B", "author": "Author B", "serial": 67890, "available": "Y"},
    {"name": "Book C", "author": "Author C", "serial": 54321, "available": "Y"},
    {"name": "Book D", "author": "Author D", "serial": 98765, "available": "N"}
]

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Get the search query from the form (e.g., book name or author)
        search_query = request.form.get('search_query', '').lower()

        # Filter the books based on the search query
        results = [book for book in books if search_query in book['name'].lower() or search_query in book['author'].lower()]

        # Render the template with the search results
        #return render_template('search_results.html', books=results)
    
    # If it's a GET request, just display the search form
    return render_template('search_form.html')

#cancel
@app.route('/cancel')
def cancel_page():
    return render_template('cancel.html')
#reports
@app.route('/reports')
def reports():
    # Ensure session is active and the role is admin
    if 'role' in session and session['role'] == 'admin':
        return render_template('reports.html')
    else:
        flash('Unauthorized access! Please log in as admin.')
        return redirect(url_for('login'))


@app.route('/book-availability')
def book_availability():

    return render_template('Book_available.hmtl')

@app.route('/Search-results')
def Search_result():
    books = list(db.books.find())

    return render_template('Search_result.html',books=books)

@app.route('/M_book_list')
def Master_book_list():
    return render_template('master_books.html')

@app.route('/M_movie_list')
def Master_movie_list():
    return render_template('master_movies.html')

@app.route('/M_member_list')
def Master_membership_list():
    return render_template('master_membership.html')

@app.route('/Active Issues')
def Active_Issues():
    return render_template('Active_Issues.html')

@app.route('/Overdue_returns')
def Overdue_returns():
    return render_template('Overdue_returns.html')


@app.route('/Issue_request')    
def Issue_request():
    # if session.get('role') == 'user':
    #     # Retrieve form data
    #     Code_No = request.form.get('CodeNo')
    #     Book_name = request.form.get('BookName')
    #     issue_date = request.form.get('issueDate')
    #     return_date = request.form.get('returnDate')
    #     Remark = request.form.get('remarks')

    #     # # Validate input fields
    #     # if not Code_No or not issue_date or not return_date:
    #     #     flash("All fields are required!", "error")
    #     #     return redirect(url_for('user_page'))

    #     # try:
    #     #     # Cast Code_No to the correct type if necessary
    #     #     Code_No = int(Code_No)

    #     #     # Fetch book details from the database
    #     #     book = db.books.find_one({"_id": Code_No})

    #     #     if not book:
    #     #         # Book does not exist in the database
    #     #         flash("Invalid book code. Please try again.", "error")
    #     #         return redirect(url_for('user_page'))

    #     #     # Check if the book is available
    #     #     if book.get("available") == "N":
    #     #         # Book is already issued
    #     #         flash(f"Book '{book.get('title', 'Unknown')}' is currently issued to another user.", "error")
    #     #         return redirect(url_for('user_page'))

    #         # # Fetch book status (optional, for display purposes)
    #         # book_status = book.get("status", "No status available")
    #         # flash(f"Book Status: {book_status}", "info")

    #         # Insert a new record into the Issued_books collection
    #     db.Issued_books.insert_one({
    #         # "user_id": session['username'],
    #         "Code_No": Code_No,
    #         "book_name":Book_name,
    #         "issue_date": issue_date,
    #         "return_date": return_date,
    #         "remark":Remark
    #     })

    #         # Update book availability in the books collection
    #         # db.books.update_one(
    #         #     {"_id": Code_No},
    #         #     {"$set": {"available": "N", "status": "issued"}}
    #         # )
    #     return redirect(url_for('user_page'))

        # except Exception as e:
        #     # Handle unexpected errors
        #     flash(f"An error occurred: {str(e)}", "error")
        #     return redirect(url_for('user_page'))

    # Unauthorized access
    # # flash("Unauthorized access!", "error")
    return render_template('user_bookIssue.html')


if __name__ == '__main__':
    app.run(debug=True)
