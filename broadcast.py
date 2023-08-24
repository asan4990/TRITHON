import time, tribes_settings
from schedule import every, repeat, run_pending


@repeat(every(0.1).seconds)
def tribes_listener():
    """
    Repeater will listen to the specified PORT and any
    keywords fed in will search for any function association
    and execute.
    """

    data, _ = tribes_settings.tribes_socket.sock.recvfrom(4096)
    data = data.decode("utf-8").split()[2]

    # Search data for function
    find_func = tribes_settings.trithon.read_dict(data)

    # Try the function
    if find_func:
        tribes_settings.trithon_functions[data]()

while True:
    run_pending()
    time.sleep(1)
