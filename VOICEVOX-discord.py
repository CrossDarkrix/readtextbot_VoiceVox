import discord
import requests
import tempfile
import threading
import time
import os
import json
try:
    import console
except:
    console = None

Token = ''
if not os.path.exists('dic_text.json'):
    with open('dic_text.json', 'w', encoding='utf-8') as f:
        f.write('{"dic": {"text_0": "ZUNDAMON", "read_text_0": "ずんだもん"}}')
    dic = {"dic": {"text_0": 'ZUNDAMON', "read_text_0": "ずんだもん"}}
else:
    try:
        dic = json.load(open('dic_text.json', 'r', encoding='utf-8'))
    except:
        dic = {"dic": {"text_0": "ZUNDAMON", "read_text_0": "ずんだもん"}}

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True
bot = discord.Bot(intents=intents)
voice_client = None
text_channel = None

def post_audio_query(text: str, speaker: int):
    URL = "http://127.0.0.1:50021/audio_query"
    Parameters = {
        "text": text,
        "speaker": speaker
    }

    response = requests.post(URL, params=Parameters)

    return response.json()


def post_synthesis(json: dict, speaker: int):
    URL = "http://127.0.0.1:50021/synthesis"

    Parameters = {
        "speaker": speaker
    }
    response = requests.post(URL, json=json, params=Parameters )

    return response.content


def save_tempfile(text: str, speaker: int):
    for i in range(len(dic['dic'])):
        try:
            if dic['dic']['text_{}'.format(i)] in text:
                text = text.replace(dic['dic']['text_{}'.format(i)], dic['dic']['read_text_{}'.format(i)])
        except:
            break
    json = post_audio_query(text, speaker)
    data = post_synthesis(json, speaker)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wf:
        wf.write(data)
        wf.close()

        path = wf.name

    return path


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('BOTが正常に起動したのだ(v1.0)'))


@bot.event
async def on_message(message):
    if message.author.bot == True:
        return
    global text_channel
    global voice_client
    channel = message.channel
    if not text_channel == channel:
        return
    path = save_tempfile(message.content, 1)
    voice_client.play(discord.FFmpegPCMAudio(path))


@bot.slash_command(description='ボイスチャンネルに接続します。')
async def join(ctx):
    global voice_client
    global text_channel
    user = ctx.author

    if not user.voice:
        await ctx.respond("ボイスチャンネルに接続していません。")
        return
    await ctx.respond("ボイスチャンネルに接続しました。")
    text_channel = ctx.channel
    voice_channel = user.voice.channel
    voice_client = await voice_channel.connect()
    path = save_tempfile("接続しました", 1)
    voice_client.play(discord.FFmpegPCMAudio(path))


@bot.slash_command(description='ボイスチャンネルの接続を解除します。')
async def left(ctx):
    global voice_client
    global text_channel
    if not voice_client:
        await ctx.respond("ボイスチャンネルに接続していません。")
        return
    await ctx.respond("切断しました。")
    await voice_client.disconnect()
    voice_client = None
    text_channel = None


@bot.slash_command(description='単語を単語辞書に追加します')
async def adddic(ctx, text, read_text):
    global dic
    for i in range(len(dic['dic'])):
        try:
            dic['dic']['text_{}'.format(i)]
        except:
            dic['dic'].update([("text_{}".format(i), text), ("read_text_{}".format(i), read_text)])
            break

    with open('dic_text.json', 'w', encoding='utf-8') as ff:
        try:
            ff.write(str(dic).replace("'", '"'))
        except:
            pass
    await ctx.respond('{}を{}という読み方にして追加しました'.format(text, read_text))


@bot.slash_command(description='単語辞書から単語を削除します(元の単語を指定してください)')
async def deldic(ctx, text):
    global dic
    error = 0
    for i in range(len(dic['dic'])):
        try:
            if dic['dic']['text_{}'.format(i)] == text:
                try:
                    del dic['dic']['text_{}'.format(i)], dic['dic']['read_text_{}'.format(i)]
                except:
                    pass
                break
        except:
            error = 1
            break
    with open('dic_text.json', 'w', encoding='utf-8') as ff:
        try:
            ff.write(str(dic).replace("'", '"'))
        except:
            pass
    if error == 1:
        await ctx.respond("単語が見つかりませんでした。")
    else:
        await ctx.respond("単語を削除しました。")


@bot.slash_command(description='単語辞書を出力します')
async def showdic(ctx):
    text = []
    for i in range(len(dic['dic']) - 1):
        try:
            text.append('元の単語: {}, 読み方: {}'.format(dic['dic']['text_{}'.format(i)], dic['dic']['read_text_{}'.format(i)]))
        except:
            pass
    await ctx.respond('\n'.join(text))


def TimeCount():
    Uptimeloop = [0]
    def TimeCounter():
        Year = 0
        Week = 0
        Day = 0
        Hour = 0
        Minute = 0
        Sec = 0
        for i in Uptimeloop:
            if Sec == 59:
                Sec = 0
                Minute += 1
            else:
                Sec += 1
            if Minute == 59:
                Minute = 0
                Hour += 1
            if Hour == 24:
                Hour = 0
                Day += 1
            if Day == 7:
                Day = 0
                Week += 1
            if Week == 13:
                Week = 0
                Year += 1
            if Year <= 9:
                SYear = '0{}'.format(Year)
            else:
                SYear = '{}'.format(Year)
            if Week <= 9:
                SWeek = '0{}'.format(Week)
            else:
                SWeek = '{}'.format(Week)
            if Day <= 9:
                SDay = '0{}'.format(Day)
            else:
                SDay = '{}'.format(Day)
            if Hour <= 9:
                SHour = '0{}'.format(Hour)
            else:
                SHour = '{}'.format(Hour)
            if Minute <= 9:
                SMinute = '0{}'.format(Minute)
            else:
                SMinute = '{}'.format(Minute)
            if Sec <= 9:
                SSec = '0{}'.format(Sec)
            else:
                SSec = '{}'.format(Sec)
            if not console == None:
                console.clear()
                print('稼働時間: {}年, {}週間, {}日, {}:{}:{}'.format(SYear, SWeek, SDay, SHour, SMinute, SSec))
            else:
                print('稼働時間: {}年, {}週間, {}日, {}:{}:{}'.format(SYear, SWeek, SDay, SHour, SMinute, SSec), end='\r', flush=True)
            time.sleep(1)
            Uptimeloop.append(i+1)
    threading.Thread(target=TimeCounter, daemon=True).start()


def main():
    TimeCount()
    bot.run(Token)


if __name__ == '__main__':
    try:
        main()
    except OSError:
        pass