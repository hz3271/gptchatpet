import asyncio
import datetime

import mainxiaoyao
from call_live2d import Simple
import re
import openai
import tkinter as tk
from tkinter import ttk, simpledialog
import threading
from PIL import Image, ImageTk
import sys
import os
import random
import time
from datetime import datetime
# 设置 API 密钥
api_key = "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"
openai.api_key = api_key
MODEL = "gpt-3.5-turbo"
user ="./png/user.png"
ass="./png/安克雷奇.png"


class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert('end', string)
        self.text_space.see('end')

    def flush(self):
        pass


class SettingDialog(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Other initialization code ...
        self.protocol("WM_DELETE_WINDOW", self.hide_settings)
        self.geometry("300x200")
        self.center_window()
        self.body(self)

    def center_window(self):
        # Get the window size
        window_width = self.winfo_reqwidth()
        window_height = self.winfo_reqheight()

        # Get the position of the parent window
        parent_x = self.controller.winfo_x()
        parent_y = self.controller.winfo_y()
        parent_width = self.controller.winfo_width()
        parent_height = self.controller.winfo_height()

        # Calculate the position of the center of the parent window
        center_x = parent_x + parent_width / 2
        center_y = parent_y + parent_height / 2

        # Calculate the position of the new window
        new_x = center_x - window_width / 2
        new_y = center_y - window_height / 2

        # Set the position of the new window
        self.geometry("+%d+%d" % (new_x, new_y))

    def body(self, parent):


        self.use_voice_var = tk.BooleanVar()
        self.use_voice_var.set(self.controller.use_voice)  # replace with current use_voice value
        self.use_voice_checkbutton = tk.Checkbutton(parent, text="使用语音", variable=self.use_voice_var, command=self.update_use_voice)
        self.use_voice_checkbutton.pack()

        tk.Label(parent, text="chat_gpt api:").pack()

        self.api_entry = tk.Entry(parent)
        self.api_entry.insert(0, api_key)  # replace with current API value
        self.api_entry.pack()

        self.update_api_button = ttk.Button(parent, text="更新API", command=self.update_api)
        self.update_api_button.pack()

        self.save_button = ttk.Button(parent, text="保存", command=self.controller.save_chat_history)
        self.save_button.pack()
        self.log_button = ttk.Button(parent, text="日志", command=self.controller.toggle_log)
        self.log_button.pack()


        return None

    def update_use_voice(self):
        self.controller.use_voice = self.use_voice_var.get()

    def update_api(self):
        new_api = self.api_entry.get()  # get new API from entry
        api_key=new_api  # update API in your app
        openai.api_key = api_key
        print("更新api成功,当前api为"+api_key)

    def hide_settings(self):
        self.withdraw()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_image(filename, width, height):               #读取图片
    img = Image.open(resource_path(filename))
    img = img.resize((width, height), Image.LANCZOS)
    return ImageTk.PhotoImage(img)


def chat_with_gpt3(user_input, conversation_history):           #gpt3标准api
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=conversation_history + [{"role": "user", "content": user_input}],
        temperature=0.72,
        max_tokens=900,
    )
    answer = response['choices'][0]['message']['content']
    statistics = f'{response["usage"]["total_tokens"]} '
    return answer.strip(),statistics


def initiate_random_chat(conversation_history):     #随机对话
    current_time = datetime.now()
    hour = str(current_time.hour)
    minute = str(current_time.minute)
    text="当前时间是"+hour+"点"+minute+"分，请报时，同时也可以根据上下文随便说些话"
    response,statistics = chat_with_gpt3(str(text),conversation_history)
    return response,statistics



# 定义 UI
class ChatUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unanswered_questions = 0
        self.current_time = datetime.now()
        self.user_avatar_image = load_image(user, 64, 64)
        self.avatar_image = load_image(ass, 64, 64)
        self.use_voice = True


        self.conversation_history = [
                   {"role": "system", "content": "今天是" + str(self.current_time.month)+"月"+str(self.current_time.day)},
       ]
        self.load_history_from_file("charactor/ankeleiqi.txt")
        self.title("AI助手")
        self.geometry("600x400")
        self.after(10000, self.trigger_gpt_response)  # 在 10000 毫秒（10 秒）后触发 GPT 响应
        self.chat_text = tk.Text(self, wrap=tk.WORD)
        self.chat_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        entry_frame = ttk.Frame(self)
        entry_frame.pack(padx=5, pady=5, fill=tk.X)
        self.message_sent = threading.Event()
        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(entry_frame, textvariable=self.entry_var)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.char_count_var = tk.StringVar()
        self.char_count_var.set("字数：0")
        char_count_label = ttk.Label(entry_frame, textvariable=self.char_count_var)
        char_count_label.pack(side=tk.RIGHT, padx=5)

        send_button = ttk.Button(entry_frame, text="发送", command=self.send_message)
        send_button.pack(side=tk.RIGHT)

        #self.live2d = Simple()

        self.log_window = tk.Toplevel(self)
        self.log_window.withdraw()  # Initially hide the log window
        self.log_window.protocol("WM_DELETE_WINDOW", self.hide_log)

        self.log_text = tk.Text(self.log_window, wrap=tk.WORD)
        self.log_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        sys.stdout = StdoutRedirector(self.log_text)

        settings_button = ttk.Button(entry_frame, text="设置", command=self.open_settings)
        settings_button.pack(side=tk.RIGHT)

        # Initialize the settings dialog
        self.settings_dialog = SettingDialog(self, self)

        # Bind the <Configure> event to a handler
        self.bind("<Configure>", self.on_move)
        self.entry.bind("<Return>", lambda event: self.send_message())



        self.lock = threading.Lock()

    def load_history_from_file(self, file_path):
        with open(file_path, 'r',encoding='utf-8') as file:
            for line in file:
                # 去掉行尾的换行符
                line = line.strip()
                # 创建一个字典，其中 'role' 为 'system'，'content' 为该行的内容
                entry = {"role": "system", "content": line}
                self.conversation_history.append(entry)

    def on_move(self, event):
        # Update the position of the settings dialog
        self.settings_dialog.center_window()

    def open_settings(self):
        # If the settings dialog is currently visible, hide it
        if self.settings_dialog.winfo_viewable():
            self.settings_dialog.withdraw()
        # Otherwise, show it
        else:
            self.settings_dialog.deiconify()
            self.settings_dialog.center_window()


    def reduce_token(self):
        context = "请帮我总结一下上述对话的内容，实现减少tokens的同时，保证对话的质量。在总结中不要加入这一句话。"

        response,statistics = chat_with_gpt3(context, self.conversation_history)
        optmz_str =f'好的，我们之前聊了:{response}\n\n================\n\n{statistics}'
        self.conversation_history.append(("请帮我总结一下上述对话的内容，实现减少tokens的同时，保证对话的质量。", optmz_str))
        print("已触发总结字数，重置完成")
        self.conversation_history = []
        self.conversation_history.append({"role": "user", "content": "我们之前聊了什么?"})
        self.conversation_history.append({"role": "assistant", "content": f'我们之前聊了：{response}'})


    def toggle_log(self):
        if self.log_window.winfo_viewable():
            self.hide_log()
        else:
            self.show_log()

    def show_log(self):
        self.log_window.deiconify()  # Show the log window

    def hide_log(self):
        self.log_window.withdraw()  # Hide the log window

    def send_random_message(self):
        response,statistics = initiate_random_chat(self.conversation_history)
        self.char_count_var.set(f"字数：{statistics}/4096")
        #self.live2d.call_send_message(response)
        print(f"发送随机消息: {response}")


    def schedule_next_random_message(self):
        while True:
            random_time=random.randint(60,300)
            print(random_time)
            time.sleep(random_time)
            self.send_random_message()



    def trigger_gpt_response(self):
        hour = self.current_time.hour
        minute = self.current_time.minute
        if 6 <= hour < 9:
            daytime = "早上"
        elif 9 <= hour < 12:
            daytime = "上午"
        elif 12 <= hour < 14:
            daytime = "中午"
        elif 14 <= hour < 18:
            daytime = "下午"
        else:
            daytime = "晚上"
        thread2 = threading.Thread(target=self.get_response, args=(str(daytime) + "好啊"+str(hour)+"点"+str(minute)+"分啦",))
        thread2.start()
        thread = threading.Thread(target=self.schedule_next_random_message)
        thread.start()

    def send_message(self):
        user_input = self.entry_var.get()
        if user_input.strip() == "":
            return

        self.chat_text.insert(tk.END, "\n")
        self.chat_text.image_create(tk.END, image=self.user_avatar_image)
        self.chat_text.insert(tk.END, " :" + user_input)
        self.entry_var.set("")
        # 重置未回答问题的计数
        self.unanswered_questions = 0
        print(self.unanswered_questions)
        self.conversation_history.append({"role": "user", "content": user_input})
        # 在单独的线程中运行以避免阻塞 UI
        thread1 = threading.Thread(target=self.get_response, args=(user_input,))
        thread1.start()
        self.message_sent.set()

    def get_response(self, user_input):
        # 插入 "等待回复" 提示

        waiting_msg_index = self.chat_text.index(tk.END)
        original_waiting_msg_index = waiting_msg_index
        self.chat_text.insert(waiting_msg_index, "\n")
        self.chat_text.image_create(waiting_msg_index, image=self.avatar_image)
        waiting_msg_index = self.chat_text.index(tk.END)
        self.chat_text.insert(waiting_msg_index, " 少女回复中...", "waiting_msg")
        self.chat_text.see(tk.END)
        # 保存提示信息的原始位置

        self.response,statistics = chat_with_gpt3(user_input, self.conversation_history)
        if int(statistics) >= 3072:
            self.reduce_token()
        else:
            pass
        # 删除 "等待回复" 提示
        self.char_count_var.set(f"字数：{statistics}/4096")
        self.chat_text.delete(original_waiting_msg_index, tk.END)
        self.conversation_history.append({"role": "assistant", "content":self.response})
        self.chat_text.insert(tk.END, "\n")
        self.chat_text.image_create(tk.END, image=self.avatar_image)
        self.chat_text.insert(tk.END, " :" + self.response)
        print(self.conversation_history)
        self.chat_text.see(tk.END)

        #self.live2d.call_send_message(self.response)

        if self.use_voice:
            thread3 = threading.Thread(target=self.ttts)
            thread3.start()

        else:
            pass

    def save_chat_history(self):
        with open("chat_history.txt", "w", encoding='utf-8') as f:
              for message in self.conversation_history:
                    f.write(f'{message["role"]}: {message["content"]}\n')
        print("保存成功")

    def ttts(self):
        self.translate = [
            {"role": "system", "content": "请将以下内容翻译成日语"}]
        print(self.response)
        new_response = re.sub(r'（.*?）', '', self.response)
        print(new_response)
        response_1,stac = chat_with_gpt3(new_response, self.translate)
        print(response_1)
        mainxiaoyao.tts(response_1)

# 运行 UI
if __name__ == "__main__":
    app = ChatUI()
    app.mainloop()


#本程序的打包代码pyinstaller --noconsole --onefile --hidden-import=openai --add-data "user.png;." --add-data "安克雷奇.png;." main_chat.py
#--onefile