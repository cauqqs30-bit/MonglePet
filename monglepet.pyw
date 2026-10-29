import tkinter as tk
from tkinter import messagebox
import json, os, time, random, math
from pathlib import Path

APP_NAME = "몽글펫"
SAVE_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "MonglePet"
SAVE_FILE = SAVE_DIR / "save.json"

DEFAULT = {
    "pet_type": "강아지", "name": "몽글이", "age_seconds": 0,
    "hunger": 82.0, "happiness": 82.0, "energy": 82.0,
    "coins": 80, "xp": 0, "items": {"간식": 2, "공": 1, "쿠션": 0},
    "last_saved": time.time(), "x": 120, "y": 140, "equipped": "없음"
}
def clamp(v, lo=0, hi=100): return max(lo, min(hi, v))

class DeskPet:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("310x380+120+140")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#f7f2eb")
        self.data = self.load_data()
        self.drag = None
        self.action = "idle"
        self.action_until = 0
        self.shop_open = False
        self._build()
        self._restore_position()
        self._apply_offline_time()
        self.refresh()
        self.tick()

    def load_data(self):
        try:
            SAVE_DIR.mkdir(parents=True, exist_ok=True)
            if SAVE_FILE.exists():
                d = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
                for k, v in DEFAULT.items():
                    d.setdefault(k, v)
                return d
        except Exception:
            pass
        return DEFAULT.copy()

    def save_data(self):
        try:
            SAVE_DIR.mkdir(parents=True, exist_ok=True)
            self.data["last_saved"] = time.time()
            self.data["x"], self.data["y"] = self.root.winfo_x(), self.root.winfo_y()
            SAVE_FILE.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _apply_offline_time(self):
        elapsed = max(0, min(time.time() - float(self.data.get("last_saved", time.time())), 7*24*3600))
        hours = elapsed / 3600
        self.data["age_seconds"] += elapsed
        self.data["hunger"] = clamp(self.data["hunger"] - hours * 4.0)
        self.data["happiness"] = clamp(self.data["happiness"] - hours * 2.5)
        self.data["energy"] = clamp(self.data["energy"] - hours * 1.8)
        self.save_data()

    def _build(self):
        self.top = tk.Frame(self.root, bg="#f7f2eb", height=30)
        self.top.pack(fill="x")
        self.top.bind("<Button-1>", self.start_drag)
        self.top.bind("<B1-Motion>", self.do_drag)
        tk.Label(self.top, text="✦ 몽글펫", bg="#f7f2eb", fg="#51483e",
                 font=("맑은 고딕", 10, "bold")).pack(side="left", padx=10)
        tk.Button(self.top, text="—", command=self.minimize, bd=0, bg="#f7f2eb",
                  fg="#786b60", activebackground="#e8ded2", font=("맑은 고딕", 10),
                  width=3).pack(side="right")
        tk.Button(self.top, text="×", command=self.close, bd=0, bg="#f7f2eb",
                  fg="#786b60", activebackground="#e8ded2", font=("맑은 고딕", 10),
                  width=3).pack(side="right")
        self.top.bind("<Double-Button-1>", lambda e: self.toggle_panel())

        self.canvas = tk.Canvas(self.root, width=310, height=190, bg="#e8f1e8",
                                highlightthickness=0)
        self.canvas.pack(fill="x")
        self.canvas.bind("<Button-1>", self.pet_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)

        self.panel = tk.Frame(self.root, bg="#f7f2eb")
        self.panel.pack(fill="both", expand=True)
        name_row = tk.Frame(self.panel, bg="#f7f2eb")
        name_row.pack(fill="x", padx=12, pady=(7, 2))
        self.name_label = tk.Label(name_row, text="", bg="#f7f2eb", fg="#40372f",
                                   font=("맑은 고딕", 12, "bold"))
        self.name_label.pack(side="left")
        self.stage_label = tk.Label(name_row, text="", bg="#f7f2eb", fg="#897a6b",
                                    font=("맑은 고딕", 9))
        self.stage_label.pack(side="right")

        self.stats = {}
        for key, label in [("hunger","포만감"),("happiness","행복"),("energy","기력")]:
            row = tk.Frame(self.panel, bg="#f7f2eb")
            row.pack(fill="x", padx=12, pady=2)
            tk.Label(row, text=label, width=6, anchor="w", bg="#f7f2eb",
                     fg="#66594d", font=("맑은 고딕", 9)).pack(side="left")
            bar = tk.Canvas(row, height=10, bg="#e4dcd1", highlightthickness=0)
            bar.pack(side="left", fill="x", expand=True, padx=6)
            val = tk.Label(row, text="", width=4, bg="#f7f2eb", fg="#66594d",
                           font=("맑은 고딕", 8))
            val.pack(side="right")
            self.stats[key] = (bar, val)

        self.info = tk.Label(self.panel, text="", bg="#f7f2eb", fg="#6f6256",
                             font=("맑은 고딕", 8))
        self.info.pack(pady=(3, 2))
        buttons = tk.Frame(self.panel, bg="#f7f2eb")
        buttons.pack(fill="x", padx=10, pady=3)
        self.make_button(buttons, "🍖 밥 주기", self.feed, "#f4d5ae").pack(side="left", expand=True, fill="x", padx=2)
        self.make_button(buttons, "🎾 놀기", self.play, "#cde5d2").pack(side="left", expand=True, fill="x", padx=2)
        self.make_button(buttons, "💤 재우기", self.sleep_pet, "#d7d8f4").pack(side="left", expand=True, fill="x", padx=2)
        bottom = tk.Frame(self.panel, bg="#f7f2eb")
        bottom.pack(fill="x", padx=10, pady=(1, 8))
        self.make_button(bottom, "🛍 상점", self.open_shop, "#ead9ef").pack(side="left", expand=True, fill="x", padx=2)
        self.make_button(bottom, "🐶/🐱 친구 바꾸기", self.switch_pet, "#e8e0d6").pack(side="left", expand=True, fill="x", padx=2)

    def make_button(self, parent, text, command, color):
        return tk.Button(parent, text=text, command=command, bd=0, relief="flat",
                         bg=color, fg="#4e443b", activebackground="#d6c9bb",
                         font=("맑은 고딕", 9), cursor="hand2", padx=4, pady=5)

    def _restore_position(self):
        try:
            x, y = int(self.data.get("x", 120)), int(self.data.get("y", 140))
            self.root.geometry(f"+{x}+{y}")
        except Exception: pass

    def start_drag(self, event):
        self.drag = (event.x_root, event.y_root, self.root.winfo_x(), self.root.winfo_y())
    def do_drag(self, event):
        if self.drag:
            dx, dy = event.x_root-self.drag[0], event.y_root-self.drag[1]
            self.root.geometry(f"+{self.drag[2]+dx}+{self.drag[3]+dy}")
    def canvas_drag(self, event):
        if self.drag:
            self.do_drag(event)
    def end_drag(self, event):
        self.drag = None
        self.save_data()
    def pet_click(self, event):
        self.drag = (event.x_root, event.y_root, self.root.winfo_x(), self.root.winfo_y())
        if 65 < event.x < 250 and 30 < event.y < 180:
            self.data["happiness"] = clamp(self.data["happiness"] + 3)
            self.action, self.action_until = "happy", time.time()+1.5
            self.data["xp"] += 1
            self.save_data()
            self.refresh()
    def minimize(self):
        self.root.overrideredirect(False)
        self.root.iconify()
        self.root.after(500, lambda: self.root.overrideredirect(True) if self.root.state() != "normal" else None)
    def close(self):
        self.save_data()
        self.root.destroy()
    def toggle_panel(self):
        pass

    def stage(self):
        days = self.data["age_seconds"] / 86400
        if days < 1: return "아기"
        if days < 3: return "어린이"
        if days < 7: return "청소년"
        return "어른"

    def feed(self):
        if self.data["items"].get("간식", 0) <= 0:
            messagebox.showinfo("간식이 없어요", "상점에서 간식을 구매해 주세요.")
            return
        self.data["items"]["간식"] -= 1
        self.data["hunger"] = clamp(self.data["hunger"] + 25)
        self.data["happiness"] = clamp(self.data["happiness"] + 4)
        self.data["xp"] += 5
        self.action, self.action_until = "eat", time.time()+2
        self.save_data(); self.refresh()

    def play(self):
        if self.data["energy"] < 12:
            messagebox.showinfo("기력이 부족해요", "조금 쉬게 해 주세요.")
            return
        self.data["happiness"] = clamp(self.data["happiness"] + 18)
        self.data["energy"] = clamp(self.data["energy"] - 10)
        self.data["hunger"] = clamp(self.data["hunger"] - 5)
        self.data["xp"] += 8
        self.data["coins"] += 5
        self.action, self.action_until = "play", time.time()+3
        self.save_data(); self.refresh()

    def sleep_pet(self):
        self.data["energy"] = clamp(self.data["energy"] + 25)
        self.action, self.action_until = "sleep", time.time()+3
        self.save_data(); self.refresh()

    def switch_pet(self):
        self.data["pet_type"] = "고양이" if self.data["pet_type"] == "강아지" else "강아지"
        self.data["name"] = "몽글이" if self.data["pet_type"] == "강아지" else "냥글이"
        self.save_data(); self.refresh()

    def open_shop(self):
        win = tk.Toplevel(self.root)
        win.title("몽글펫 상점"); win.geometry("290x245")
        win.configure(bg="#fbf6ef"); win.attributes("-topmost", True)
        tk.Label(win, text=f"🪙 보유 코인: {self.data['coins']}", bg="#fbf6ef",
                 font=("맑은 고딕", 11, "bold")).pack(pady=10)
        products = [("간식", "🍖 간식 3개", 15), ("공", "🎾 장난감 공", 30), ("쿠션", "🛏 포근한 쿠션", 45)]
        for item, label, price in products:
            row = tk.Frame(win, bg="#fbf6ef"); row.pack(fill="x", padx=15, pady=5)
            tk.Label(row, text=f"{label}  ·  {price} 코인", bg="#fbf6ef",
                     font=("맑은 고딕", 9)).pack(side="left")
            tk.Button(row, text="구매", command=lambda i=item,p=price: self.buy_item(i,p,win),
                      bg="#d8e8d9", bd=0, padx=10).pack(side="right")
        tk.Label(win, text="놀아 주면 코인을 얻어요.", bg="#fbf6ef",
                 fg="#88796c", font=("맑은 고딕", 8)).pack(pady=7)

    def buy_item(self, item, price, win):
        if self.data["coins"] < price:
            messagebox.showinfo("코인 부족", "놀아 주기로 코인을 모아 보세요.", parent=win)
            return
        self.data["coins"] -= price
        self.data["items"][item] = self.data["items"].get(item, 0) + (3 if item == "간식" else 1)
        self.save_data(); self.refresh()
        messagebox.showinfo("구매 완료", f"{item} 구매 완료!", parent=win)

    def draw_pet(self):
        c = self.canvas; c.delete("all")
        # soft, simple pseudo-3D scene
        c.create_rectangle(0,0,310,190, fill="#e8f1e8", outline="")
        c.create_oval(22,145,288,194, fill="#d5e2d3", outline="")
        # window/sun decorative background
        c.create_oval(240,12,278,50, fill="#f7e6ae", outline="")
        c.create_oval(14,18,54,58, fill="#d5e8ed", outline="")
        c.create_oval(30,26,46,42, fill="#e8f1e8", outline="")
        is_cat = self.data["pet_type"] == "고양이"
        baby = self.stage() == "아기"
        scale = 0.78 if baby else (0.90 if self.stage()=="어린이" else 1.0)
        cx, cy = 155, 111
        bob = math.sin(time.time()*3)*2 if self.action not in ("sleep",) else 0
        cy += bob
        fur = "#e8b985" if not is_cat else "#b9c3d3"
        dark = "#b77d4b" if not is_cat else "#818da4"
        light = "#f7d7b4" if not is_cat else "#dfe5ef"
        # body shadow and body
        c.create_oval(cx-53*scale,cy+21*scale,cx+53*scale,cy+66*scale, fill="#c2d0c1", outline="")
        c.create_oval(cx-43*scale,cy-3*scale,cx+43*scale,cy+54*scale, fill=dark, outline="")
        c.create_oval(cx-38*scale,cy-8*scale,cx+38*scale,cy+48*scale, fill=fur, outline="")
        c.create_oval(cx-25*scale,cy+3*scale,cx+22*scale,cy+38*scale, fill=light, outline="")
        # ears
        if is_cat:
            c.create_polygon(cx-31*scale,cy-42*scale,cx-27*scale,cy-75*scale,cx-5*scale,cy-48*scale,
                             fill=dark, outline="")
            c.create_polygon(cx+5*scale,cy-48*scale,cx+28*scale,cy-75*scale,cx+32*scale,cy-40*scale,
                             fill=dark, outline="")
            c.create_polygon(cx-25*scale,cy-47*scale,cx-26*scale,cy-65*scale,cx-13*scale,cy-48*scale,
                             fill="#eaa8b5", outline="")
            c.create_polygon(cx+14*scale,cy-48*scale,cx+27*scale,cy-65*scale,cx+25*scale,cy-45*scale,
                             fill="#eaa8b5", outline="")
        else:
            c.create_oval(cx-49*scale,cy-52*scale,cx-17*scale,cy-17*scale, fill=dark, outline="")
            c.create_oval(cx+17*scale,cy-52*scale,cx+49*scale,cy-17*scale, fill=dark, outline="")
            c.create_oval(cx-45*scale,cy-49*scale,cx-22*scale,cy-22*scale, fill=fur, outline="")
            c.create_oval(cx+22*scale,cy-49*scale,cx+45*scale,cy-22*scale, fill=fur, outline="")
        # head
        c.create_oval(cx-39*scale,cy-61*scale,cx+39*scale,cy+10*scale, fill=dark, outline="")
        c.create_oval(cx-35*scale,cy-65*scale,cx+35*scale,cy+5*scale, fill=fur, outline="")
        # shiny highlight
        c.create_oval(cx-25*scale,cy-55*scale,cx-8*scale,cy-40*scale, fill=light, outline="")
        # eyes / sleeping face
        if self.action == "sleep" and time.time() < self.action_until:
            c.create_arc(cx-24*scale,cy-30*scale,cx-8*scale,cy-18*scale, start=0, extent=180, style="arc", width=2)
            c.create_arc(cx+8*scale,cy-30*scale,cx+24*scale,cy-18*scale, start=0, extent=180, style="arc", width=2)
            c.create_text(cx+44,cy-66,text="Z", fill="#7780b5", font=("Arial",13,"bold"))
        else:
            c.create_oval(cx-23*scale,cy-31*scale,cx-12*scale,cy-15*scale, fill="#42352e", outline="")
            c.create_oval(cx+12*scale,cy-31*scale,cx+23*scale,cy-15*scale, fill="#42352e", outline="")
            c.create_oval(cx-20*scale,cy-29*scale,cx-16*scale,cy-24*scale, fill="white", outline="")
            c.create_oval(cx+15*scale,cy-29*scale,cx+19*scale,cy-24*scale, fill="white", outline="")
        # muzzle / nose
        c.create_oval(cx-13*scale,cy-7*scale,cx+13*scale,cy+7*scale, fill=light, outline="")
        c.create_oval(cx-3*scale,cy-5*scale,cx+3*scale,cy+0*scale, fill="#6d5145", outline="")
        c.create_arc(cx-8*scale,cy-1*scale,cx,cy+8*scale, start=200, extent=140, style="arc", width=1)
        c.create_arc(cx,cy-1*scale,cx+8*scale,cy+8*scale, start=200, extent=140, style="arc", width=1)
        # paws
        c.create_oval(cx-32*scale,cy+37*scale,cx-8*scale,cy+52*scale, fill=light, outline="")
        c.create_oval(cx+8*scale,cy+37*scale,cx+32*scale,cy+52*scale, fill=light, outline="")
        if self.action in ("happy","play") and time.time() < self.action_until:
            c.create_text(cx+55,cy-45,text="♥", fill="#e88e9c", font=("Arial",18,"bold"))
        if self.data["hunger"] < 20:
            c.create_text(cx-53,cy-65,text="…", fill="#ad7770", font=("Arial",17,"bold"))
        c.create_text(155,177,text=f"{self.data['name']}  ·  {self.stage()} {self.data['pet_type']}",
                      fill="#52664f", font=("맑은 고딕",9,"bold"))

    def refresh(self):
        self.name_label.config(text=f"🐾 {self.data['name']}")
        self.stage_label.config(text=f"Lv.{1 + int(self.data['xp']//50)} · {self.stage()}")
        for key, (bar, val) in self.stats.items():
            value = int(self.data[key])
            bar.delete("all")
            w = max(1, int(bar.winfo_width() * value / 100))
            color = "#8fbf9a" if value > 55 else ("#e9c47b" if value > 25 else "#d98b84")
            bar.create_rectangle(0,0,w,10, fill=color, outline="")
            bar.create_text(120,5,text="", fill="")
            val.config(text=f"{value}%")
        items = self.data["items"]
        self.info.config(text=f"🪙 {self.data['coins']} 코인   ·   🍖 {items.get('간식',0)}   ·   🎾 {items.get('공',0)}")
        self.draw_pet()

    def tick(self):
        self.data["age_seconds"] += 1
        self.data["hunger"] = clamp(self.data["hunger"] - 0.035)
        self.data["happiness"] = clamp(self.data["happiness"] - 0.018)
        self.data["energy"] = clamp(self.data["energy"] - 0.012)
        if time.time() - self.data.get("last_saved",0) > 15:
            self.save_data()
        self.refresh()
        self.root.after(1000, self.tick)

if __name__ == "__main__":
    root = tk.Tk()
    app = DeskPet(root)
    root.mainloop()
