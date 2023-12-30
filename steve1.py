import time
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import adafruit_ssd1306
import adafruit_rfm9x
import keyboard

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

# Configure LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0)
rfm9x.tx_power = 23

recv_prev_packet = "none"
recv_packet = "none"
send_packet = "none"

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)

def UpdateDisplay():
  global recv_prev_packet
  display.fill(0)
  display.text('RX: ', 0, 0, 1)
  display.text(recv_prev_packet, 25, 0, 1)
  display.text('TX: ', 0, 10, 1)
  display.text(send_packet, 25, 10, 1)
  display.show()

def send_key(key,event):
  global send_packet
  send_packet = 'Sent Button ' + key + '!'
  rfm9x.send(bytes(send_packet, "ascii"))
  UpdateDisplay()
  print("TX: " + send_packet)

keyboard.on_press_key('a', lambda e: send_key("A", e))
keyboard.on_press_key('b', lambda e: send_key("B", e))
keyboard.on_press_key('c', lambda e: send_key("C", e))
UpdateDisplay()
while True:
  # check for packet rx
  packet = None
  packet = rfm9x.receive()
  if not packet is None:
    # Display the packet text and rssi
    recv_packet = str(packet, "ascii")
    if recv_packet[:5] == "ACK: ":
      print(recv_packet)
    else:
      print("RX: "+recv_packet)
      recv_prev_packet = recv_packet
      UpdateDisplay()
      time.sleep(0.75)
      temp = "ACK: snr: "+str(rfm9x.last_snr)+" rssi: "+str(rfm9x.last_rssi)
      rfm9x.send(bytes(temp, "ascii"))

  if not btnA.value:
    send_key("A","")
  elif not btnB.value:
    send_key("B","")
  elif not btnC.value:
    send_key("C","")

  time.sleep(0.1)
