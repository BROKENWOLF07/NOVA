import psutil

battery = psutil.sensors_battery()

if battery:
    print(battery.percent)
else:
    print("No battery detected")
    