import sqlite3
import os.path
from sys import exit
from hashlib import pbkdf2_hmac

##############################
#   INITIALIZATION
##############################

# Setting for password hashing
SALT = b'?\x9a\xcbnx\x14\x1b \xb7\x19\x1d\x90\xf8\xcd\x93&'
ITERATIONS = 1000

##############################
#   MAIN
##############################

# Run bot
def main():

    path = "telegram.db"

    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"'{path}' not found")
            
        con = sqlite3.connect(path)

    except Exception as e:
        exit(-1)

    while True:
        print("1) View Users\n")
        print("2) Register User\n")
        print("3) Delete User\n")
        print("Select action: ")
        choice = int(input())

        if choice < 1 or choice > 3:
            print("\nInvalid selection, retry\n")    
        else:
            break

    if choice == 1:
        cur = con.cursor()
        cur.execute('SELECT * FROM USERS')

        rows = cur.fetchall()
        
        for row in rows:
            print(row)

    elif choice == 2:
        print("Insert username: ")
        username = input()

        print("Insert password: ")
        password = input()

        print("Insert name: ")
        name = input()

        print("Insert surname: ")
        surname = input()

        print("Insert level: ")
        level = input()

        password_hash = pbkdf2_hmac('sha256', password.encode(), SALT, ITERATIONS).hex()

        con.execute('''INSERT INTO USERS 
                       VALUES(?,?,?,?,?)''', (username, password_hash, name, surname, level))
        con.commit()


    elif choice == 3:
        print("\nInsert username of user to delete: ")
        username = input()

        con.execute('''DELETE FROM USERS WHERE USERNAME=?''', (username,))
        con.commit()


if __name__ == "__main__":
    main()