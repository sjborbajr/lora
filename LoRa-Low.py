import time
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import adafruit_ssd1306
import json
import atexit

import adafruit_rfm9x
import sys
import select
import termios
import tty

#Global Variables
SETTINGS_FILE = "data/settings.json"
recv_packet = "none"
sent_packet = "none"


def load_settings():
  with open(SETTINGS_FILE, 'r') as f:
    settings = json.load(f)
  return settings

def set_raw_mode(fd):
  # Save the terminal settings, and register an exit to reset back
  original_settings = termios.tcgetattr(fd)
  atexit.register(lambda: termios.tcsetattr(fd, termios.TCSADRAIN, original_settings))
  tty.setraw(fd)

def UpdateDisplay():
  display.fill(0)
  display.text(f'RX: {recv_packet}', 0, 0, 1)
  display.text(f'TX: {sent_packet}', 0, 12, 1)
  if rfm9x.last_snr:
    display.text("SNR "+str(rfm9x.last_snr)+" RSSI "+str(rfm9x.last_rssi), 0, 23, 1)
  else:
    display.text("-=-=-=-=-=-=-=-=-=-=-=-=-=-", 0, 24, 1)
  display.show()

def send_packet(key):
  global sent_packet
  sent_packet = 'Sent Button ' + key + '!'
  rfm9x.send(bytes(sent_packet, "ascii"))
  log("TX: " + sent_packet)
  UpdateDisplay()

def log(text):
  print("Time: "+time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+", "+text+"\r")
  with open("logs/LoRa-Low-"+time.strftime("%Y%m%d", time.localtime())+".log", "a") as log_file:
    log_file.write("Time: "+time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+", "+text+"\r\n")

def save_raw(packet,tag = ""):
  filename="raw_packets/"+tag+time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+"-snr-"+str(rfm9x.last_snr)+"-rssi-"+str(rfm9x.last_rssi)
  with open(filename+".pkt", "wb") as pkt_file:
    pkt_file.write(packet)

settings = load_settings()

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
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, settings.get("frequency_mhz", 915.0))
rfm9x.tx_power = settings.get("tx_power", 23)
rfm9x.spreading_factor = settings.get("spreading_factor", 7)
rfm9x.encryption_key = bytes.fromhex(settings.get("encryption_key","0123456789ABCDEF0123456789ABCDEF"))

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)

log("Program Started")
atexit.register(log,"Program Stopped")
set_raw_mode(sys.stdin.fileno())
UpdateDisplay()
while True:
  # check for packet rx
  packet = None
  packet = rfm9x.receive()
  if packet is not None:
    try:
      recv_packet = str(packet, "ascii")
      save_raw(packet,"ASCII-")
      log("RX: '"+recv_packet+"' snr: "+str(rfm9x.last_snr)+" rssi: "+str(rfm9x.last_rssi))
      if not recv_packet[:5] == "ACK: ":
        UpdateDisplay()
        #The other side isn't seeing the ACK with too shot of a delay here
        time.sleep(0.6)
        temp = "ACK: snr: "+str(rfm9x.last_snr)+" rssi: "+str(rfm9x.last_rssi)
        rfm9x.send(bytes(temp, "ascii"))
    except UnicodeDecodeError as e:
      save_raw(packet,"ERR-")
      print(f"Error decoding packet: {e}")
      log(f"RSSI: {rfm9x.last_rssi}, SNR: {rfm9x.last_snr}, Faild to Decode Packet")

  #Check for button presses
  if not btnA.value:
    send_packet("btnA")
  elif not btnB.value:
    send_packet("btnB")
  elif not btnC.value:
    send_packet("btnC")

  #check for script console input and xmit
  while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
    char = sys.stdin.read(1)
    if char == 'x':
      exit()
    else:
      send_packet(char)

  time.sleep(0.1)
