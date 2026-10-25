
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Line, Ellipse, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
import os, shutil, math, webbrowser, random
from datetime import datetime

try:
    from plyer import tts, flash, battery
    HAS_PLYER = True
except:
    HAS_PLYER = False

Window.clearcolor = get_color_from_hex("#0A0E14")

class ParticleOrb(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angle = 0
        self.particles = []
        for _ in range(60):
            self.particles.append({
                'r': random.uniform(0.3, 1.0),
                'a': random.uniform(0, 360),
                's': random.uniform(0.5, 1.5),
                'size': random.uniform(2, 5)
            })
        Clock.schedule_interval(self.update, 1/30)
        self.bind(pos=self.draw, size=self.draw)
    def draw(self, *args):
        self.canvas.clear()
        cx, cy = self.center_x, self.center_y
        base_r = min(self.width, self.height) * 0.42
        with self.canvas:
            # outer glow
            Color(0.0, 0.85, 0.85, 0.08)
            Ellipse(pos=(cx-base_r*1.2, cy-base_r*1.2), size=(base_r*2.4, base_r*2.4))
            # particles
            for p in self.particles:
                rad = base_r * p['r']
                ang = p['a'] + self.angle * p['s']
                x = cx + rad * math.cos(math.radians(ang)) * 0.8
                y = cy + rad * math.sin(math.radians(ang)) * 0.6
                # cyan dots
                alpha = 0.6 + 0.4*math.sin(math.radians(ang*2))
                Color(0.1, 0.8, 0.8, alpha)
                Ellipse(pos=(x-p['size']/2, y-p['size']/2), size=(p['size'], p['size']))
                # small glow
                Color(0.3, 1.0, 1.0, alpha*0.3)
                Ellipse(pos=(x-p['size'], y-p['size']), size=(p['size']*2, p['size']*2))
    def update(self, dt):
        self.angle += 0.8
        if self.angle > 360:
            self.angle -= 360
        for p in self.particles:
            p['a'] += p['s']*0.5
        self.draw()

class KanchiApp(App):
    def build(self):
        self.title = "KANCHI AI"
        root = FloatLayout()

        # TOP STATUS BAR
        top_bar = BoxLayout(size_hint=(1, 0.06), pos_hint={'x':0,'y':0.94}, spacing=4, padding=4)
        with top_bar.canvas.before:
            Color(*get_color_from_hex("#111820"))
            Rectangle(pos=top_bar.pos, size=top_bar.size)
        top_bar.bind(pos=lambda inst, v: setattr(inst.canvas.before.children[0], 'pos', v), size=lambda inst, v: setattr(inst.canvas.before.children[0], 'size', v))
        top_bar.add_widget(Label(text=f"[color=7ED6FF]{datetime.now().strftime('%I:%M %p')}[/color]", markup=True, font_size=9, size_hint=(0.18,1)))
        def chip(txt, col="#1A2A3A"):
            b = Button(text=txt, font_size=7, size_hint=(0.20,1), background_color=get_color_from_hex(col), background_normal='')
            with b.canvas.before:
                Color(*get_color_from_hex("#2A4A5A"))
                Line(rounded_rectangle=(b.x, b.y, b.width, b.height, 10), width=0.6)
            return b
        top_bar.add_widget(chip("◉ Screen\nVision", "#0F2A3A"))
        top_bar.add_widget(chip("♡ Face\nAuth", "#0F2A1F"))
        top_bar.add_widget(chip("⚑ Memory\n(2002)", "#2A1F0F"))
        top_bar.add_widget(Label(text="Wed", font_size=8, color=get_color_from_hex("#7ED6FF"), size_hint=(0.12,1)))
        root.add_widget(top_bar)

        # SECOND ROW - CONTROLS
        ctrl = GridLayout(cols=5, spacing=6, size_hint=(0.96, 0.10), pos_hint={'x':0.02,'y':0.83}, padding=2)
        def ctrl_btn(title, subtitle, icon=""):
            box = BoxLayout(orientation='vertical', padding=4, spacing=1)
            with box.canvas.before:
                Color(*get_color_from_hex("#161E26"))
                RoundedRectangle(pos=box.pos, size=box.size, radius=[12])
                Color(*get_color_from_hex("#2A3A4A"))
                Line(rounded_rectangle=(box.x, box.y, box.width, box.height, 12), width=0.6)
            box.bind(pos=lambda inst, v: setattr(inst.canvas.before.children[1], 'pos', v), size=lambda inst, v: setattr(inst.canvas.before.children[1], 'size', v))
            box.add_widget(Label(text=icon, font_size=10, size_hint=(1,0.3)))
            box.add_widget(Label(text=title, font_size=8, color=get_color_from_hex("#FFFFFF"), size_hint=(1,0.35)))
            box.add_widget(Label(text=subtitle, font_size=6, color=get_color_from_hex("#7A8A9A"), size_hint=(1,0.35)))
            return box
        torch_box = ctrl_btn("TORCH", "OFF", "🔦")
        vol_box = ctrl_btn("100%", "-  +", "🔊")
        batt_box = ctrl_btn("30%", "Battery\nTap status", "🔋")
        wa_box = ctrl_btn("WhatsApp", "", "💬")
        yt_box = ctrl_btn("YouTube", "", "▶️")
        # Make them clickable
        torch_box.bind(on_touch_down=lambda inst, touch: self.torch_cmd() if inst.collide_point(*touch.pos) else None)
        wa_box.bind(on_touch_down=lambda inst, touch: self.whatsapp_cmd("91", "Hi from Kanchi") if inst.collide_point(*touch.pos) else None)
        for b in [torch_box, vol_box, batt_box, wa_box, yt_box]:
            ctrl.add_widget(b)
        root.add_widget(ctrl)

        # CENTRAL ORB
        self.orb = ParticleOrb(size_hint=(0.80, 0.40), pos_hint={'x':0.10,'y':0.35})
        root.add_widget(self.orb)

        # MIC BUTTONS
        mic_row = BoxLayout(size_hint=(0.80, 0.06), pos_hint={'x':0.10,'y':0.27}, spacing=8)
        mic_btn = Button(text="● Tap mic to talk", font_size=9, size_hint=(0.6,1), background_color=get_color_from_hex("#1E2A32"), background_normal='')
        with mic_btn.canvas.before:
            Color(*get_color_from_hex("#2A3A4A"))
            Line(rounded_rectangle=(mic_btn.x, mic_btn.y, mic_btn.width, mic_btn.height, 20), width=0.8)
        mic_btn.bind(pos=lambda inst, v: setattr(inst.canvas.before.children[0], 'pos', v), size=lambda inst, v: setattr(inst.canvas.before.children[0], 'size', v))
        mic_btn.bind(on_press=self.mic_cmd)
        ready = Label(text="Ready", font_size=8, color=get_color_from_hex("#7A8A9A"), size_hint=(0.2,1))
        mic_row.add_widget(mic_btn)
        mic_row.add_widget(ready)
        root.add_widget(mic_row)

        hands = BoxLayout(size_hint=(0.70, 0.05), pos_hint={'x':0.15,'y':0.21}, spacing=4)
        hands.add_widget(Label(text="● Hands-Free:  OFF  (Tap to Enable)", font_size=8, color=get_color_from_hex("#9AAABA")))
        root.add_widget(hands)

        # APP ACCESS
        app_access = BoxLayout(size_hint=(0.96, 0.20), pos_hint={'x':0.02,'y':0.01}, orientation='vertical', spacing=4)
        # Top row
        row1 = BoxLayout(spacing=6, size_hint=(1,0.18))
        row1.add_widget(Button(text="🛡️ App Access", font_size=8, size_hint=(0.35,1), background_color=get_color_from_hex("#0A2A1A"), background_normal=''))
        row1.add_widget(Label(text="", size_hint=(0.65,1)))
        app_access.add_widget(row1)

        row2 = BoxLayout(spacing=6, size_hint=(1,0.18))
        row2.add_widget(Button(text="⚙️ Settings", font_size=8, size_hint=(0.25,1), background_color=get_color_from_hex("#1A1A1A"), background_normal=''))
        hands_free = BoxLayout(size_hint=(0.75,1), spacing=4)
        hands_free.add_widget(Label(text="Hands-Free\nOFF", font_size=7, halign='center'))
        voice_on = Button(text="🔊 Voice\nON", font_size=7, background_color=get_color_from_hex("#0A2A1A"), background_normal='')
        voice_on.bind(on_press=lambda x: self.speak("Voice is ON, Boss"))
        hands_free.add_widget(voice_on)
        row2.add_widget(hands_free)
        app_access.add_widget(row2)

        row3 = BoxLayout(spacing=6, size_hint=(1,0.18))
        row3.add_widget(Button(text="((•)) Kanchi (Female Hindi)", font_size=7, background_color=get_color_from_hex("#0F1F2F"), background_normal=''))
        row3.add_widget(Button(text="🌐 Auto (Hindi/Eng)  ✨", font_size=7, background_color=get_color_from_hex("#1A1A1A"), background_normal=''))
        app_access.add_widget(row3)

        # Input row
        input_box = BoxLayout(size_hint=(1,0.35), spacing=6, padding=2)
        with input_box.canvas.before:
            Color(*get_color_from_hex("#1A1F26"))
            RoundedRectangle(pos=input_box.pos, size=input_box.size, radius=[18])
        input_box.bind(pos=lambda inst, v: setattr(inst.canvas.before.children[0], 'pos', v), size=lambda inst, v: setattr(inst.canvas.before.children[0], 'size', v))
        self.input = TextInput(hint_text="Speak with mic above or type in Hindi / English...  call/sms/wa/organize", font_size=8, size_hint=(0.85,1), background_color=get_color_from_hex("#1A1F26"), foreground_color=get_color_from_hex("#7ED6FF"), multiline=False, cursor_color=get_color_from_hex("#00E5FF"))
        self.input.bind(on_text_validate=self.process_command)
        send_btn = Button(text="➤", font_size=14, size_hint=(0.15,1), background_color=get_color_from_hex("#0A2A3A"), background_normal='')
        send_btn.bind(on_press=self.process_command)
        input_box.add_widget(self.input)
        input_box.add_widget(send_btn)
        app_access.add_widget(input_box)

        root.add_widget(app_access)

        # Status label
        self.output = Label(text="KANCHI READY - Lock par bhi chalegi • Tap mic or type", font_size=8, color=get_color_from_hex("#7ED6FF"), size_hint=(0.96,0.03), pos_hint={'x':0.02,'y':0.74}, halign='center')
        root.add_widget(self.output)

        # Auto start lock-screen service
        Clock.schedule_once(lambda dt: self.start_background_service(), 1)
        Clock.schedule_interval(self.update_battery, 5)
        return root

    def start_background_service(self):
        try:
            from jnius import autoclass
            service = autoclass('org.kivy.android.PythonService')
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            service.start(mActivity, "KANCHI ACTIVE", "Lock screen par bhi chal rahi hai • AI Studio Ready", "", "")
            self.output.text = "Background service ON - Lock par bhi chalegi"
        except Exception as e:
            print(f"Service (PC normal): {e}")
            self.output.text = "Kanchi Ready - Lock support ON (APK me service chalega)"

    def update_battery(self, dt):
        try:
            if HAS_PLYER:
                from plyer import battery
                b = battery.status
                if b:
                    self.output.text = f"Battery {b.get('percentage','30')}% - Kanchi Active - Lock par bhi ON"
        except:
            pass

    def speak(self, text):
        self.output.text = text[:60]
        if HAS_PLYER:
            try:
                tts.speak(text)
            except:
                pass

    def mic_cmd(self, *args):
        self.speak("Haan boss, bolo kya kaam hai?")
        self.orb.angle += 20

    def torch_cmd(self, *args):
        try:
            flash.on()
            self.speak("Torch ON")
            Clock.schedule_once(lambda dt: flash.off(), 3)
        except:
            self.speak("Torch ON - Flash ready")

    def whatsapp_cmd(self, number, msg):
        clean = ''.join(filter(str.isdigit, number))
        if len(clean)==10:
            clean="91"+clean
        try:
            import urllib.parse
            url = f"https://wa.me/{clean}?text={urllib.parse.quote(msg)}"
            webbrowser.open(url)
            self.speak(f"WhatsApp opening {clean}")
        except Exception as e:
            self.speak(f"WA error {e}")

    def process_command(self, *args):
        raw = self.input.text.strip()
        txt = raw.lower()
        if not txt:
            return
        self.output.text = f"Command: {raw}"
        if txt.startswith("call "):
            num = raw.split("call ",1)[1].split()[0]
            self.call_cmd(num)
        elif txt.startswith("sms ") or txt.startswith("msg "):
            parts = raw.split(None, 2)
            if len(parts)>=3:
                self.sms_cmd(parts[1], parts[2])
        elif txt.startswith("wa ") or "whatsapp" in txt:
            parts = raw.split(None, 2)
            if len(parts)>=2:
                msg = parts[2] if len(parts)>=3 else "Hi from Kanchi"
                self.whatsapp_cmd(parts[1], msg)
        elif "organize" in txt:
            self.organize_cmd()
        elif "torch" in txt:
            self.torch_cmd()
        elif "youtube" in txt:
            webbrowser.open("https://youtube.com")
            self.speak("YouTube khol raha hu")
        else:
            self.speak(raw)
        self.input.text=""

    def call_cmd(self, number):
        self.speak(f"Calling {number}")
        try:
            from plyer import call
            call.makecall(tel=number)
        except:
            try:
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                intent = Intent(Intent.ACTION_DIAL)
                intent.setData(Uri.parse(f"tel:{number}"))
                PythonActivity.mCurrentActivity.startActivity(intent)
            except:
                webbrowser.open(f"tel:{number}")

    def sms_cmd(self, number, message):
        self.speak(f"SMS to {number}")
        try:
            from plyer import sms
            sms.send(recipient=number, message=message)
        except:
            try:
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                intent = Intent(Intent.ACTION_VIEW)
                intent.setData(Uri.parse(f"smsto:{number}"))
                intent.putExtra("sms_body", message)
                PythonActivity.mCurrentActivity.startActivity(intent)
            except Exception as e:
                self.speak(f"SMS error {e}")

    def organize_cmd(self):
        try:
            base = "/storage/emulated/0/Download/Kanchi_Photos" if os.path.exists("/storage") else os.path.join(os.getcwd(), "Kanchi_Photos")
            os.makedirs(base, exist_ok=True)
            photos = os.path.join(base, "Photos")
            os.makedirs(photos, exist_ok=True)
            moved=0
            for f in os.listdir(base):
                fp=os.path.join(base,f)
                if os.path.isfile(fp) and f.lower().endswith((".jpg",".jpeg",".png")):
                    shutil.move(fp, os.path.join(photos,f))
                    moved+=1
            self.speak(f"{moved} photos organized")
        except Exception as e:
            self.speak(f"Error {e}")

KanchiApp().run()
