import time
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import json
import adafruit_ssd1306
import atexit

import threading
import subprocess
from adafruit_tinylora.adafruit_tinylora import TTN, TinyLoRa

#Global Variables
SETTINGS_FILE = "data/settings.json"
line1 = "LoRa WAN starting"
line2 = "¯\_(ツ)_/¯"

def load_settings():
  with open(SETTINGS_FILE, 'r') as f:
    settings = json.load(f)
  return settings

def send_pi_data_periodic(message):
  threading.Timer(interval, send_pi_data_periodic).start()
  if not message == 'start':
    line1 = "Periodic data send - "+time.strftime("%H-%M-%S", time.localtime())
    log(line1)
  send_pi_data()
  UpdateDisplay()

def send_pi_data():
  data = getCPU
  line2 = 'CPU:'+str(data)
  log(line2)
  data_pkt = bytearray(2)
  # Encode float as int
  data = int(data * 100)
  # Encode payload as bytes
  data_pkt[0] = (data >> 8) & 0xff
  data_pkt[1] = data & 0xff
  # Send data packet
  lora.send_data(data_pkt, len(data_pkt), lora.frame_counter)
  lora.frame_counter += 1

def UpdateDisplay():
  display.fill(0)
  display.text(f'{line1}', 0, 0, 1)
  display.text(f'{line2}', 0, 12, 1)
  display.text("-=-=-=-=-=-=-=-=-=-=-=-=-=-", 0, 24, 1)
  display.show()

def log(text):
  print("Time: "+time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+", "+text+"\r")
  with open("logs/LoRa-WAN-"+time.strftime("%Y%m%d", time.localtime())+".log", "a") as log_file:
    log_file.write("Time: "+time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+", "+text+"\r\n")

def getCPU():
  cmd = "top -bn1 | grep load | awk '{printf \"%.1f\", $(NF-2)}'"
  CPU = subprocess.check_output(cmd, shell = True )
  CPU = float(CPU)
  return CPU

settings = load_settings()
devaddr = bytearray(settings.get("devaddr", "00000000"))
nwkey = bytearray(settings.get("nwkey", "00000000000000000000000000000000"))
app = bytearray(settings.get("appkey", "00000000000000000000000000000000"))
interval = settings.get("interval",5.0)

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

# TinyLoRa Configuration
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = DigitalInOut(board.CE1)
irq = DigitalInOut(board.D22)
rst = DigitalInOut(board.D25)

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)

# Initialize ThingsNetwork configuration
ttn_config = TTN(devaddr, nwkey, app, country='US')
# Initialize lora object
lora = TinyLoRa(spi, cs, irq, rst, ttn_config)

log("Program Started")
atexit.register(log,"Program Stopped")

#start sending data
line1 = "Started periodic data sending..."
log(line1)
send_pi_data_periodic("start")

while True:
  packet = None

  #Check for button presses
  if not btnA.value:
    line1 = "btnA"
    UpdateDisplay()
  elif not btnB.value:
    line1 = "btnB"
    UpdateDisplay()
  elif not btnC.value:
    line1 = "btnC"
    UpdateDisplay()

    time.sleep(.1)
