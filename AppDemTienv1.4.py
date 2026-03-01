import tkinter as tk
from tkinter import ttk
import json
import os

class MoneyCounter:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Ứng dụng đếm tiền v1.4")
        self.window.configure(bg='#f0f0f0')
        
        # Thiết lập Icon cho ứng dụng (nếu có)
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "Calculator.ico")
            if os.path.exists(icon_path):
                self.window.iconbitmap(icon_path)
            else:
                # Tìm icon trong cùng thư mục chạy script
                if os.path.exists("Calculator.ico"):
                    self.window.iconbitmap("Calculator.ico")
        except Exception:
            pass

        # General Padding Values - DÙNG CHUNG
        self.padx_value = 15
        self.pady_value = 8

        # Style configuration
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), background='#f0f0f0')
        style.configure('Content.TLabel', font=('Arial', 11), background='#f0f0f0')
        style.configure('Money.TLabel', font=('Arial', 11), foreground='#2c3e50')
        style.configure('Sum.TLabel', font=('Arial', 11, 'bold'), foreground='#27ae60')
        style.configure('Total.TLabel', font=('Arial', 13, 'bold'), foreground='#2980b9')
        style.configure('Action.TButton', font=('Arial', 11), padding=10, cursor="hand2")
        style.configure('Error.TLabel', font=('Arial', 10), foreground='red')

        # Main frame
        main_frame = ttk.Frame(self.window, padding="30")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        self.denominations = [500000, 200000, 100000, 50000, 20000, 10000, 5000]
        self.entries = []
        self.entry_vars = [] # Lưu trữ các StringVar để theo dõi thay đổi
        self.sum_labels = []

        # Header Frame
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, self.pady_value * 2))

        headers = ["Mệnh giá (VNĐ)", "Số lượng", "Thành tiền (VNĐ)"]
        for col, header in enumerate(headers):
            label = ttk.Label(header_frame, text=header, style='Header.TLabel')
            label.grid(row=0, column=col, padx=self.padx_value)

        for i, denom in enumerate(self.denominations):
            denom_label = ttk.Label(main_frame, text=f"{denom:,}", style='Money.TLabel')
            denom_label.grid(row=i+1, column=0, padx=self.padx_value, pady=self.pady_value, sticky="e")

            def validate_input(P, idx=i):
                if P == "":
                    return True
                if P.isdigit():
                    value = int(P)
                    if 0 <= value <= 9999:
                        return True
                    else:
                        self.error_label.config(text="Số lượng quá lớn!")
                        return False
                self.error_label.config(text="Chỉ nhập số!")
                return False

            vcmd = (self.window.register(validate_input), '%P')

            # Sử dụng StringVar để theo dõi thay đổi nội dung (Real-time updates)
            entry_var = tk.StringVar(value="0")
            entry_var.trace_add("write", lambda *args, idx=i: self.on_var_change(idx))
            self.entry_vars.append(entry_var)

            entry = ttk.Entry(main_frame, width=10, justify='center', font=('Arial', 11), 
                              validate='key', validatecommand=vcmd, textvariable=entry_var)
            entry.grid(row=i+1, column=1, padx=self.padx_value, pady=self.pady_value, sticky="ew")
            entry.bind('<Up>', lambda e, idx=i: self.increase_value(idx))
            entry.bind('<Down>', lambda e, idx=i: self.decrease_value(idx))
            entry.bind('<FocusIn>', lambda e, entry=entry: self.on_entry_click(entry))
            
            # === THÊM MỚI: Bind phím Enter (Return) với hàm di chuyển focus ===
            entry.bind('<Return>', self.move_focus_on_enter)
            
            self.entries.append(entry)

            sum_label = ttk.Label(main_frame, text="0", style='Sum.TLabel', width=15)
            sum_label.grid(row=i+1, column=2, padx=self.padx_value, pady=self.pady_value, sticky="e")
            self.sum_labels.append(sum_label)

        # Button frame (chỉ giữ nút "Reset tiền")
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(self.denominations)+2, column=0, columnspan=3, pady=self.pady_value*2)

        self.reset_btn = ttk.Button(button_frame, text="Reset tiền", style='Action.TButton', 
                                      command=self.reset_all, takefocus=False)
        self.reset_btn.grid(row=0, column=0, padx=self.padx_value)

        # Total amount frame
        total_frame = ttk.Frame(main_frame)
        total_frame.grid(row=len(self.denominations)+3, column=0, columnspan=3, pady=self.pady_value)

        ttk.Label(total_frame, text="Tổng cộng:", style='Header.TLabel').grid(row=0, column=0, padx=self.padx_value)
        self.total_label = ttk.Label(total_frame, text="0 VNĐ", style='Total.TLabel', width=20)
        self.total_label.grid(row=0, column=1, padx=self.padx_value)

        # Note section
        note_frame = ttk.LabelFrame(main_frame, text="Ghi chú", padding="15")
        note_frame.grid(row=len(self.denominations)+4, column=0, columnspan=3, pady=self.pady_value, sticky="ew")
        note_frame.grid_columnconfigure(0, weight=1)

        self.note_text = tk.Text(note_frame, height=6, width=60, font=('Arial', 11), wrap="word", 
                                 relief="solid", borderwidth=1)
        self.note_text.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        scrollbar = ttk.Scrollbar(note_frame, orient="vertical", command=self.note_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.note_text.configure(yscrollcommand=scrollbar.set)

        note_button_frame = ttk.Frame(note_frame)
        note_button_frame.grid(row=1, column=0, columnspan=2, pady=(15, 5))

        save_note_btn = ttk.Button(note_button_frame, text="Lưu ghi chú", style='Action.TButton', 
                                     command=self.save_note, takefocus=False)
        save_note_btn.grid(row=0, column=0, padx=self.padx_value)

        clear_note_btn = ttk.Button(note_button_frame, text="Xóa ghi chú", style='Action.TButton', 
                                      command=self.clear_note, takefocus=False)
        clear_note_btn.grid(row=0, column=1, padx=self.padx_value)

        # Copyright label
        copyright_label = ttk.Label(main_frame, text="©Nguyễn Duy Trường 2025 v1.4", 
                                      font=('Arial', 9), foreground='#666666', anchor="center")
        copyright_label.grid(row=len(self.denominations)+5, column=0, columnspan=3, pady=(15, 0), sticky="ew")

        # Label hiển thị thông báo lỗi
        self.error_label = ttk.Label(main_frame, text="", style="Error.TLabel")
        self.error_label.grid(row=len(self.denominations)+6, column=0, columnspan=3)

        
        # Load ghi chú và số lượng tiền đã lưu (nếu có)
        self.load_note()
        self.load_data()  # Load dữ liệu số lượng tờ tiền từ file JSON

        self.window.update_idletasks()
        self.window.minsize(600, 800)

        self.window.update_idletasks()
        width = 600
        height = 800
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f'{width}x{height}+{x}+{y}')

        # Bind phím tắt toàn cục
        self.window.bind("<Control-r>", lambda e: self.reset_all())
        self.window.bind("<Control-s>", lambda e: self.save_note())

        self.window.mainloop()
        
    # === HÀM MỚI: Di chuyển focus khi nhấn Enter ===
    def move_focus_on_enter(self, event):
        """Moves focus to the next entry widget, like the Tab key."""
        widget = event.widget
        # Tìm vị trí của widget hiện tại trong danh sách các ô entry
        try:
            current_index = self.entries.index(widget)
        except ValueError:
            # Nếu widget không có trong danh sách, không làm gì cả
            return

        # Tính toán vị trí của ô entry tiếp theo, quay vòng lại từ đầu nếu ở ô cuối
        next_index = (current_index + 1) % len(self.entries)
        
        # Di chuyển focus đến ô tiếp theo
        next_entry = self.entries[next_index]
        next_entry.focus_set()
        
        # Bôi đen toàn bộ text trong ô mới để người dùng dễ dàng nhập đè lên
        next_entry.select_range(0, tk.END)
        
        # Ngăn hành vi mặc định của phím Enter (ví dụ: xuống dòng)
        return "break"

    def on_var_change(self, index):
        """Callback khi giá trị trong StringVar thay đổi."""
        self.update_subtotal_and_total(index)

    def on_entry_click(self, entry):
        if entry.get() == "0":
            entry.delete(0, tk.END)

    def increase_value(self, index):
        try:
            current = self.entries[index].get()
            if current == '':
                current = '0'
            current = int(current)
            if current < 9999:
                self.entries[index].delete(0, tk.END)
                self.entries[index].insert(0, str(current + 1))
                self.update_subtotal_and_total(index)
            else:
                self.error_label.config(text="Số lượng quá lớn!")
        except ValueError:
            self.entries[index].delete(0, tk.END)
            self.entries[index].insert(0, "0")
            self.update_subtotal_and_total(index)

    def decrease_value(self, index):
        try:
            current = self.entries[index].get()
            if current == '':
                current = '0'
            current = int(current)
            if current > 0:
                self.entries[index].delete(0, tk.END)
                self.entries[index].insert(0, str(current - 1))
                self.update_subtotal_and_total(index)
        except ValueError:
            self.entries[index].delete(0, tk.END)
            self.entries[index].insert(0, "0")
            self.update_subtotal_and_total(index)

    def reset_all(self):
        for var in self.entry_vars:
            var.set("0")
        for sum_label in self.sum_labels:
            sum_label.config(text="0")
        self.total_label.config(text="0 VNĐ")
        self.error_label.config(text="")
        self.update_total()
        self.save_data()  # Lưu trạng thái sau khi reset

    def save_note(self):
        note_content = self.note_text.get("1.0", tk.END)
        with open("money_counter_note.txt", "w", encoding="utf-8") as f:
            f.write(note_content)

    def clear_note(self):
        self.note_text.delete("1.0", tk.END)
        try:
            os.remove("money_counter_note.txt")
        except FileNotFoundError:
            pass

    def load_note(self):
        try:
            with open("money_counter_note.txt", "r", encoding="utf-8") as f:
                note_content = f.read()
                self.note_text.delete("1.0", tk.END)
                self.note_text.insert("1.0", note_content)
        except FileNotFoundError:
            pass

    def save_data(self):
        data = {
            "entries": [var.get() for var in self.entry_vars]
        }
        with open("money_counter_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_data(self):
        if os.path.exists("money_counter_data.json"):
            with open("money_counter_data.json", "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if "entries" in data:
                        for i, count in enumerate(data["entries"]):
                            if i < len(self.entry_vars):
                                self.entry_vars[i].set(str(count))
                                try:
                                    quantity = int(count)
                                except ValueError:
                                    quantity = 0
                                self.update_subtotal(i, quantity)
                        self.update_total()
                except json.JSONDecodeError:
                    pass

    def update_subtotal(self, index, quantity):
        subtotal = quantity * self.denominations[index]
        self.sum_labels[index].config(text=f"{subtotal:,}")

    def update_total(self):
        total = 0
        for i, entry in enumerate(self.entries):
            try:
                quantity = int(entry.get())
                total += quantity * self.denominations[i]
            except ValueError:
                pass
        self.total_label.config(text=f"{total:,} VNĐ")

    def update_subtotal_and_total(self, index):
        try:
            quantity = int(self.entries[index].get())
        except ValueError:
            quantity = 0
        self.update_subtotal(index, quantity)
        self.update_total()
        self.save_data()  # Lưu dữ liệu mỗi khi cập nhật số lượng

if __name__ == "__main__":
    app = MoneyCounter()