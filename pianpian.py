import streamlit as st
import librosa
import math
def numbertonote(num):
  notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
  half_off = num - 1 + 9
  octave = half_off // 12
  note_index = half_off % 12
  return f"{notes[note_index]}{octave}"
def keysbetween(lower,higher):
  global offval
  sharpflat = {"#":1, "b":-1," ":0}
  a = lower
  b = higher
  if len(a)>=3: a_note = [a[0],a[1],a[2:]]
  else: a_note = [a[0]," ",a[1:]]
  if len(b)>=3: b_note = [b[0],b[1],b[2:]]
  else: b_note = [b[0]," ",b[1:]]
  a_val = 12*int(a_note[2]) + offval[a_note[0]] + sharpflat[a_note[1]]
  b_val = 12*int(b_note[2]) + offval[b_note[0]] + sharpflat[b_note[1]]
  return b_val-a_val

def precision():
    keys = st.session_state["keys"]
    score = st.session_state["score"]
    wrong = st.session_state["wrong"]
    for i in range(1, 89):
        score[i] = None
    for i in range(1, 89):
        if keys[i] is None:
            continue
        if not halfuse and "#" in numbertonote(i):
            continue
        errors = []
        for j in range(1, 89):
            if i == j or keys[j] is None:
                continue
            if not halfuse and "#" in numbertonote(j):
                continue
            a = keys[i] / keys[j]
            r = 2 ** ((i - j) / 12)
            w = a/r
            wrong[i][j] = w
            if w > 0 and math.isfinite(w):
                e = abs(CUSTARD * math.log2(w))
                errors.append(e)
        if errors:
            ave = sum(errors) / len(errors)
            # 오차!!!!!!!!!
            score[i] = 100 * math.exp(-ave / WHIP)
        else: score[i] = None

def setscore(num):
    log_scr = float(0)
    for i in range(1, 89):
        if not st.session_state["keys"][i]:
            continue
        if num == i:
            continue
        w = st.session_state["wrong"][num][i]
        if w <= 0 or not math.isfinite(w):
            continue
        log_scr += abs(math.log(w))
    if log_scr > 700:
        st.session_state["score"][num] = float("inf")
    else:
        st.session_state["score"][num] = math.exp(log_scr)
def process_mp3(uploaded_file):
    y, sr = librosa.load(
            uploaded_file,
            sr=None,
            mono=True
    )
    filename = uploaded_file.name
    if not filename[-4:] == (".mp3"):
        st.warning("mp3가 아닙니다")
        return
    keyname = filename[:-4]
    position =  keysbetween("A0", keyname) + 1
    f0, voiced_flag, voiced_prob = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("A0"),
        fmax=librosa.note_to_hz("C8")
    )
    f0_valid = [
        float(x)
        for x in f0
        if not math.isnan(float(x))
    ]
    av = (
        sum(f0_valid) / len(f0_valid)
    )
    st.session_state["keys"][position] = av
    '''st.success(
        f"{filename} → "
        f"{keyname} → "
        f"{average_frequency:.4f} Hz → "
        f"keys[{position}]"
    )'''

def dataget():
  global keys, keyname,keyuploader
  y, sr = librosa.load(keyuploader, sr=None)
  f0, flag,trash2 = librosa.pyin(
    y,
    fmin=librosa.note_to_hz("A0"),  
    fmax=librosa.note_to_hz("C8")
  )
  f0 = [x for x in f0 if x == x]
  
  if len(f0) != 0: keys[keysbetween("A0",keyname)+1] = sum(f0)/len(f0)
  else: keys[keysbetween("A0",keyname+1)] = None
  print(f"데이터 업로드됨: {keyname}, 위치: {keysbetween("A0",keyname)+1}, 값: {sum(f0)/len(f0)}, 디버그-길이: {sum(f0)}/{len(f0)}, 디버그-리스트: {f0}")
def finalcalc():
    precision()
    for i in range(1, 89):
        if st.session_state["score"][i] is not None:
            print(
                f"{numbertonote(i)}: "
                f"{st.session_state['score'][i]}"
            )
if "init" not in st.session_state:
  
  keys = [None]*89
  score = [1]*89  
  wrong = [[0]*89]*89
  # 여러 번 반복하고 틀린것마다 배수를 부여해 계산!
  #has_no_half = {"C":False,"D":False,"E":False,"F":True,"G":False,"A":False,"B":True}
  
else:
  keys = st.session_state["keys"]
  score = st.session_state["score"]
  wrong = st.session_state["wrong"]
  
REPEAT = 5
CREAM = 100
WHIP = 50
CUSTARD = 1200
offval = {"C":1,"D":3,"E":5,"F":6,"G":8,"A":10,"B":12}
resetvalue_ = 0
multiplier = 1+(2*(1/12))
halfuse = st.toggle("반음 사용")
keyname = st.text_input("어떤 음계에 대한 파일인가요? (예: C#5)")
uploaded_files = st.file_uploader(
    "MP3 파일들을 선택하세요.",
    type=["mp3"],
    accept_multiple_files=True
)
#upload = st.button("데이터 업로드(OLD)")
if st.button("모든 MP3 데이터 업로드"):
    if not uploaded_files:
        st.error(
            "MP3 파일을 하나 이상 선택해주세요."
        )
    else:
      for uploaded_file in uploaded_files:
        process_mp3(uploaded_file)
debugprintkeys = st.button("디버그: keys")
if st.button("최종 결과,,"): finalcalc()
if debugprintkeys: print(keys)
#if upload: dataget()
if "init" not in st.session_state:
    st.session_state["init"] = True
st.session_state["keys"] = keys
st.session_state["score"] = score
st.session_state["wrong"] = wrong
