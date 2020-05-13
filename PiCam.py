from picamera import PiCamera
from time import sleep

camera = PiCamera()

bool sense = false

while(true)
    for i in range(5):
        sleep(5)
        camera.capture('/home/pi/Desktop/image%s.jpg' % i)