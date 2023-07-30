import pyqt5_chat

text=()
def weather():
    print("***判断是否需要生图***")
    switch = [
        {"role": "system",
         "content": "DELL是一种图像生成AI，而你一个判断自然语言是否需要执行图像生成功能的判断工具，你只需要返回是或否。判断我发你的文字是否涉及到了生图/画图/画一张"}]
    boo = pyqt5_chat.get_response(text, switch)
    print(boo)
    if "是" in boo:
        return True
    else:
        return False