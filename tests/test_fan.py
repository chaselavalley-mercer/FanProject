import fan
fan.init()
print("Type 0..100 for fan %, 'q' to quit")
try:
    while True:
        s = input("> ").strip().lower()
        if s == 'q': break
        try:
            p = int(s)
            fan.set_percent(p)
        except:
            print("Enter an integer 0..100")
finally:
    fan.stop()
