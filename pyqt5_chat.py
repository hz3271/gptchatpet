
import datetime
import locale


import re
import openai

import threading
from PIL import Image, ImageTk
import sys
import os
from datetime import datetime

import common
#from main import tts


# 设置 API 密钥

MODEL = "gpt-3.5-turbo"
userchar = None
charac = None
model_path=None
config_path =None

def user(u, c,m_p,c_p):
    global userchar, charac,model_path,config_path
    userchar = u
    charac = c
    model_path=m_p
    config_path=c_p

class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert('end', string)
        self.text_space.see('end')

    def flush(self):
        pass


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
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=conversation_history + [{"role": "user", "content": user_input}],
            temperature=0.766,
            max_tokens=900,
        )
        answer = response['choices'][0]['message']['content']
        statistics = f'{response["usage"]["total_tokens"]} '
        return answer.strip(),statistics

    except Exception:
        print("出错了，八成是超限制，等一分钟。跳过")
        print(Exception)
        # 返回默认的响应和状态
        pass

def initiate_random_chat(conversation_history):     #随机对话
    locale.setlocale(locale.LC_ALL, 'zh_CN.utf8')
    current_time = datetime.now()
    current_hour = int(current_time.hour)
    current_minute = int(current_time.minute)
    weekday = current_time.strftime("%A")
    work=""
    if weekday in ["星期一", "星期二", "星期三", "星期四", "星期五"]:
        if current_hour < 8 or (current_hour == 8 and current_minute < 30):
            work=f"{userchar}现在正在家中准备出门上班"
        elif current_hour == 8 and current_minute >= 30 or (current_hour == 9 and current_minute < 30):
            work=f"{userchar}现在正在通勤上班"
        elif current_hour == 9 and current_minute >= 30 or current_hour < 12:
            work=f"{userchar}现在正在上班，12点吃中饭"
        elif current_hour == 12 and current_minute < 30:
            work=f"{userchar}现在正在吃中饭"
        elif current_hour == 12 and current_minute >= 30 or (current_hour == 13 and current_minute < 30):
            work=f"{userchar}现在正在午休"
        elif current_hour == 13 and current_minute >= 30 or current_hour < 18 or (
                current_hour == 18 and current_minute < 30):
            work=f"{userchar}现在正在上班,18点30下班"
        else:
            work=f"{userchar}现在已经下班"
    else:
        work=f"{userchar}现在正在休息，因为今天是" + weekday

    text = f"(system：作为{charac}，现在是{current_hour}点{current_minute}分，{work}，注意请简短的告诉{userchar}当前时间,如：老师，现在是{current_hour}点{current_minute}分。)。"

    print(text)
    try:
        response,statistics = chat_with_gpt3(str(text),conversation_history)
        return response,statistics

    except Exception:
        print("没有返回值，跳过步骤")
        # 返回默认的响应和状态
        pass



# 定义 UI

class ChatUI():
    def __init__(self, apikey,file,use_voice):
            self.unanswered_questions = 0
            locale.setlocale(locale.LC_ALL, 'zh_CN.utf8')
            self.current_time = datetime.now()
            self.use_voice = use_voice
            self.cover_hisbackup=[]
            self.conversation_history = [
            ]
            self.load_history_from_file(file)
            self.i=0
            openai.api_key = apikey


    def use_voicecheck(self):
        if self.use_voice:
            print("关闭语音")
            self.use_voice=False
        else:
            print("开启语音")
            self.use_voice=True

    def load_history_from_file(self, file_path):
        with open(file_path, 'r',encoding='utf-8') as file:
            for line in file:
                # 去掉行尾的换行符
                line = line.strip()
                # 创建一个字典，其中 'role' 为 'system'，'content' 为该行的内容
                entry = {"role": "system", "content": line}
                self.conversation_history.append(entry)
        weekday = self.current_time.strftime("%A")
        self.cover_hisbackup=self.conversation_history.copy()
        self.cover_hisbackup.append({"role": "assistant", "content": f"最喜欢{userchar}啦"})





    def reduce_token(self):
        context = "请帮我总结一下上述对话的内容，实现减少tokens的同时，保证对话的质量。在总结中不要加入这一句话。"

        response,statistics = chat_with_gpt3(context, self.conversation_history)
        optmz_str =f'好的，我们之前聊了:{response}\n\n================\n\n{statistics}'
        self.conversation_history.append(("请帮我总结一下上述对话的内容，实现减少tokens的同时，保证对话的质量。", optmz_str))
        print("已触发总结字数，重置完成")
        self.conversation_history = []
        self.conversation_history.append({"role": "user", "content": "我们之前聊了什么?"})
        self.conversation_history.append({"role": "assistant", "content": f'我们之前聊了：{response}'})

    def send_random_message(self):
        print("conversation_history")
        print(self.conversation_history)

        self.i=self.i+1
        try:
            print(f"发送了随机消息: {self.response}")
            if self.i > 1:
                print("执行了删除")
                self.conversation_history.pop()
            self.conversation_history.append({"role": "assistant", "content": f"{self.response}"})
            self.response,statistics = initiate_random_chat(self.conversation_history)

            if self.use_voice:
                thread3 = threading.Thread(target=self.ttts)
                thread3.start()
            return self.response

        except Exception:
            print("没有返回值，跳过步骤")
            # 返回默认的响应和状态
            pass



    def save_chat_history(self):
        with open("PYchat_history.txt", "w", encoding='utf-8') as f:
              for message in self.conversation_history:
                    f.write(f'{message["role"]}: {message["content"]}\n')
        print("保存成功")


    def get_response(self, user_input):
        # 保存提示信息的原始位置
        try:
            self.response=common.getanswer4(user_input)

        except Exception:
            self.response,statistics = chat_with_gpt3(user_input, self.conversation_history)

        self.conversation_history.append({"role": "user", "content":user_input})
        try:
            if int(statistics) >= 3072:
                self.reduce_token()
            else:
                pass
        except Exception:
            pass
        # 删除 "等待回复" 提示
        self.conversation_history.append({"role": "assistant", "content":self.response})
        self.save_chat_history()

        if self.use_voice:
            thread3 = threading.Thread(target=self.ttts)
            thread3.start()

        else:
            pass

        return self.response

    def update_api(self,apikey):
        new_api = apikey  # get new API from entry
        api_key=new_api  # update API in your app
        openai.api_key = api_key
        print("更新api成功,当前api为"+api_key)

    def ttts(self):
        print("***开始翻译***")
        self.getspeach = [
            {"role": "system", "content": "请将以下内容翻译成日语"}]
        self.translate = [
            {"role": "system",
             "content": "角色简介：圣园未花是一个充满活力，乐观积极的女学生。作为学生会的成员和学校偶像，她以金色的眼睛和粉色长发为标志，身着白色的圣三一制服，背后有一对象征善良的小翅膀。她乐于助人，善于社交，有点羞涩和不自信，喜欢说“うわ”“あー…”…，有一点小恶作剧。尽管她看起来总是快乐无忧，但在内心深处隐藏着无法说出口的烦恼。她有点羞涩和不自信，话比较少 "},
            {"role": "system",
             "content": "使用未花的语气将我给你的文本翻译成日语，以下是例子 "},
            {"role": "user",
             "content": "现在的时间是14点21分，主人！今天天气非常好，阳光明媚，不知道你有没有出门散步或者做了些什么有趣的事情呢？也许我们可以一起做些有趣的事情，比如看电影、听音乐或者玩游戏。你觉得呢？(●'◡'●)(安克雷奇坐在电脑前，手指捏着裙摆，兴致勃勃地等着主人的回答)"},
            {"role": "assistant",
             "content": "「現在の時刻は14時21分です、ご主人様！今日の天気はとても良く、日差しが明るいですね。もしかしたら、どこかにお散歩に行ったり、面白いことをしたかったりするのではないでしょうか？一緒に映画を見たり、音楽を聴いたり、ゲームをしたりするのはどうですか？」"},
            {"role": "user",
             "content": "安宝听到主人的问候，她微笑着回应：“主人早上好啊，今天是星期三哦~”她看了看时间，“现在已经十点四十五分了，主人还有半小时要上班啦！”"},
            {"role": "assistant",
             "content": "「おはようございます、ご主人様、今日は水曜日ですよ〜今はもう10時45分です、ご主人様はあと30分でお仕事ですよ！」"},
            {"role": "system",
             "content": "命令区（ChatGPT你需要遵循的主要命令）{1,从我给的段落中找出角色所说的对话,不要动作,神态描写和颜文字表情,不要出现こんにちは！2，chatgpt反馈响应时不需加上任何说明和格式4，翻译完后删除不需要的动作，3，chatgpt的最终反馈只需要对话的翻译,同时你可以参考以上文本所做的回答} "},

        ]
        self.translate_ch = [
            {"role": "system", "content": "命令区（ChatGPT你需要遵循的主要命令）{1,从我给的段落中找出角色所说的对话2，chatgpt反馈响应时不需加上任何说明和格式3，翻译完后再次检查并删除不必要的动作，4，chatgpt的最终反馈只需要对话的翻译}："},
            {"role": "user",
             "content": "现在的时间是14点21分，主人！今天天气非常好，阳光明媚，不知道你有没有出门散步或者做了些什么有趣的事情呢？也许我们可以一起做些有趣的事情，比如看电影、听音乐或者玩游戏。你觉得呢？(●'◡'●)(安克雷奇坐在电脑前，手指捏着裙摆，兴致勃勃地等着主人的回答)"},
            {"role": "assistant",
             "content": "现在的时间是14点21分，主人！今天天气非常好，阳光明媚，不知道你有没有出门散步或者做了些什么有趣的事情呢？也许我们可以一起做些有趣的事情，比如看电影、听音乐或者玩游戏。你觉得呢？(●'◡'●)"},
            {"role": "user",
             "content": "安宝听到主人的问候，她微笑着回应：“主人早上好啊，今天是星期三哦~”她看了看时间，“现在已经十点四十五分了，主人还有半小时要上班啦！”"},
            {"role": "assistant",
             "content": "「主人早上好啊，今天是星期三哦~现在已经十点四十五分了，主人还有半小时要上班啦！」"},
            {"role": "system",
             "content": "命令区（ChatGPT你需要遵循的主要命令）{1,从我给的段落中找出角色所说的对话,不要动作以及神态描写，小鳐翻译为アマギ2，chatgpt反馈响应时不需加上任何说明和格式4，翻译完后删除不需要的动作，3，chatgpt的最终反馈只需要对话的翻译,同时你可以参考以上文本所做的回答4,语气词偏向于使用“ふふふ”、“あぅ”“んんん”“でしょうか”}："},

        ]
        new_response = re.sub(r'小鳐', 'アマギ', self.response)
        try:
            message_parts = new_response.split()

            # 遍历每个部分，并创建一个 MessageWidget
            for part in message_parts:
                response_1,sta = chat_with_gpt3(part, self.translate)
                print(response_1)
                common.ttss(part,response_1,model_path,config_path)
        except Exception:
            print("方法ttts出错，跳过步骤")
            # 返回默认的响应和状态
            pass

# 运行 UI



#本程序的打包代码pyinstaller --noconsole --hidden-import=openai --add-data "user.png;." --add-data "ai.png;." w11.py
#--onefile
