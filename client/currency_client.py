import zmq
import os
import time


def main():
    context = zmq.Context()

    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5566")

    try:
        while True:
            os.system("cls" if os.name == "nt" else "clear")

            # Display menu options
            print("===[Currency Microservice Test Program]===")
            print("1. Preferred Currency Cost per Unit")
            print("2. Preferred Currency Cost")
            print("3. Compare Currency")
            print("4. Quit")
            user_choice = input("\nEnter your choice (1-4): ").strip()

            # User selected action
            request = {}

            if user_choice == "1":
                currency = (
                    input("\nEnter preferred currency code (EX: CAD): ").strip().upper()
                )

                cost = float(input("Enter cost in USD: "))
                units = float(input("Enter number of units: "))

                request = {
                    "action": "currency_per_unit",
                    "currency": currency,
                    "cost": cost,
                    "units": units,
                }

            elif user_choice == "2":
                currency = (
                    input("\nEnter preferred currency code (EX: CAD): ").strip().upper()
                )
                cost = float(input("Enter cost in USD: "))

                request = {
                    "action": "preferred_currency_cost",
                    "currency": currency,
                    "cost": cost,
                }

            elif user_choice == "3":
                currency1 = (
                    input("\nEnter first currency code (EX: CAD): ").strip().upper()
                )
                currency2 = (
                    input("Enter second currency code (EX: EUR): ").strip().upper()
                )

                cost = float(input("Enter cost in USD: "))

                request = {
                    "action": "compare_currency",
                    "currency1": currency1,
                    "currency2": currency2,
                    "cost": cost,
                }

            elif user_choice == "4":
                print("\nQuitting test program.")
                break

            else:
                print("\nInvalid choice...please try again!")
                time.sleep(0.5)
                continue

            # Send request to server
            socket.send_json(request)
            print(f"\nSent request: {request}")

            # Receive response from server
            response = socket.recv_json()
            print(f"\nReceived response: {response}")

            input("\nPlease press [Enter] to continue...")

    except KeyboardInterrupt:
        os.system("cls" if os.name == "nt" else "clear")
        print("Test program terminated, interrupted by user.")

    finally:
        socket.close()
        context.term()


if __name__ == "__main__":
    main()
