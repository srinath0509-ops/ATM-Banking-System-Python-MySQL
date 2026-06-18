import random
import mysql.connector

# ================= MYSQL CONNECTION =================
# Connect Python with MySQL database

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Srinath@123",
    database="atm_system"
)

cursor = db.cursor()

# ================= GENERATE ACCOUNT NUMBER =================
# Generates unique account number

def generate_account_number():

    while True:

        account_number = random.randint(100000, 999999)

        query = "SELECT * FROM accounts WHERE account_number = %s"

        cursor.execute(query, (account_number,))

        result = cursor.fetchone()

        if result is None:
            return account_number


# ================= CREATE ACCOUNT =================

def create_account():

    print("\n----------- Create Account -----------")

    name = input("Enter your name: ")

    while True:

        pin = input("Create 4-digit or 6-digit PIN: ")

        if pin.isdigit() and (len(pin) == 4 or len(pin) == 6):
            break

        print("Invalid PIN.")

    while True:

        try:

            balance = float(input("Enter initial deposit: $"))

            if balance >= 0:
                break

            print("Amount cannot be negative.")

        except ValueError:
            print("Enter valid amount.")

    account_number = generate_account_number()

    # Insert into accounts table
    query = """
    INSERT INTO accounts(account_number, name, pin, balance)
    VALUES (%s, %s, %s, %s)
    """

    values = (account_number, name, pin, balance)

    cursor.execute(query, values)

    db.commit()

    # ================= SAVE TRANSACTION =================

    query = """
    INSERT INTO transactions(account_number, transaction_type, amount, transaction_time)
    VALUES (%s, %s, %s, NOW())
    """

    cursor.execute(query, (account_number, "Initial Deposit", balance))

    db.commit()

    print("\nAccount Created Successfully!")
    print(f"Your Account Number is: {account_number}")


# ================= LOGIN =================

def login():

    try:

        account_number = int(input("Enter account number: "))

        query = "SELECT pin FROM accounts WHERE account_number = %s"

        cursor.execute(query, (account_number,))

        result = cursor.fetchone()

        if result is None:
            print("Account not found.")
            return None

        stored_pin = result[0]

        attempts = 3

        while attempts > 0:

            pin = input("Enter PIN: ")

            if pin == stored_pin:

                print("\nLogin Successful!")
                return account_number

            attempts -= 1

            print(f"Wrong PIN. Attempts left: {attempts}")

        print("Too many wrong attempts.")
        return None

    except ValueError:
        print("Invalid input.")
        return None


# ================= CHECK BALANCE =================

def check_balance(account_number):

    query = "SELECT balance FROM accounts WHERE account_number = %s"

    cursor.execute(query, (account_number,))

    result = cursor.fetchone()

    print(f"\nAvailable Balance: ${result[0]:.2f}")


# ================= DEPOSIT MONEY =================

def deposit_money(account_number):

    try:

        amount = float(input("Enter deposit amount: $"))

        if amount <= 0:
            print("Invalid amount.")
            return

        # Update balance
        query = """
        UPDATE accounts
        SET balance = balance + %s
        WHERE account_number = %s
        """

        cursor.execute(query, (amount, account_number))

        db.commit()

        # Save transaction
        query = """
        INSERT INTO transactions(account_number, transaction_type, amount, transaction_time)
        VALUES (%s, %s, %s, NOW())
        """

        cursor.execute(query, (account_number, "Deposit", amount))

        db.commit()

        print("\nDeposit Successful!")

    except ValueError:
        print("Invalid input.")


# ================= WITHDRAW MONEY =================

def withdraw_money(account_number):

    try:

        amount = float(input("Enter withdrawal amount: $"))

        # Get balance
        query = "SELECT balance FROM accounts WHERE account_number = %s"

        cursor.execute(query, (account_number,))

        balance = cursor.fetchone()[0]

        if amount <= 0:
            print("Invalid amount.")

        elif amount > balance:
            print("Insufficient balance.")

        else:

            # Update balance
            query = """
            UPDATE accounts
            SET balance = balance - %s
            WHERE account_number = %s
            """

            cursor.execute(query, (amount, account_number))

            db.commit()

            # Save transaction
            query = """
            INSERT INTO transactions(account_number, transaction_type, amount, transaction_time)
            VALUES (%s, %s, %s, NOW())
            """

            cursor.execute(query, (account_number, "Withdrawal", amount))

            db.commit()

            print("\nWithdrawal Successful!")

    except ValueError:
        print("Invalid input.")


# ================= TRANSFER MONEY =================

def transfer_money(sender_account):

    try:

        receiver_account = int(input("Enter receiver account number: "))

        # Check receiver exists
        query = "SELECT * FROM accounts WHERE account_number = %s"

        cursor.execute(query, (receiver_account,))

        result = cursor.fetchone()

        if result is None:
            print("Receiver account not found.")
            return

        amount = float(input("Enter transfer amount: $"))

        # Get sender balance
        query = "SELECT balance FROM accounts WHERE account_number = %s"

        cursor.execute(query, (sender_account,))

        sender_balance = cursor.fetchone()[0]

        if amount <= 0:
            print("Invalid amount.")

        elif amount > sender_balance:
            print("Insufficient balance.")

        else:

            # Deduct sender balance
            query = """
            UPDATE accounts
            SET balance = balance - %s
            WHERE account_number = %s
            """

            cursor.execute(query, (amount, sender_account))

            # Add receiver balance
            query = """
            UPDATE accounts
            SET balance = balance + %s
            WHERE account_number = %s
            """

            cursor.execute(query, (amount, receiver_account))

            db.commit()

            # Save sender transaction
            query = """
            INSERT INTO transactions(account_number, transaction_type, amount, transaction_time)
            VALUES (%s, %s, %s, NOW())
            """

            cursor.execute(query, (sender_account, "Transfer Sent", amount))

            # Save receiver transaction
            query = """
            INSERT INTO transactions(account_number, transaction_type, amount, transaction_time)
            VALUES (%s, %s, %s, NOW())
            """

            cursor.execute(query, (receiver_account, "Transfer Received", amount))

            db.commit()

            print("\nTransfer Successful!")

    except ValueError:
        print("Invalid input.")


# ================= MINI STATEMENT =================
# Shows all transaction history

def mini_statement(account_number):

    print("\n----------- MINI STATEMENT -----------")

    query = """
    SELECT transaction_type, amount, transaction_time
    FROM transactions
    WHERE account_number = %s
    ORDER BY transaction_time DESC
    """

    cursor.execute(query, (account_number,))

    result = cursor.fetchall()

    if len(result) == 0:
        print("No transactions found.")

    else:

        for row in result:

            print(
                f"{row[2]} | {row[0]} | ${row[1]:.2f}"
            )
    print(check_balance(account_number))


# ================= LOGOUT =================

def logout():

    confirm = input("Are you sure you want to logout? (yes/no): ")

    if confirm.lower() == "yes":

        print("\nThank you for using our ATM services.")
        exit()


# ================= ATM MACHINE =================

def atm_machine():

    print("=========== Welcome To Mini ATM Machine ===========")

    while True:

        print("\n1. Create Account")
        print("2. Login")
        print("3. Logout")

        try:

            choice = int(input("Enter your choice: "))

            if choice == 1:

                create_account()

            elif choice == 2:

                account_number = login()

                if account_number:

                    while True:

                        print("\n----------- ATM MENU -----------")
                        print("1. Check Balance")
                        print("2. Deposit Money")
                        print("3. Withdraw Money")
                        print("4. Transfer Money")
                        print("5. Mini Statement")
                        print("6. Logout")

                        option = int(input("Enter your option: "))

                        if option == 1:
                            check_balance(account_number)

                        elif option == 2:
                            deposit_money(account_number)

                        elif option == 3:
                            withdraw_money(account_number)

                        elif option == 4:
                            transfer_money(account_number)

                        elif option == 5:
                            mini_statement(account_number)

                        elif option == 6:
                            print("\nLogged out successfully.")
                            break

                        else:
                            print("Invalid option.")

            elif choice == 3:

                logout()

            else:
                print("Choose between 1 to 3.")

        except ValueError:
            print("Enter numbers only.")


# ================= START PROGRAM =================

atm_machine()