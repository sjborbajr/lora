#!/bin/bash
screen -X -S updater quit
screen -X -S LoRa quit
screen -dmLS updater /bin/bash /opt/lora/git/updater.sh