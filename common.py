import gpt4
from mainxiaoyao import TTSHandler




tttts = TTSHandler()

def use_live2d(uselive2d):
    tttts.use_or(uselive2d)

def ttss(part, part_jp, model_path, config_path):

      tttts.tts(part, part_jp, model_path, config_path)

def getanswer4(text):
    chat=gpt4.Chat4()
    answer=chat.get_answer(text)
    return answer

def getanswer3_5(text):
    chat=gpt4.Chat3_5()
    answer=chat.get_answer(text)
    return answer