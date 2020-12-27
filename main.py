#インポート群
import discord #基本
import os
from server import keep_alive
#import traceback
import time #Ping

#変数群
TOKEN = os.getenv("TOKEN") #トークン
prefix = 'o.' #Prefix
activity = discord.Streaming(name='o.help でヘルプ♪', url="https://www.twitch.tv/discord")
embed_help = discord.Embed(title="Aoi コマンドリスト",description="※現在は仮運用中です\no.neko…にゃーん\no.invite…このBotの招待リンクを表示するよ\no.ping…BotのPingを取得するよ\n\n（このBotは半自動です。たまに人が会話します）")
verifyed = ['HereBranch']

#接続に必要なオブジェクトを生成
client = discord.Client()

#起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('[Aoi] ログインしました')
    await client.change_presence(activity=activity)

#メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    #メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    GLOBAL_CH_NAME = "konoha-global" #グローバルチャットのチャンネル名
    GLOBAL_WEBHOOK_NAME = "konoha-global" #グローバルチャットのWebhook名
    if message.content == prefix + 'help':
        await message.channel.send(embed=embed_help)
        
    if message.channel.name == GLOBAL_CH_NAME:
        # kohoha-globalの名前をもつチャンネルに投稿されたので、メッセージを転送する
        await message.delete()

        channels = client.get_all_channels()
        global_channels = [ch for ch in channels if ch.name == GLOBAL_CH_NAME]

        for channel in global_channels:
            ch_webhooks = await channel.webhooks()
            webhook = discord.utils.get(ch_webhooks, name=GLOBAL_WEBHOOK_NAME)

            if webhook is None:
                # そのチャンネルに konoha-global というWebhookは無かったので無視
                continue
            if message.author.name in verifyed:
                if message.author.name == 'HereBranch':
                    if message.author.discriminator == '5679':
                        global_authorname = message.author.name + '#' + message.author.discriminator + ' ✅♾'
                    else:
                        global_authorname = message.author.name + '#' + message.author.discriminator + ' ✅'
                else:
                    global_authorname = message.author.name + '#' + message.author.discriminator + ' ✅'
            else:
                global_authorname = message.author.name + '#' + message.author.discriminator
            await webhook.send(content=message.content,
                username=global_authorname,
                avatar_url=message.author.avatar_url_as(format="png"))
        
    #にゃーん
    if message.content == prefix + 'neko':
        await message.channel.send('にゃーん')
        
    #Botの招待リンク表示
    if message.content == prefix + 'invite':
        await message.channel.send('**AoiBot招待リンク**:\nhttps://www.herebots.ml/aoi')

    #Ping
    if message.content == prefix + 'ping':
       time_then = time.monotonic()
       ping_send = await message.channel.send('__*`Pingを取得中...`*__')
       ping = '%.2f' % (1000*(time.monotonic()-time_then))
       await ping_send.edit(content='**Ping: **' + ping + 'ms')
        
# repl.it接続
keep_alive()

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)