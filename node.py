
from machine import Pin, SoftI2C
import ssd1306
from time import sleep
import requests

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    dataFromBS = conn.recv(1024)
    dataFromBS = str(dataFromBS)
    
    # Display message on the OLED
    displayMessage(dataFromBS)
    ack.value(0)

    if(getStatus() == "ACK"):
        r = requests.get(BROADCAST_SERVER_URL+"/ack?status=true")
        print(r.content)

    response = getStatus()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()


def getStatus():
    if ack.value() == 1:
        ack_state="ACK"
    else:
        ack_state="WAIT"
    return ack_state

def displayMessage(content):
    try:
        i2c = SoftI2C(scl=Pin(5), sda=Pin(4))
        oled_width = 128
        oled_height = 64
        oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
        oled.text('{content}', 0, 0)
        oled.show()
        return "Successfully Displayed"
    except Exception as e:
        print(e)
        return "OLED Failure"