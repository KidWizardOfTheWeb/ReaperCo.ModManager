import time
from pypresence import Presence, PyPresenceException
import asyncio

def RPC_loop(client_id):
    RPC = Presence(client_id=client_id)  # Initialize the client class
    RPC.connect()  # Start the handshake loop

    # TODO: add a way to update the info here
    print(
        RPC.update(
            state="In Manager",
            # details="Editing mods",
            name="Reaper Co. Mod Manager",
        )
    )  # Set the presence
    # time.sleep(5)
    # while True:  # The presence will stay on as long as the program is running
    #     time.sleep(15)  # Can only update rich presence every 15 seconds