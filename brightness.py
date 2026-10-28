import screen_brightness_control as sbc


def brightness_up():
    try:
        current = sbc.get_brightness()[0]
        new = min(current + 10, 100)

        sbc.set_brightness(new)

        return f"Brightness increased to {new} percent sir"

    except Exception as e:
        return f"Brightness error: {e}"


def brightness_down():
    try:
        current = sbc.get_brightness()[0]
        new = max(current - 10, 0)

        sbc.set_brightness(new)

        return f"Brightness decreased to {new} percent sir"

    except Exception as e:
        return f"Brightness error: {e}"


def set_brightness(percent):
    try:
        percent = int(percent)

        if percent < 0:
            percent = 0

        if percent > 100:
            percent = 100

        sbc.set_brightness(percent)

        return f"Brightness set to {percent} percent sir"

    except Exception as e:
        return f"Brightness error: {e}"


def get_brightness():
    try:
        current = sbc.get_brightness()[0]

        return f"Current brightness is {current} percent sir"

    except Exception as e:
        return f"Brightness error: {e}"