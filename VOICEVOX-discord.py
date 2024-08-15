import discord
import requests
import tempfile
import os
import json

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
    print("起動しました。")


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
    await ctx.respond('追加しました')


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


bot.run(Token)