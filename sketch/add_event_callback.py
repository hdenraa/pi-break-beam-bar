import RPi.GPIO as GPIO
import queue
q = queue.Queue()
BEAM_PINS = [18, # Start
             27,
             22,
             23,
             24]

GPIO.setmode(GPIO.BCM)

def action(c):
    print(c)


def action2(c):
    q.put(action3)

def action3():
    print("ACTION 3")

if __name__ == "__main__":
    for p in BEAM_PINS:
        GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(p, GPIO.FALLING, action2, 500)
    import signal
    while True:
        a = q.get()
        print("Exec a")
        a()
