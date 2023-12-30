import time
import board
import busio
import digitalio
import adafruit_rfm9x

# Configure the CS (Chip Select) and RST (Reset) pins
# Adjust these pins according to your wiring
CS = digitalio.DigitalInOut(board.CE1)
RST = digitalio.DigitalInOut(board.D25)

# Initialize SPI bus
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialize RFM9x LoRa Radio
# Set the frequency to your region's standard (915.0 MHz used here for North America)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RST, 915.0)

def log_packet(packet):
    """
    Logs the received packet along with RSSI value and timestamp to a file.
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    rssi = rfm9x.rssi
    with open("lora_logs.txt", "a") as log_file:
        log_file.write(f"Time: {timestamp}, RSSI: {rssi}, Payload: {packet}\n")

print("RFM9x LoRa Receiver - Listening for packets")

while True:
    try:
        packet = rfm9x.receive()
        if packet is not None:
            packet_text = str(packet, 'ascii')
            print(f"Received: {packet_text}")
            log_packet(packet_text)
        time.sleep(0.1)
    except KeyboardInterrupt:
        print("Program terminated by user")
        break
