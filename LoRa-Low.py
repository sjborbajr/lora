import time
import busio
from digitalio import DigitalInOut, Direction, Pull
import sys
import select
import board
import adafruit_ssd1306
import adafruit_rfm9x
import termios
import tty
import atexit

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

recv_packet = "none"
send_packet = "none"

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)

def set_raw_mode(fd):
  # Save the terminal settings, and register an exit to reset back
  original_settings = termios.tcgetattr(fd)
  atexit.register(lambda: termios.tcsetattr(fd, termios.TCSADRAIN, original_settings))
  tty.setraw(fd)

def UpdateDisplay():
  display.fill(0)
  display.text('RX: '+recv_packet, 0, 0, 1)
  display.text('TX: '+send_packet, 0, 10, 1)
  if rfm9x.last_snr:
    display.text("SNR"+str(rfm9x.last_snr)+" RSSI"+str(rfm9x.last_rssi), 0, 22, 1)
  else:
    display.text("-=-=-=-=-=-=-=-=-=-=-=-=-=-=", 0, 22, 1)
  display.show()

def send_key(key):
  global send_packet
  send_packet = 'Sent Button ' + key + '!'
  rfm9x.send(bytes(send_packet, "ascii"))
  log("TX: " + send_packet)
  UpdateDisplay()

def log(text):
  print("Time: "+time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+", "+text+"\r")
  with open("lora.log", "a") as log_file:
    log_file.write("Time: "+time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+", "+text+"\r\n")

def save_raw(packet,tag = ""):
  filename="raw_packets/"+tag+time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())+"-snr-"+str(rfm9x.last_snr)+"-rssi-"+str(rfm9x.last_rssi)+".pkt"
  with open(filename, "wb") as pkt_file:
    pkt_file.write(packet)

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
      log(f"RSSI: {rfm9x.last_snr}, SNR: {rfm9x.last_snr}, Faild to Decode Packet")

  #Check for button presses
  if not btnA.value:
    send_key("btnA")
  elif not btnB.value:
    send_key("btnB")
  elif not btnC.value:
    send_key("btnC")

  #check for script console input
  while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
    char = sys.stdin.read(1)
    if char == 'x':
      exit()
    else:
      send_key(char)

  #min looptime
  time.sleep(0.1)
