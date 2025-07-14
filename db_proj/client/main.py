from auth import register, login

def show_menu():
    print("\n=== QUIZ GAME MENU ===")
    print("1. Register")
    print("2. Login")
    print("3. Exit")

def main():
    user = None  

    while True:
        show_menu()
        choice = input("Choose an option (1–3): ")

        if choice == "1":
            user = register()
        elif choice == "2":
            user = login()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")
        if user:
            print(f"🎉 Hello {user}! You're now logged in.")
            break 

if __name__ == "__main__":
    main()
