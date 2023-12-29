# Import Python System Libraries
import time
# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import RFM9x
import adafruit_rfm9x

# Button A
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP

# Button B
btnB = DigitalInOut(board.D6)
btnB.direction = Direction.INPUT
btnB.pull = Pull.UP

# Button C
btnC = DigitalInOut(board.D12)
btnC.direction = Direction.INPUT
btnC.pull = Pull.UP

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)


# Configure LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0)
#classadafruit_rfm9x.RFM9x(spi: SPI, cs: DigitalInOut, reset: DigitalInOut, frequency: int, *, preamble_length: int = 8, high_power: bool = True (Default is True), baudrate: int = 5000000, agc: bool = False, crc: bool = True)
rfm9x.tx_power = 23
#The transmit power in dBm. Can be set to a value from 5 to 23 for high power devices (RFM95/96/97/98, high_power=True) or -1 to 14 for low power devices. Only integer power levels are actually set (i.e. 12.5 will result in a value of 12 dBm). The actual maximum setting for high_power=True is 20dBm but for values > 20 the PA_BOOST will be enabled resulting in an additional gain of 3dBm. The actual setting is reduced by 3dBm. The reported value will reflect the reduced setting.

recv_prev_packet = None
sent_prev_packet = None

# Set initial display.
display.fill(0)
display.text('RX: ', 0, 0, 1)
display.text(recv_prev_packet, 25, 0, 1)
display.text('TX: ', 0, 10, 1)
display.text(sent_prev_packet, 25, 10, 1)
display.show()

while True:
    # check for packet rx
    packet = None
    packet = rfm9x.receive()
    if not packet is None:
        # Display the packet text and rssi
        display.fill(0)
        recv_prev_packet = str(packet, "ascii")
        display.text('RX: ', 0, 0, 1)
        display.text(recv_prev_packet, 25, 0, 1)
        display.text('TX: ', 0, 0, 1)
        display.text(sent_prev_packet, 25, 0, 1)

    if not btnA.value:
        # Send Button A
        display.fill(0)
        button_a_data = bytes("Button A!","ascii")
        rfm9x.send(button_a_data)
        display.text('Sent Button A!', 25, 10, 1)
    elif not btnB.value:
        # Send Button B
        display.fill(0)
        button_b_data = bytes("Button B!","ascii")
        rfm9x.send(button_b_data)
        display.text('Sent Button B!', 25, 15, 1)
    elif not btnC.value:
        # Send Button C
        display.fill(0)
        button_c_data = bytes("Button C!","ascii")
        rfm9x.send(button_c_data)
        display.text('Sent Button C!', 25, 15, 1)


    display.show()
    time.sleep(0.1)
