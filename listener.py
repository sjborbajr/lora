import time
from SX127x.LoRa import *
from SX127x.board_config import BOARD

# Initialize the board
BOARD.setup()
# Define a class for the LoRa radio
class LoRaReceiver(LoRa):
    def __init__(self, verbose=False):
        super(LoRaReceiver, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)

    def on_rx_done(self):
        print("Packet received")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        snr = self.get_pkt_snr_value()
        rssi = self.get_pkt_rssi_value()
        self.log_packet(payload, timestamp, snr, rssi)
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

    def log_packet(self, payload, timestamp, snr, rssi):
        with open("lora_logs.txt", "a") as log_file:
            log_file.write(f"Time: {timestamp}, SNR: {snr}, RSSI: {rssi}, Payload: {payload}\n")

    def start(self):
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

# Create a LoRa receiver object
lora = LoRaReceiver(verbose=False)

# Set frequency, spreading factor and other parameters
lora.set_freq(915.0)
lora.set_spreading_factor(7)
lora.set_bw(125)

# Start the receiver
lora.start()

try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    BOARD.teardown()
