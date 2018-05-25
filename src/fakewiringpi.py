from math import sin
import time

def wiringPiSetup() -> None:
    pass

def pinMode(pin: int, mode: int) -> None:
    pass

def digitalRead(pin: int) -> int:
    if int(time.clock() % 10) < 5:
        return 1
    else:
        return 0

def digitalWrite(pin: int, value: int) -> None:
    pass
    
def analogRead(pin: int) -> int:
    return int(512 + 128*sin(time.clock()))
