import sys#和第七行一起用来导入库的，如果大家电脑直接就能导入的话这两行估计可以删
import wave#不确定是否有用
import librosa
import matplotlib#不确定是否有用
import numpy as np
import music21
import tkinter as tk
from tkinter import filedialog
sys.path.append("C:/Users/qq328/AppData/Local/Programs/Python/Python312/Lib/site-packages")
# -*- coding:utf-8 -*-
import tkinter as tk

# 定义一个全局变量来存储文件路径
selected_file_path = ""

def open_file():
    # 使用filedialog.askopenfilename打开文件选择对话框
    file_path = filedialog.askopenfilename()
    # 检查用户是否选择了文件
    if file_path:
        # 更新标签以显示文件路径
        global selected_file_path  # 声明这是一个全局变量
        selected_file_path = file_path  # 存储文件路径
        file_label.config(text=file_path)
# 创建主窗口
root = tk.Tk()
# 设置窗口title
root.title('桃园')
root.geometry('450x450')
# root_window.iconbitmap('C:/Users/Administrator/Desktop/favicon.ico')
root["background"] = "DarkSlateBlue"
text = tk.Label(root, text="A MUSIC WORLD BELONGS TO YOU", bg="pink", fg="black", font=('Times',40, 'bold italic'))
text.pack()
# 创建第一个按钮
choose_button = tk.Button(root, text="choose a music file", bg="pink", fg="black",font=('Times', 30, 'bold italic'),command=open_file)
choose_button.pack(pady=150)  # 可以调整这个值来控制按钮的位置
# 创建第二个按钮
close_button = tk.Button(root, text="close", bg="pink", fg="black",font=('Times', 30, 'bold italic'),command=root.quit)
close_button.pack(pady=50)  # 这里的pady值决定了按钮与上面控件的距离
# 进入主循环，显示主窗口
root.mainloop()

def frequency_to_midi(frequency):#输入一个频率（Hz）输出对应的MIDI值
    p = music21.pitch.Pitch()
    p.frequency = frequency
    return p.midi
def aboutsecond(time):#输入识别出来的音符时间，输出一个音符（十六分音符四分音符什么的）的标准时间（单位为秒）
    if time>2.0 and time<=4.5:
       if time<=2.67:
            second = 2.0
       elif time>2.67 and time<=3.33:
            second = 3.0
       elif time>3.33:
            second = 4.0
    elif time>1.0 and time<=2.0:
        if time<=1.33:
            second = 1.0
        elif time>1.33 and time<=1.67:
            second = 1.5
        elif time>1.67:
            second = 2.0
    elif time>0.5 and time<=1.0:
        if time<=0.67:
            second = 0.5
        elif time>0.67 and time<=0.83:
            second = 0.75
        elif time>0.83:
            second = 1.0
    elif time>=0.20 and time<=0.5:
        if abs(time-0.25)>=abs(time-0.5):
            second = 0.25
        else:
            second = 0.5
   # elif time>4.5:
       # second = time%1
    else:
        second = 0.0
    return second
class audio:#提取音频的特征
    def __init__(self, input_file, sr=None, frame_len=512, n_fft=None, win_step=2 / 3, window="hamming"):
        """
        初始化
        :param input_file: 输入音频文件
        :param sr: 所输入音频文件的采样率，默认为None
        :param frame_len: 帧长，默认512个采样点(32ms,16kHz),与窗长相同
        :param n_fft: FFT窗口的长度，默认与窗长相同
        :param win_step: 窗移，默认移动2/3，512*2/3=341个采样点(21ms,16kHz)
        :param window: 窗类型，默认汉明窗
        """
        self.input_file = input_file
        self.frame_len = frame_len  # 帧长，单位采样点数
        self.wave_data, self.sr = librosa.load(self.input_file, sr=sr)
        self.window_len = frame_len  # 窗长512
        if n_fft is None:
            self.fft_num = self.window_len  # 设置NFFT点数与窗长相等
        else:
            self.fft_num = n_fft
        self.win_step = win_step
        self.hop_length = round(self.window_len * win_step)  # 重叠部分采样点数设置为窗长的1/3（1/3~1/2）,即帧移(窗移)2/3
        self.window = window

    def pitch(self, ts_mag=0.25):
        """
        获取每帧音高，即基频，这里应该包括基频和各次谐波，最小的为基频（一次谐波），其他的依次为二次、三次...谐波
        各次谐波等于基频的对应倍数，因此基频也等于各次谐波除以对应的次数，精确些等于所有谐波之和除以谐波次数之和
        :param ts_mag: 幅值倍乘因子阈值，>0，大于np.average(np.nonzero(magnitudes)) * ts_mag则认为对应的音高有效,默认0.25
        :return: 每帧基频及其对应峰的幅值(>0)，
                 np.ndarray[shape=(1 + n_fft/2，n_frames), dtype=float32]，（257，全部采样点数/(512*2/3)+1）

        usage:
        pitches, mags = self.pitch()  # 获取每帧基频
        f0_likely = []  # 可能的基频F0
        for i in range(pitches.shape[1]):  # 按列遍历非0最小值，作为每帧可能的F0
            try:
                f0_likely.append(np.min(pitches[np.nonzero(pitches[:, i]), i]))
            except ValueError:
                f0_likely.append(np.nan)  # 当一列，即一帧全为0时，赋值最小值为nan
        f0_all = np.array(f0_likely)
        """
        mag_spec = np.abs(librosa.stft(self.wave_data, n_fft=self.fft_num, hop_length=self.hop_length,
                                       win_length=self.frame_len, window=self.window))
        pitches, magnitudes = librosa.piptrack(S=mag_spec, sr=self.sr, threshold=1.0, ref=np.mean,
                                               fmin=26, fmax=4200)  # 人类正常说话基频最大可能范围50-500Hz
        ts = np.average(magnitudes[np.nonzero(magnitudes)]) * ts_mag
        pit_likely = pitches
        mag_likely = magnitudes
        pit_likely[magnitudes < ts] = 0
        mag_likely[magnitudes < ts] = 0
        return pit_likely, mag_likely

if __name__ == '__main__':
    audio_file =selected_file_path#导入音频
    self= audio(audio_file)#定义一个类
    #获取逐帧基频（就是声音频率）的过程，也是照着上面pitch函数里的用法抄的
    pitches, mags = self.pitch()  # 获取每帧基频
    f0_likely = []  # 可能的基频F0
    for i in range(pitches.shape[1]):  # 按列遍历非0最小值，作为每帧可能的F0
        try:
            f0_likely.append(np.min(pitches[np.nonzero(pitches[:, i]), i]))
        except ValueError:
            f0_likely.append(np.nan)  # 当一列，即一帧全为0时，赋值最小值为nan
            f0_all = np.array(f0_likely)
    #一帧持续时长0.032秒，见class里面_init_函数 “:param frame_len: 帧长，默认512个采样点(32ms,16kHz),与窗长相同”这行
    duration = 0.032
    #创建列表然后把每帧时长和频率打包放到PITCH_LIST里
    PITCH_LIST = []
    for PitcH in f0_all:
            PITCH_LIST.append((PitcH,duration))
            #print(PitcH)
    notes = []
    length = []
    #notes列表储存音符，给每个音符指定了MIDI值和时间，这里时间还是0.032秒
    for PitcH,DuratioN in PITCH_LIST:
        if np.isnan(PitcH):
           continue        #有影响估计也不会太大（根据最后结果来看）
        else:
            midi_note  =  frequency_to_midi(PitcH)#调用函数，频率转MIDI值
            note = music21.note.Note(midi = midi_note)#创建音符对象,用MIDI值确定它在五线谱上对应哪个音符
            note.duration = music21.duration.Duration(DuratioN)#定义出音符对象的时间
            notes.append(note)#存入列表
        #print(note.pitch.midi)#调试用来看MIDI值的，建议不要删
    #下面的大循环主要作用是把0.032秒一个的音符合并成时间长度
    #length列表存最终的音符对象，这里面的音符时间是最终谱子里显现的音符的时间
    k = 0
    for notE in notes:
        if k == 0:
          t = notE.pitch.midi#把这一帧的MIDI值记成这个音符的MIDI值，这里存在问题，如果第一个音符的MIDI值不准确（比如第一个音符被记成E，最后结果就是E，结果就会错）
          n = 1#用来存到底有几帧是这个音符
          k = 1#判断到底走哪个选择分支，和音频关系不大
          midi_list=[]# 每一个“打包”的midi值
          stop_list=[]# 用于中间取消判断
          time_list=[]# 记录midi值出现的次数
        else:
            if notE.pitch.midi <=t+1 and notE.pitch.midi >=t-1:#比如C的MIDI值是60，59到61之间都判断为C，提高容错率，但这个上下浮动为1的范围是我按前面数组返回的MIDI值凭感觉填的，并不具有科学性
                n+=1#把这帧时间加到当前音符时间里
                midi_list.append(notE.pitch.midi)# 把这帧时间对应的midi值加到空列表里

            else:#不在这个音符范围里面了，说明音符换了
                #print("如下")#调试用的
                #print(n)#调试用的
                #if(n<=2):#持续时间太短，可能是杂音啥的，把它忽略然后重新开始下一个音符的时间判定##把它改成2了，留有杂音的余地
                 # k = 0 #这个判断可能会有问题，比如某一段数组是FFFFEFFFF,本可以变成一个四分音符的F，我这么写就会变成两个八分音符的F
                #else:
                  w = aboutsecond(n*DuratioN)#n*DuratioN是记录的此音符对应时间，为了让时间更符合音符的标准时间用了这个函数（我不确定时间不标准究竟会不会报错，因为我看不懂它报错的意思）
                  #print(w)
                  if w == 0:#时间持续太短，同样忽略这个音符
                    k = 0
                  else:#和上面122行到125行一样的步骤
                      # 遍历列表，找到其中出现最多的midi值，以它作为这个“打包”好的音符的midi值
                      i = 0
                      stop_list.append(1)
                      for item in range(len(midi_list)):
                          if stop_list[i] == 1:
                              time_list.append(1)  # 记录该midi值出现次数
                              for other in range((i + 1), len(midi_list)):  # 遍历“打包”好的音符，统计该midi值总出现次数
                                  if other == midi_list[i]:
                                      time_list[i] += 1
                                      stop = 0
                                  else:
                                      stop = 1
                                  stop_list.append(stop)  # 如果在它之前出现过这个midi值，就不再统计它
                          i += 1
                      # 查找最大值的下标
                      max_time = time_list.index(max(time_list))
                      t = midi_list[max_time]

                      note = music21.note.Note(midi = t)
                      note.duration = music21.duration.Duration(w)
                      length.append(note)
                      k = 0
    if n>1:#防止最后一个音没被定义成音符
        note = music21.note.Note(midi = t)
        w = aboutsecond(n*DuratioN)
        if w != 0.0:
            note.duration = music21.duration.Duration(w)
            length.append(note)
   #下面这段也是调试用的
   # for s in length:
       # print("如下：")
       # print(s.pitch.midi)
       # print(s.duration)
    score = music21.stream.Stream()#创建一个流，类似于生成一个空白的谱子等你添加音符
    score.append(length)#把带音符的列表导入
    score.show()#显示这个谱子

#其他备注：这里的aboutsecond函数是默认四分音符一拍，每分钟60拍的音符对应的时常，四分音符1s，八分音符0.5s等，但其实到底哪个音符是一拍，一分钟有多少拍都是可以自定义的……
#这个知识点在以后更进一步的时候可能有用？简单来说就是一个音符对应是几秒其实是不确定的……
