import serial
import time
import threading
import config


class PowerSocketsController:
    def __init__(self, port, baudrate, timeout=1, settle_time=3):
        self.port = port
        self.baud = baudrate
        self.timeout = timeout
        self.settle_time = settle_time
        self.lock = threading.Lock()  # Thread lock to ensure only one thread uses the UART port
        self.serial = None

        try:
            self.serial = serial.Serial(port, baudrate, timeout=timeout)
            time.sleep(settle_time)
        except Exception as e:
            print(f"ERROR: {e}")

    def reinit(self):
        """Re-initialization in case of failure."""
        if self.serial:
            self.serial.close()
        try:
            self.serial = serial.Serial(self.port, self.baud, timeout=self.timeout)
            time.sleep(self.settle_time)
            return self.get_state()
        except Exception as e:
            print(f"ERROR: {e}")
        return None

    def send_command(self, cmd):
        """Send command to the device and return response."""
        with self.lock:  # Ensure thread-safe access to the serial port
            try:
                self.serial.reset_input_buffer()  # Clear any junk left over
                self.serial.write(cmd.encode('utf-8'))
                response = self.serial.readline().decode('utf-8').strip()

                if response:
                    if not response.startswith('s:'):
                        raise ValueError(f"Unexpected response: {response}")
                    states = response[2:]  # Remove "s:" part
                    if len(states) != 2:
                        raise ValueError(f"Invalid state format: {states}")
                    return [int(state) for state in states]
            except Exception as e:
                print(f"ERROR during command send: {e}")
                self.reinit()  # Attempt to reinitialize on error

        return None

    def get_state(self):
        """Get the current state of the sockets."""
        return self.send_command('g:00')  # Query device for state

    def set_socket(self, socket_number, state):
        """Set individual socket ON (1) or OFF (0)."""
        if socket_number not in (0, 1):
            print("ERROR: Socket number must be 0 or 1")
            return None
        if state not in (0, 1):
            print("ERROR: State must be 0 (OFF) or 1 (ON)")
            return None

        cmd = f"s:{socket_number}{state}"
        return self.send_command(cmd)

    def set_socket_on(self, socket_number):
        return self.set_socket(socket_number, 1)

    def set_socket_off(self, socket_number):
        return self.set_socket(socket_number, 0)

    def close(self):
        """Close the serial connection."""
        with self.lock:  # Ensure thread-safe access to the serial port while closing
            try:
                if self.serial:
                    self.serial.close()
            except Exception as e:
                print(f"ERROR while closing serial: {e}")



if __name__ == "__main__":
    controller = PowerSocketsController(port=config.UART_SW_PORT, baudrate=config.UART_SW_BAUD)
    print("Connected:", controller.serial)
    if controller.serial:
        try:
            print("Current State:", controller.get_state())

            print("Turning ON socket 0...")
            print(controller.set_socket_on(0))

            print("Turning ON socket 1...")
            print(controller.set_socket_on(1))

            print("Turning OFF socket 1...")
            print(controller.set_socket_off(1))

            print("Turning OFF socket 0...")
            print(controller.set_socket_off(0))

            print("Reinit:")
            print(controller.reinit())

        finally:
            controller.close()
