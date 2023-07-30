import argparse
import utils
import commons
import torch
from vits_F.models import SynthesizerTrn
from text import text_to_sequence
from torch import no_grad, LongTensor
from scipy.io.wavfile import write

def get_text(text, hps):
    text_norm = text_to_sequence(text,hps.symbols, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm

def text_to_speech(text, model_path, config_path, output_file, noise_scale, noise_scale_w, length_scale, speaker_id):
    device = torch.device('cpu')
    hps = utils.get_hparams_from_file(config_path)
    net = SynthesizerTrn(
        len(hps.symbols),
        hps.data.filter_length // 2 + 1,
        hps.train.segment_size // hps.data.hop_length,
        n_speakers=hps.data.n_speakers,
        **hps.model)
    utils.load_checkpoint(model_path, net)
    net = net.eval().to(device)

    text = text.replace('\n', ' ').replace('\r', '').replace(" ", "")
    stn_tst = get_text(text, hps)
    with no_grad():
        x_tst = stn_tst.unsqueeze(0).to(device)
        x_tst_lengths = LongTensor([stn_tst.size(0)]).to(device)
        sid = LongTensor([speaker_id]).to(device)
        audio = net.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=noise_scale, noise_scale_w=noise_scale_w,
                          length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()

    write(output_file, 22050, audio)

#text_to_speech("今日の杭州市の天気は曇りで、気温は32度になるようです！明日の天気予報によると、中雨が降る予定で、最高気温は29度、最低気温は24度です。ご主上様、ご注意くださいね〜」「ご主上様、何かお手伝いできることはありますか？アマギはいつでもご奉仕いたしますよ〜", "../model/yao/G_12000.pth", "../model/yao/config12000.json", "output.wav")