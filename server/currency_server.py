import zmq
import requests


def get_exchange_rates():
    RATES_API_URL = "https://open.er-api.com/v6/latest/USD"

    response = requests.get(RATES_API_URL)
    data = response.json()

    if data["result"] == "success":
        return data["rates"]
    else:
        print("\nError fetching exchange rates.")
        return None


# User Story 1: Cost Per Unit in Preferred Currency
def currency_per_unit(currency, cost, units, rates):
    if currency not in rates:
        return {"error": f"Currency {currency} not found in exchange rates."}

    rate = rates[currency]
    converted_cost = cost * rate
    cost_per_unit = converted_cost / units

    return {"currency": currency, "cost_per_unit": cost_per_unit}


# User Story 2: Cost in Preferred Currency
def preferred_currency_cost(currency, cost, rates):
    if currency not in rates:
        return {"error": f"Currency {currency} not found in exchange rates."}

    rate = rates[currency]
    converted_cost = cost * rate

    return {"currency": currency, "converted_cost": converted_cost}


# User Story 3: Compare Costs in Multiple Currencies
def compare_currency(currency1, currency2, cost, rates):
    if (currency1 not in rates) or (currency2 not in rates):
        return {
            "error": f"Currency {currency1} or {currency2} not found in exchange rates."
        }

    rate1 = rates[currency1]
    rate2 = rates[currency2]
    rate_currency1_to_currency2 = rate2 / rate1

    converted_cost1 = cost * rate1
    converted_cost2 = converted_cost1 * rate_currency1_to_currency2

    return {
        "currency1": currency1,
        "converted_cost1": converted_cost1,
        "currency2": currency2,
        "converted_cost2": converted_cost2,
        "rate_currency1_to_currency2": rate_currency1_to_currency2,
    }


def main():
    context = zmq.Context()

    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5566")

    print("\nMicroservice is running and listening for requests...")

    # Setup poller obj & register socket, use for 'Ctrl+C' stops
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    try:
        while True:
            # Poll socket with timeout (EX: 1000 ms)
            socks = dict(poller.poll(1000))

            if socket in socks and socks[socket] == zmq.POLLIN:
                try:
                    # Receive request from client
                    request = socket.recv_json()
                    print(f"\nReceived request: {request}")

                    rates = get_exchange_rates()
                    action = request.get("action")

                    # Process request & generate response
                    if not rates:
                        response = {"error": "Failed to fetch exchange rates."}

                    elif action == "currency_per_unit":
                        currency = request.get("currency")
                        cost = float(request.get("cost"))
                        units = float(request.get("units"))

                        response = currency_per_unit(currency, cost, units, rates)

                    elif action == "preferred_currency_cost":
                        currency = request.get("currency")
                        cost = float(request.get("cost"))

                        response = preferred_currency_cost(currency, cost, rates)

                    elif action == "compare_currency":
                        currency1 = request.get("currency1")
                        currency2 = request.get("currency2")
                        cost = float(request.get("cost"))

                        response = compare_currency(currency1, currency2, cost, rates)

                    else:
                        response = {"error": "No user action specified."}

                    # Send response to client
                    socket.send_json(response)
                    print(f"\nSent response: {response}")

                except Exception as e:
                    error_response = {"error": str(e)}
                    socket.send_json(error_response)
                    print(f"\nThere's an error: {e}")

            else:
                pass

    except KeyboardInterrupt:
        print("\nQuitting microservice program.")

    finally:
        socket.close()
        context.term()


if __name__ == "__main__":
    main()
