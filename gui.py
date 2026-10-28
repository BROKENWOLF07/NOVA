
import tkinter as tk
import threading
import queue
import math
import time
import webbrowser
from urllib.parse import quote_plus
from datetime import datetime

from speech import speak, listen

try:
    from commands import run_command
except Exception as exc:
    print("[NOVA] Could not load commands.py:", exc)
    run_command = None

try:
    import psutil
except ImportError:
    psutil = None


# ---------------------------------------------------------
# NOVA interface theme
# ---------------------------------------------------------

BG = "#070B12"
PANEL = "#0C1320"
CYAN = "#69E6FF"
WHITE = "#EAF8FF"
MUTED = "#7B91A8"
GREEN = "#72F5C8"
ORANGE = "#FFC477"
RED = "#FF7585"
FONT = "Segoe UI"


class NovaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NOVA | Personal Intelligence")
        self.root.geometry("1120x700")
        self.root.minsize(900, 620)
        self.root.configure(bg=BG)

        self.closing = False
        self.voice_enabled = False
        self.active_mode = False
        self.busy = False
        self.phase = 0.0
        self.animation_state = "standby"
        self.activation_started = 0.0
        self.activation_duration = 3.0

        self.events = queue.Queue()
        self.command_lock = threading.Lock()

        self._build_ui()
        self._clock()
        self._animate()
        self._poll_events()

        self.root.protocol("WM_DELETE_WINDOW", self.close)

        # Start voice mode after the window has appeared.
        self.root.after(1000, self.start_voice)

    # -----------------------------------------------------
    # USER INTERFACE
    # -----------------------------------------------------

    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=28, pady=(18, 0))

        tk.Label(
            header,
            text="N O V A",
            bg=BG,
            fg=WHITE,
            font=(FONT, 22, "bold")
        ).pack(side="left")

        self.clock_label = tk.Label(
            header,
            text="--:--:--",
            bg=BG,
            fg=MUTED,
            font=(FONT, 11)
        )
        self.clock_label.pack(side="right")

        tk.Label(
            self.root,
            text="PERSONAL INTELLIGENCE  /  VOICE INTERFACE",
            bg=BG,
            fg=MUTED,
            font=(FONT, 9)
        ).pack(anchor="w", padx=31, pady=(4, 10))

        content = tk.Frame(self.root, bg=BG)
        content.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        left = tk.Frame(content, bg=BG)
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(
            content,
            bg=PANEL,
            highlightthickness=1,
            highlightbackground="#202D3B",
            width=285
        )
        right.pack(side="right", fill="y", padx=(14, 0))
        right.pack_propagate(False)

        tk.Label(
            right,
            text="LIVE ACTIVITY",
            bg=PANEL,
            fg=WHITE,
            font=(FONT, 11, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 3))

        tk.Label(
            right,
            text="COMMANDS  /  RESPONSES",
            bg=PANEL,
            fg=MUTED,
            font=(FONT, 8, "bold")
        ).pack(anchor="w", padx=15, pady=(0, 10))

        tk.Frame(right, bg="#263646", height=1).pack(
            fill="x", padx=14, pady=(0, 8)
        )

        log_frame = tk.Frame(right, bg=PANEL)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        self.log_text = tk.Text(
            log_frame,
            bg=PANEL,
            fg=WHITE,
            insertbackground=CYAN,
            relief="flat",
            wrap="word",
            font=(FONT, 9),
            padx=4,
            pady=4,
            spacing1=3,
            spacing3=7,
            state="disabled",
            borderwidth=0
        )
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(
            log_frame,
            command=self.log_text.yview,
            bg=PANEL,
            troughcolor=BG,
            relief="flat",
            width=8
        )
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.tag_configure("time", foreground="#6D879C")
        self.log_text.tag_configure(
            "user", foreground=CYAN, font=(FONT, 9, "bold")
        )
        self.log_text.tag_configure(
            "nova", foreground=GREEN, font=(FONT, 9, "bold")
        )
        self.log_text.tag_configure(
            "error", foreground=RED, font=(FONT, 9, "bold")
        )
        self.log_text.tag_configure("detail", foreground="#B5C6D5")

        self._append_log(
            "NOVA",
            "Activity panel initialized.",
            "nova"
        )

        # Animated HUD.
        self.orb = tk.Canvas(
            left,
            bg=BG,
            highlightthickness=0,
            height=300
        )
        self.orb.pack(fill="both", expand=True, padx=4)
        self.orb.bind("<Configure>", lambda _event: self._draw_orb())

        self.status = tk.Label(
            left,
            text="INITIALIZING",
            bg=BG,
            fg=CYAN,
            font=(FONT, 13, "bold")
        )
        self.status.pack(pady=(0, 4))

        self.hint = tk.Label(
            left,
            text='Say "Nova" to activate',
            bg=BG,
            fg=MUTED,
            font=(FONT, 10)
        )
        self.hint.pack()

        self.activity = tk.Label(
            left,
            text="NOVA CORE  /  STANDBY",
            bg=BG,
            fg="#456176",
            font=(FONT, 8)
        )
        self.activity.pack(pady=(7, 12))

        bottom = tk.Frame(left, bg=PANEL)
        bottom.pack(fill="x", padx=4, pady=(0, 10))

        self.entry = tk.Entry(
            bottom,
            bg=PANEL,
            fg=WHITE,
            insertbackground=CYAN,
            relief="flat",
            font=(FONT, 10)
        )
        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(12, 6),
            pady=12,
            ipady=4
        )
        self.entry.insert(0, "Type a command...")
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<Return>", self._send_typed)

        tk.Button(
            bottom,
            text="SEND",
            command=self._send_typed,
            bg="#173647",
            fg=CYAN,
            activebackground="#214B60",
            activeforeground=WHITE,
            relief="flat",
            font=(FONT, 9, "bold"),
            cursor="hand2"
        ).pack(side="right", padx=10, pady=9, ipadx=10, ipady=6)

        controls = tk.Frame(left, bg=BG)
        controls.pack(pady=(0, 4))

        self.voice_btn = tk.Button(
            controls,
            text="VOICE ON",
            command=self.toggle_voice,
            bg=BG,
            fg=CYAN,
            activebackground=BG,
            activeforeground=WHITE,
            relief="flat",
            font=(FONT, 9, "bold"),
            cursor="hand2"
        )
        self.voice_btn.pack(side="left", padx=10)

        tk.Button(
            controls,
            text="SLEEP",
            command=self.sleep_mode,
            bg=BG,
            fg=ORANGE,
            activebackground=BG,
            activeforeground=WHITE,
            relief="flat",
            font=(FONT, 9, "bold"),
            cursor="hand2"
        ).pack(side="left", padx=10)

        tk.Button(
            controls,
            text="EXIT",
            command=self.close,
            bg=BG,
            fg=RED,
            activebackground=BG,
            activeforeground=WHITE,
            relief="flat",
            font=(FONT, 9, "bold"),
            cursor="hand2"
        ).pack(side="left", padx=10)

    # -----------------------------------------------------
    # ACTIVITY LOG
    # -----------------------------------------------------

    def _append_log(self, speaker, message, tag="detail"):
        if self.closing:
            return

        stamp = datetime.now().strftime("%H:%M:%S")

        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{stamp}] ", "time")
        self.log_text.insert("end", f"{speaker}: ", tag)
        self.log_text.insert("end", f"{str(message).strip()}\n", "detail")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _clear_placeholder(self, _event=None):
        if self.entry.get() == "Type a command...":
            self.entry.delete(0, "end")

    def _clock(self):
        if self.closing:
            return

        self.clock_label.config(
            text=datetime.now().strftime("%a  %H:%M:%S")
        )
        self.root.after(1000, self._clock)

    def _set_status(self, title, hint=None, color=CYAN):
        self.status.config(text=title, fg=color)
        if hint:
            self.hint.config(text=hint)

    # -----------------------------------------------------
    # HUD ANIMATION
    # -----------------------------------------------------

    def _draw_orb(self):
        if not hasattr(self, "orb") or self.closing:
            return

        c = self.orb
        c.delete("all")

        w = max(c.winfo_width(), 300)
        h = max(c.winfo_height(), 250)
        x, y = w / 2, h / 2

        r = min(70, w * 0.13, h * 0.23)
        activating = self.animation_state == "activating"
        active = self.active_mode or self.busy
        progress = 1.0

        if activating:
            progress = min(
                1.0,
                (time.monotonic() - self.activation_started)
                / self.activation_duration
            )

        red = "#FF243D"
        pale = "#DDE4E8"

        for gx in range(0, w, 28):
            c.create_line(gx, 0, gx, h, fill="#10141A")
        for gy in range(0, h, 28):
            c.create_line(0, gy, w, gy, fill="#10141A")

        c.create_text(
            20, 18,
            anchor="nw",
            text="NOVA / SYSTEM INTERFACE",
            fill="#6C727B",
            font=(FONT, 8, "bold")
        )

        mode = "BOOT SEQUENCE" if activating else (
            "ACTIVE" if active else "STANDBY"
        )
        c.create_text(
            w - 20, 18,
            anchor="ne",
            text=mode,
            fill=red if activating or active else "#59616B",
            font=(FONT, 8, "bold")
        )

        # Rotating geometric frame.
        spin = self.phase * (1.1 if activating else 0.3)
        diamond_r = r + 63
        points = []

        for i in range(4):
            a = math.pi / 4 + i * math.pi / 2 + spin * 0.2
            points.extend([
                x + math.cos(a) * diamond_r,
                y + math.sin(a) * diamond_r
            ])

        c.create_polygon(
            *points,
            outline="#57232C" if activating else "#252A31",
            fill="",
            width=1
        )

        # Concentric segmented rings.
        for i, rr in enumerate((r + 8, r + 20, r + 32, r + 44, r + 55)):
            start = (self.phase * (18 + i * 7) + i * 51) % 360
            c.create_arc(
                x - rr, y - rr, x + rr, y + rr,
                start=start,
                extent=250 if i % 2 else 300,
                style="arc",
                outline=red if activating and i % 2 == 0 else "#343941",
                width=2 if i in (0, 2) else 1
            )

        # Central hexagonal core.
        hex_r = r * (0.72 + 0.04 * math.sin(self.phase * 2))
        hex_points = []

        for i in range(6):
            a = math.pi / 3 * i + self.phase * 0.1
            hex_points.extend([
                x + math.cos(a) * hex_r,
                y + math.sin(a) * hex_r
            ])

        c.create_polygon(
            *hex_points,
            fill="#130B10" if activating else "#101820",
            outline=red if activating else "#7E8790",
            width=2
        )

        inner_r = hex_r * 0.45
        triangle = []

        for i in range(3):
            a = -math.pi / 2 + i * 2 * math.pi / 3
            triangle.extend([
                x + math.cos(a) * inner_r,
                y + math.sin(a) * inner_r
            ])

        c.create_polygon(
            *triangle,
            outline=pale if activating else red,
            fill="",
            width=2
        )

        c.create_oval(
            x - 6, y - 6, x + 6, y + 6,
            fill=red if activating or active else "#78818A",
            outline=""
        )

        # Boot progress bar.
        bar_w = min(260, w * 0.55)
        bx1, by1 = x - bar_w / 2, y + r + 75
        bx2, by2 = x + bar_w / 2, by1 + 15

        c.create_rectangle(
            bx1, by1, bx2, by2,
            outline="#70757C"
        )

        fill_amount = (
            progress if activating
            else (1.0 if active else 0.1)
        )
        fill_end = min(bx1 + bar_w * fill_amount, bx2 - 2)

        if fill_end > bx1 + 2:
            c.create_rectangle(
                bx1 + 2, by1 + 2, fill_end, by2 - 2,
                fill=pale if activating else (red if active else "#4A2029"),
                outline=""
            )

        if activating:
            label = (
                "INITIALIZING NEURAL CORE"
                if progress < 0.35 else
                "CALIBRATING SYSTEMS"
                if progress < 0.70 else
                "ESTABLISHING CONNECTION"
            )
            c.create_text(
                x, by2 + 20,
                text=label,
                fill=red,
                font=(FONT, 9, "bold")
            )
            c.create_text(
                x, by2 + 38,
                text=f"{int(progress * 100):03d}%",
                fill=pale,
                font=(FONT, 8)
            )
        else:
            label = (
                "SYSTEMS ONLINE / AWAITING COMMAND"
                if active else 'SAY "NOVA" TO INITIALIZE'
            )
            c.create_text(
                x, by2 + 23,
                text=label,
                fill=red if active else "#747B84",
                font=(FONT, 9, "bold")
            )

        # Small technical ticks.
        for i in range(48):
            a = i * math.pi / 24 + self.phase * 0.08
            r1 = r + 60
            r2 = r1 + (7 if i % 4 == 0 else 3)

            c.create_line(
                x + math.cos(a) * r1,
                y + math.sin(a) * r1,
                x + math.cos(a) * r2,
                y + math.sin(a) * r2,
                fill="#87303A" if activating and i % 4 == 0 else "#3A3E45"
            )

    def _animate(self):
        if self.closing:
            return

        self.phase += (
            0.09 if self.animation_state == "activating"
            else 0.06 if self.voice_enabled or self.busy
            else 0.025
        )

        if (
            self.animation_state == "activating"
            and time.monotonic() - self.activation_started
            >= self.activation_duration
        ):
            self.animation_state = "active"
            self.events.put((
                "status",
                "SYSTEMS ONLINE",
                "Speak your command",
                RED
            ))
            self.events.put(("activity", "NOVA CORE / ACTIVE SESSION"))

            greeting = self.get_greeting()
            self.events.put(("log", "NOVA", greeting, GREEN))
            threading.Thread(
                target=self._say,
                args=(greeting,),
                daemon=True
            ).start()

        elif not self.active_mode and self.animation_state != "activating":
            self.animation_state = "standby"

        self._draw_orb()
        self.root.after(40, self._animate)

    def get_greeting(self):
        hour = datetime.now().hour

        if 5 <= hour < 12:
            greeting = "Good morning"
        elif 12 <= hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        return (
            f"{greeting,} sir. NOVA systems are online. "
            "How may I assist you?"
        ).replace("('", "").replace("',)", "")

    # -----------------------------------------------------
    # VOICE CONTROL
    # -----------------------------------------------------

    def start_voice(self):
        if self.closing or self.voice_enabled:
            return

        self.voice_enabled = True
        self.active_mode = False

        self.voice_btn.config(text="VOICE ON", fg=GREEN)
        self._set_status(
            "WAKE-WORD MODE",
            'Say "Nova" to activate',
            CYAN
        )
        self.activity.config(text="MICROPHONE / WAKE-WORD MODE")

        threading.Thread(
            target=self._voice_loop,
            daemon=True
        ).start()

    def toggle_voice(self):
        if self.voice_enabled:
            self.voice_enabled = False
            self.active_mode = False
            self.animation_state = "standby"

            self.voice_btn.config(text="VOICE OFF", fg=ORANGE)
            self.events.put((
                "status", "VOICE PAUSED",
                "Press VOICE OFF to resume", ORANGE
            ))
            self.events.put(("activity", "MICROPHONE / PAUSED"))
        else:
            self.start_voice()

    def sleep_mode(self):
        self.active_mode = False
        self.animation_state = "standby"

        self.events.put((
            "status", "STANDBY",
            'Say "Nova" to activate', CYAN
        ))
        self.events.put(("activity", "NOVA CORE / WAKE-WORD MODE"))

    def _voice_loop(self):
        while self.voice_enabled and not self.closing:
            try:
                if self.busy:
                    time.sleep(0.15)
                    continue

                if not self.active_mode:
                    # Wake-word mode: listen for Nova.
                    text = listen(timeout=3, phrase_time_limit=7)

                    if not text:
                        continue

                    text = str(text).strip()
                    lower = text.lower()

                    if "nova" in lower:
                        self.active_mode = True
                        self.animation_state = "activating"
                        self.activation_started = time.monotonic()

                        self.events.put((
                            "status", "INITIALIZING NOVA",
                            "Boot sequence in progress", RED
                        ))
                        self.events.put((
                            "activity", "NOVA CORE / INITIALIZATION"
                        ))

                        # If the user said "Nova, open YouTube",
                        # preserve the command after the wake word.
                        command_after_wake = lower.split("nova", 1)[1].strip()
                        command_after_wake = command_after_wake.lstrip(
                            " ,.!?:;"
                        )

                        if command_after_wake:
                            self.events.put((
                                "pending_command", command_after_wake
                            ))

                    continue

                # Do not listen while the boot animation is running.
                if self.animation_state == "activating":
                    time.sleep(0.12)
                    continue

                # Process a command included with the wake word.
                pending = None
                try:
                    pending = self.pending_command
                    self.pending_command = None
                except AttributeError:
                    pass

                if pending:
                    command = pending
                else:
                    # Longer time limits for complete spoken commands.
                    command = listen(timeout=8, phrase_time_limit=18)

                if not command:
                    continue

                command = str(command).strip()
                low = command.lower()

                if not command:
                    continue

                if any(phrase in low for phrase in (
                    "go to sleep",
                    "sleep mode",
                    "stop listening",
                    "enter standby",
                    "standby mode",
                    "bye nova",
                    "goodbye nova"
                )):
                    self.events.put(("log", "YOU", command, CYAN))
                    self.active_mode = False
                    self.animation_state = "standby"

                    self.events.put((
                        "status", "STANDBY",
                        'Say "Nova" to activate', CYAN
                    ))
                    self.events.put((
                        "activity", "NOVA CORE / WAKE-WORD MODE"
                    ))

                    self._say("Standing by, sir.")
                    continue

                self.events.put(("log", "YOU", command, CYAN))
                self.events.put((
                    "status", "PROCESSING",
                    "Executing your command", GREEN
                ))
                self.events.put(("activity", "COMMAND / EXECUTING"))

                self._execute(command, voice=True)

            except Exception as exc:
                self.events.put((
                    "log", "Voice error", str(exc), RED
                ))
                time.sleep(0.5)

    def _say(self, text):
        if not text:
            return

        try:
            speak(str(text))
        except Exception as exc:
            self.events.put((
                "log", "Speech output error", str(exc), RED
            ))

    # -----------------------------------------------------
    # COMMAND INPUT AND PROCESSING
    # -----------------------------------------------------

    def _send_typed(self, _event=None):
        command = self.entry.get().strip()

        if not command or command == "Type a command...":
            return

        self.entry.delete(0, "end")
        self.events.put(("log", "YOU", command, CYAN))

        threading.Thread(
            target=self._execute,
            args=(command, False),
            daemon=True
        ).start()

    def _execute(self, command, voice=False):
        # Avoid running two commands simultaneously.
        if not self.command_lock.acquire(blocking=False):
            self.events.put((
                "log", "NOVA",
                "One command is still running. Please wait, sir.",
                ORANGE
            ))
            return

        self.busy = True

        try:
            self.events.put((
                "status", "PROCESSING",
                str(command)[:55], GREEN
            ))

            low = command.lower().strip()

            if low in ("open google", "go to google"):
                webbrowser.open("https://www.google.com")
                answer = "Opening Google, sir."

            elif low in ("open youtube", "go to youtube"):
                webbrowser.open("https://www.youtube.com")
                answer = "Opening YouTube, sir."

            elif low in ("open gmail", "go to gmail"):
                webbrowser.open("https://mail.google.com")
                answer = "Opening Gmail, sir."

            elif low.startswith(("search for ", "google ")):
                query = command.split(" ", 1)[1].strip()

                if low.startswith("search for "):
                    query = command[len("search for "):].strip()
                elif low.startswith("google "):
                    query = command[len("google "):].strip()

                webbrowser.open(
                    "https://www.google.com/search?q="
                    + quote_plus(query)
                )
                answer = f"Searching Google for {query}, sir."

            elif low.startswith("open website "):
                address = command[len("open website "):].strip()

                if not address.startswith(("http://", "https://")):
                    address = "https://" + address

                webbrowser.open(address)
                answer = f"Opening {address}, sir."

            elif run_command is not None:
                answer = run_command(command)

                # Use the AI fallback for commands not understood by
                # the existing command dispatcher.
                if isinstance(answer, str) and (
                    "did not understand" in answer.lower()
                    or "not understand that command" in answer.lower()
                ):
                    ai_answer = self._ask_ai(command)
                    if ai_answer:
                        answer = ai_answer

                if answer is None:
                    answer = (
                        "The command finished, but the command module "
                        "did not return a response message, sir."
                    )
            else:
                answer = (
                    "The command module could not be loaded. "
                    "Please check commands.py."
                )

            self.events.put(("log", "NOVA", str(answer), GREEN))

            # Speak responses for voice and typed commands.
            self._say(answer)

            if voice:
                self.events.put((
                    "status", "I'M LISTENING",
                    'Say your next command, or "go to sleep"', CYAN
                ))
                self.events.put((
                    "activity", "VOICE / ACTIVE SESSION"
                ))
            else:
                self.events.put((
                    "status", "READY",
                    "Command complete", CYAN
                ))
                self.events.put(("activity", "NOVA CORE / READY"))

        except Exception as exc:
            print("[NOVA COMMAND ERROR]", exc)
            self.events.put((
                "log", "Command error", str(exc), RED
            ))
            self.events.put((
                "status", "COMMAND ERROR",
                "Check the terminal for details", RED
            ))
            self._say("Sorry, sir. An error occurred while processing that command.")

        finally:
            self.busy = False
            self.command_lock.release()

    def _ask_ai(self, command):
        try:
            from brain import ask_ai
            return ask_ai(command)
        except Exception as exc:
            self.events.put((
                "log", "AI error", str(exc), RED
            ))
            return None

    # -----------------------------------------------------
    # SAFE BACKGROUND-THREAD TO GUI COMMUNICATION
    # -----------------------------------------------------

    def _poll_events(self):
        if self.closing:
            return

        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]

                if kind == "status":
                    self._set_status(event[1], event[2], event[3])

                elif kind == "activity":
                    self.activity.config(text=event[1])

                elif kind == "log":
                    if len(event) >= 4:
                        tag = (
                            "user" if event[1] == "YOU"
                            else "error" if event[3] in (RED, ORANGE)
                            else "nova"
                        )
                        self._append_log(event[1], event[2], tag)
                    else:
                        self._append_log("SYSTEM", event[1], "error")

                elif kind == "pending_command":
                    self.pending_command = event[1]

        except queue.Empty:
            pass

        self.root.after(100, self._poll_events)

    def close(self):
        self.closing = True
        self.voice_enabled = False
        self.active_mode = False

        try:
            self.root.destroy()
        except tk.TclError:
            pass


def main():
    root = tk.Tk()
    NovaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
