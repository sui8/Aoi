#インポート群
import discord #基本
import os
from server import keep_alive
from data.vips import verifyed, moderators, OWNER_ID
from data.stickers import stickers
import re #正規表現
import asyncio #タイマー
import datetime #日時取得
import json #jsonファイル読み込み
import pya3rt #Talk API

#変数群
TOKEN = os.getenv("TOKEN") #トークン
prefix = 'o.' #Prefix
Verifymode = 0
ICON = os.getenv("ICON") #AoiアイコンURL
STICKER_URL = os.getenv("STICKER_URL") #ステッカー保管場所URL
TALKAPI_KEY = os.getenv("TALKAPI_KEY") #Talk API Key

#Embed群
embed_help = discord.Embed(title="Aoi コマンドリスト",description="o.invite…このBotの招待リンクを表示するよ\no.join…このコマンドを実行したチャンネルをグローバルチャットにするよ\no.verify…グローバルチャットアカウント認証申請をするよ\no.gban <ユーザーID>…グローバルチャットBANを実行するよ（Aoi モデレーターのみ）\no.gbanlist…グローバルチャットBANリストを表示するよ\no.gbaninfo <ユーザーID>ユーザーのグローバルチャットBANに関する情報を確認できるよ\no.globallist…グローバルチャットに接続中のサーバー一覧を表示するよ\n\n（グローバルチャットを解除する場合は、そのチャンネルを削除してください）\n'aoi-talk'というチャンネルを作って話しかけてみよう！")
embed_verify_help = discord.Embed(title='グローバル認証制度について',description="準備中")
lettersover = discord.Embed(title="文字数制限超過",description="未認証ユーザーによる文字数制限超過の為、200文字を超える投稿は遮断されました。",color=0xff0000)

#メンバーインテント
intents = discord.Intents.default()
intents.members = True

#接続に必要なオブジェクトを生成
client = discord.Client(intents=intents)

#GBANリスト読み込み
with open('data/gbans.json', encoding='utf-8') as f:
    gbans = json.load(f)

#グローバルチャットリスト読み込み
with open('data/globals.json', encoding='utf-8') as f:
    globals = json.load(f)

#グローバルチャットBAN時のテンプレート
gban_template = {"reason" : "", "enforcer" : "", "datetime" : ""}
#グローバルチャット参加時のテンプレート
global_template = {"channel" : "", "enforcer" : "", "datetime" : ""}

#グローバルチャットNGワード
global_ng = [prefix + "invite", prefix + "join", prefix + "verify", prefix + "gbanlist", prefix + "help"]

#Prefix文字列化
prefix = str(prefix)



#起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('[Aoi] ログインしました')
    bot_guilds = len(client.guilds)
    activity = discord.Streaming(name='o.help でヘルプ | ' + str(bot_guilds) + ' Guilds ', url="https://www.twitch.tv/discord")
    await client.change_presence(activity=activity)
    #起動メッセージをHereBots Hubに送信（チャンネルが存在しない場合、スルー）
    try:
      ready_log = client.get_channel(800380094375264318)
      embed = discord.Embed(title="Aoi 起動完了",description="**Aoi#3869** が起動しました。\nサーバー数: " + str(bot_guilds), timestamp=datetime.datetime.now())
      embed.set_footer(text="Aoi",icon_url=ICON)
      await ready_log.send(embed=embed)
    except:
      pass

  
#Talk API
def talkapi(message):
  talkclient = pya3rt.TalkClient(TALKAPI_KEY)
  talk_reply = talkclient.talk(message)
  return talk_reply['results'][0]['reply']



#メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    global gbans, gban_template, global_ng, globals, global_template
    #メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
      return

    #DMの場合無視する
    if isinstance(message.channel, discord.channel.DMChannel):
      return

    #Talk API
    if message.channel.name == "aoi-talk":
      talk_message_reply = talkapi(message.content)
      await message.channel.send(talk_message_reply)

    GLOBAL_CH_NAME = "aoi-global" #グローバルチャットのチャンネル名
    GLOBAL_WEBHOOK_NAME = "AoiGlobal" #グローバルチャットのWebhook名
    if message.content == prefix + 'help':
        await message.channel.send(embed=embed_help)

    #認証ヘルプ
    if message.content == prefix + 'verify-help':
      await message.channel.send(embed=embed_verify_help)

    #登録
    if message.content == prefix + 'join':
      #もし既にAoiGlobalがあれば、拒否する（但し、名前で判断しているのでそこが難点）
      webhook_there = discord.utils.get(await message.channel.webhooks(), name=GLOBAL_WEBHOOK_NAME)
      #サーバーIDの取得
      global_tmp = message.guild.id
      #グローバルチャットリスト読み込み
      with open('data/globals.json', encoding='utf-8') as f:
          globals = json.load(f)

      if not webhook_there is None:
        embed = discord.Embed(title=":x: エラー",description="既にこのサーバーはグローバルチャットに登録されています。",color=0xff0000)
        await message.channel.send(embed=embed)

      else:
        if str(global_tmp) in globals:
          embed = discord.Embed(title=":x: エラー",description="既にこのサーバーはグローバルチャットに登録されています。",color=0xff0000)
          await message.channel.send(embed=embed)
        else:
          try:
            await message.channel.create_webhook(name=GLOBAL_WEBHOOK_NAME)
            await message.channel.edit(name=GLOBAL_CH_NAME)
            embed = discord.Embed(title=":white_check_mark: 成功",description="グローバルチャットへの登録に成功しました。チャンネル名は変更しないで下さい。（グローバルチャットを解除する場合は、当チャンネルを削除してください）",color=0x00ff00)
            await message.channel.send(embed=embed)

            #送信元特定
            global_msg_from = discord.utils.get(await message.channel.webhooks(), name=GLOBAL_WEBHOOK_NAME)
            #余計なパーツ除去
            global_msg_from = str(global_msg_from)
            global_msg_from = re.sub(r"\D", "", global_msg_from)
            global_msg_from = int(global_msg_from)

            channels = client.get_all_channels()
            global_join_from = message.guild.name
            global_channels = [ch for ch in channels if ch.name == GLOBAL_CH_NAME]
            embed = discord.Embed(title=':white_check_mark: 参加',description="**" + global_join_from + "**がグローバルチャットに参加しました。",color=0x00ffff, timestamp=datetime.datetime.now())

            #ギルドのアイコン取得
            global_join_from_icon = message.guild.icon_url_as(static_format='png')

            if len(global_join_from_icon) == 0:
              global_join_from_icon = "https://cdn.discordapp.com/embed/avatars/0.png"

            embed.set_thumbnail(url=global_join_from_icon)

            #JSONでBAN記録書き込み＆データうめ
            globals[int(global_tmp)] = global_template
            globals[int(global_tmp)]["channel"] = message.channel.id
            globals[int(global_tmp)]["enforcer"] = message.author.id
            datetime_now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
            globals[int(global_tmp)]["datetime"] = datetime_now_jst.strftime('%Y/%m/%d %H:%M:%S') + ' (JST)'

            #JSONに書き込み
            with open('data/globals.json', mode='w') as f:
              json.dump(globals, f, indent=4)
            
            #合計接続数
            global_join_total = str(len(globals))
            embed.set_footer(text="現在接続中のサーバーは " + global_join_total + " サーバーです。")

            for channel in global_channels:
              ch_webhooks = await channel.webhooks()
              webhook = discord.utils.get(ch_webhooks, name=GLOBAL_WEBHOOK_NAME)
              ch_id = webhook.id
                
              if webhook is None:
                # そのチャンネルに global というWebhookは無かったので無視
                continue

              #送信元はスキップ
              if ch_id == global_msg_from:
                continue

              #Aoi設定
              await webhook.send(username="Aoi ✅🤖",
                avatar_url=ICON, embed=embed)


          except:
            await message.channel.send('**エラーが発生しました。**\nチャンネルの全権限がAoiにある事を確認してください。')

    '''
    #解除
    if message.content == prefix + 'leave':
      await discord.Webhook.delete(self=GLOBAL_CH_NAME, reason='AoiGlobal解除')
      embed = discord.Embed(title=":white_check_mark: 成功",description="グローバルチャットへの登録を解除しました。チャンネル名は変更しても問題ありません。",color=0xff0000)
      await message.channel.send(embed=embed)
      await message.channel.send('**エラーが発生しました。**\n該当するチャンネルで正しく実行できているか確認してください。')
    '''

    #グローバルBAN
    if message.content.split(' ')[0] == prefix + "gban":
      if message.author.id == OWNER_ID:
        gban_tmp = str(message.content)
        gban_tmp = gban_tmp.split(' ')
        try:
          gban_tmp = gban_tmp[1]
          gban_tmp = int(gban_tmp)
        except:
          embed = discord.Embed(title=":x: エラー",description="コマンドが不正です。引数が正しく設定されているか確認して下さい。\n使い方: " + prefix + "gban <ユーザーID>",color=0xff0000)
          await message.channel.send(embed=embed)
        
        else:
          try:
            gban_name = await client.fetch_user(int(gban_tmp))
          except:
            embed = discord.Embed(title=":x: エラー",description="存在しないユーザーです。",color=0xff0000)
            await message.channel.send(embed=embed)

          else:
            #JSONでBAN記録読み込み
            with open('data/gbans.json', mode='r',encoding='utf-8') as f:
              gbans = json.load(f)
            
            #既にBANされているか
            if str(gban_tmp) in gbans:
              embed = discord.Embed(title=":x: エラー",description="そのユーザーは既にグローバルチャットBANされています。",color=0xff0000)
              await message.channel.send(embed=embed)

            #されていなければ実行
            else:
              #JSONでBAN記録書き込み＆データうめ
              gbans[int(gban_tmp)] = gban_template
              gbans[int(gban_tmp)]["reason"] = ""
              gbans[int(gban_tmp)]["enforcer"] = message.author.id
              datetime_now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
              gbans[int(gban_tmp)]["datetime"] = datetime_now_jst.strftime('%Y/%m/%d %H:%M:%S') + ' (JST)'

              #JSONに書き込み
              with open('data/gbans.json', mode='w') as f:
                json.dump(gbans, f, indent=4)

              #if message.author.id == OWNER_ID:
              #  
              embed = discord.Embed(title="グローバルチャットBAN",description="**" + str(gban_name) + "** [ID:" + str(gban_tmp) + "] " + "がグローバルチャットBANされました。", color=0xff0000, timestamp=datetime.datetime.now())
              embed.set_footer(text="実行者: " + str(message.author), icon_url=message.author.avatar_url_as(format="png"))
              gban_log = client.get_channel(800380075861213234)
              await gban_log.send(embed=embed)
              embed = discord.Embed(title=":white_check_mark: 成功",description="グローバルBANが正常に実行されました。\n**" + str(gban_name) + "** [ID:" + str(gban_tmp) + "] ",color=0x00ff00, timestamp=datetime.datetime.now())
              embed.set_footer(text="実行者: " + str(message.author), icon_url=message.author.avatar_url_as(format="png"))
              await message.channel.send(embed=embed)

      elif message.author.id in moderators:
        gban_tmp = str(message.content)
        gban_tmp = gban_tmp.split(' ')
        try:
          gban_tmp = gban_tmp[1]
          gban_tmp = int(gban_tmp)
        except:
          embed = discord.Embed(title=":x: エラー",description="コマンドが不正です。引数が正しく設定されているか確認して下さい。",color=0xff0000)
          await message.channel.send(embed=embed)
        
        else:
          try:
            gban_name = await client.fetch_user(int(gban_tmp))
          except:
            embed = discord.Embed(title=":x: エラー",description="存在しないユーザーです。",color=0xff0000)
            await message.channel.send(embed=embed)

          else:
            #JSONでBAN記録読み込み
            with open('data/gbans.json', mode='r',encoding='utf-8') as f:
              gbans = json.load(f)
            
            #既にBANされているか
            if gban_tmp in list(gbans.keys()):
              embed = discord.Embed(title=":x: エラー",description="そのユーザーは既にグローバルチャットBANされています。",color=0xff0000)
              await message.channel.send(embed=embed)

            #されていなければ実行
            else:
              #JSONでBAN記録書き込み＆データうめ
              gbans[int(gban_tmp)] = gban_template
              gbans[int(gban_tmp)]["reason"] = ""
              gbans[int(gban_tmp)]["enforcer"] = message.author.id
              datetime_now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
              gbans[int(gban_tmp)]["datetime"] = datetime_now_jst.strftime('%Y/%m/%d %H:%M:%S') + ' (JST)'

              #JSONに書き込み
              with open('data/gbans.json', mode='w') as f:
                json.dump(gbans, f, indent=4)

              embed = discord.Embed(title="グローバルチャットBAN",description="**" + str(gban_name) + "** [ID:" + str(gban_tmp) + "] " + "がグローバルチャットBANされました。", color=0x00ff00, timestamp=datetime.datetime.now())
              embed.set_footer(text="実行者: " + str(message.author), icon_url=message.author.avatar_url_as(format="png"))
              gban_log = client.get_channel(800380075861213234)
              await gban_log.send(embed=embed)
              embed = discord.Embed(title=":white_check_mark: 成功",description="グローバルチャットBANが正常に実行されました。\n**" + str(gban_name) + "** [ID:" + str(gban_tmp) + "] ",color=0x00ff00, timestamp=datetime.datetime.now())
              embed.set_footer(text="実行者: " + str(message.author), icon_url=message.author.avatar_url_as(format="png"))
              await message.channel.send(embed=embed)

    #グローバルBAN解除
    if message.content.split(' ')[0] == prefix + "ungban":
      if message.author.id == OWNER_ID:
        ungban_tmp = str(message.content)
        ungban_tmp = ungban_tmp.split(' ')

        #引数が正しく設定されているか
        try:
          ungban_tmp = ungban_tmp[1]
          ungban_tmp = int(ungban_tmp)
        except:
          embed = discord.Embed(title=":x: エラー",description="コマンドが不正です。引数が正しく設定されているか確認して下さい。",color=0xff0000)
          await message.channel.send(embed=embed)
        
        #引数として与えられたユーザーは存在するのか（Deleted User判別）
        else:
          try:
            ungban_name = await client.fetch_user(int(ungban_tmp))
          except:
            embed = discord.Embed(title=":x: エラー",description="存在しないユーザーです。",color=0xff0000)
            await message.channel.send(embed=embed)

          else:
            #JSONでBAN記録読み込み
            with open('data/gbans.json', mode='r',encoding='utf-8') as f:
              gbans = json.load(f)
            
            #BANされていないか
            if not str(ungban_tmp) in gbans:
              embed = discord.Embed(title=":x: エラー",description="そのユーザーはグローバルチャットBANされていません。",color=0xff0000)
              await message.channel.send(embed=embed)

            #されていれば実行
            else:
              #JSONでBAN記録削除
              del gbans[str(ungban_tmp)]

              #JSONに書き込み（更新）
              with open('data/gbans.json', mode='w') as f:
                json.dump(gbans, f, indent=4)

              #成功通知
              embed = discord.Embed(title="グローバルチャットBAN解除",description="**" + str(ungban_name) + "** [ID:" + str(ungban_tmp) + "] " + "がグローバルチャットBAN解除されました。", color=0x00ff00, timestamp=datetime.datetime.now())
              embed.set_footer(text="実行者: " + str(message.author), icon_url=message.author.avatar_url_as(format="png"))
              gban_log = client.get_channel(800380075861213234)
              await gban_log.send(embed=embed)
              embed = discord.Embed(title=":white_check_mark: 成功",description="グローバルチャットBAN解除が正常に実行されました。\n**" + str(ungban_name) + "** [ID:" + str(ungban_tmp) + "] ",color=0x00ff00, timestamp=datetime.datetime.now())
              embed.set_footer(text="実行者: " + str(message.author), icon_url=message.author.avatar_url_as(format="png"))
              await message.channel.send(embed=embed)

      elif message.author.id in moderators:
        ungban_tmp = str(message.content)
        ungban_tmp = ungban_tmp.split(' ')

        #引数が正しく設定されているか
        try:
          ungban_tmp = ungban_tmp[1]
          ungban_tmp = int(ungban_tmp)
        except:
          embed = discord.Embed(title=":x: エラー",description="コマンドが不正です。引数が正しく設定されているか確認して下さい。",color=0xff0000)
          await message.channel.send(embed=embed)
        
        #引数として与えられたユーザーは存在するのか（Deleted User判別）
        else:
          try:
            ungban_name = await client.fetch_user(int(ungban_tmp))
          except:
            embed = discord.Embed(title=":x: エラー",description="存在しないユーザーです。",color=0xff0000)
            await message.channel.send(embed=embed)

          else:
            #JSONでBAN記録読み込み
            with open('data/gbans.json', mode='r',encoding='utf-8') as f:
              gbans = json.load(f)
            
            #BANされていないか
            if not str(ungban_tmp) in gbans:
              embed = discord.Embed(title=":x: エラー",description="そのユーザーはグローバルチャットBANされていません。",color=0xff0000)
              await message.channel.send(embed=embed)

            #されていれば実行
            else:
              #JSONでBAN記録削除
              del gbans[str(ungban_tmp)]

              #JSONに書き込み（更新）
              with open('data/gbans.json', mode='w') as f:
                json.dump(gbans, f, indent=4)

              #成功通知
              embed = discord.Embed(title="グローバルチャットBAN解除",description="**" + str(ungban_name) + "** [ID:" + str(ungban_tmp) + "] " + "がグローバルチャットBAN解除されました。", color=0x00ff00, timestamp=datetime.datetime.now())
              embed.set_footer(text="実行者: " + str(message.author), icon_url=message.author.avatar_url_as(format="png"))
              gban_log = client.get_channel(800380075861213234)
              await gban_log.send(embed=embed)
              embed = discord.Embed(title=":white_check_mark: 成功",description="グローバルチャットBAN解除が正常に実行されました。\n**" + str(ungban_name) + "** [ID:" + str(gban_tmp) + "] ",color=0x00ff00, timestamp=datetime.datetime.now())
              embed.set_footer(text="実行者: " + str(message.author), icon_url=message.author.avatar_url_as(format="png"))
              await message.channel.send(embed=embed)

    #グローバルBANリスト
    if message.content == prefix + "gbanlist":
      with open('data/gbans.json', mode='r', encoding='utf-8') as f:
        gbans = json.load(f)

      gbans_keys = list(gbans.keys())
      gbans_len = len(gbans)
      gban_userlist = ""

      for i in gbans_keys:
        try:
          gban_userinfo = client.get_user(int(i))
        except:
          gban_userinfo = "Unknown User"

        gban_userlist = gban_userlist + "・**" + str(gban_userinfo) + "** [ID:" + str(i) + "]\n"

      embed = discord.Embed(title="グローバルチャットBANリスト",description=gban_userlist + "BAN者合計:** " + str(gbans_len) + "**人")
      await message.channel.send(embed=embed)

    #グローバルチャットBANユーザー情報取得
    if message.content.split(' ')[0] == prefix + "gbaninfo":
      gbaninfo_tmp = str(message.content)
      gbaninfo_tmp = gbaninfo_tmp.split(' ')

      #引数が正しく設定されているか
      try:
        gbaninfo_tmp = gbaninfo_tmp[1]
        gbaninfo_tmp = int(gbaninfo_tmp)
      except:
        embed = discord.Embed(title=":x: エラー",description="コマンドが不正です。引数が正しく設定されているか確認して下さい。",color=0xff0000)
        await message.channel.send(embed=embed)
      
      #引数として与えられたユーザーは存在するのか（Deleted User判別）
      else:
        try:
          gbaninfo_name = await client.fetch_user(int(gbaninfo_tmp))
        except:
          embed = discord.Embed(title=":x: エラー",description="存在しないユーザーです。",color=0xff0000)
          await message.channel.send(embed=embed)

        else:
          #JSONでBAN記録読み込み
          with open('data/gbans.json', mode='r',encoding='utf-8') as f:
            gbans = json.load(f)
          
          #BANされていないか
          if not str(gbaninfo_tmp) in gbans:
            embed = discord.Embed(title=":x: エラー",description="そのユーザーはグローバルチャットBANされていません。",color=0xff0000)
            await message.channel.send(embed=embed)

          #されていれば情報収集
          else:
            #JSONでBAN記録削除
            gbaninfo_reason = gbans[str(gbaninfo_tmp)]["reason"]
            print(gbaninfo_reason)
            gbaninfo_enforcer = gbans[str(gbaninfo_tmp)]["enforcer"]
            gbaninfo_datetime = gbans[str(gbaninfo_tmp)]["datetime"]

            #実行者は存在するか
            try:
              gbaninfo_enforcer_name = await client.fetch_user(int(gbaninfo_enforcer))
            except:
              gbaninfo_enforcer_name = "Deleted User"

            #理由はあるか
            if len(gbaninfo_reason) == 0:
              gbaninfo_reason = "理由が入力されていません"

            embed = discord.Embed(title="グローバルチャットBAN情報",description="")
            embed.add_field(name="ユーザー名", value=str(gbaninfo_name) + " [ID:" + str(gbaninfo_tmp) + "]", inline=False)
            embed.add_field(name="理由", value=str(gbaninfo_reason), inline=False)
            embed.add_field(name="実行者", value=str(gbaninfo_enforcer_name) + " [ID:" + str(gbaninfo_enforcer) + "]", inline=True)
            embed.add_field(name="実行日時", value=str(gbaninfo_datetime), inline=True)
            #embed.set_thumbnail(url=message.author.avatar_url_as(format="png"))
            await message.channel.send(embed=embed)

    #グローバルチャットサーバーリスト
    if message.content == prefix + "globallist":
      with open('data/globals.json', mode='r', encoding='utf-8') as f:
        globals = json.load(f)

      globals_keys = list(globals.keys())
      globals_len = len(globals)
      global_guildlist = ""

      for i in globals_keys:
        try:
          global_guildinfo = client.get_guild(int(i))
        except:
          global_guildinfo = "Deleted Server"
          #globals_len = globals_len - 1

        global_guildlist = global_guildlist + "・**" + str(global_guildinfo) + "**\n"

      embed = discord.Embed(title="グローバルチャット接続中サーバーリスト",description=global_guildlist + "接続中サーバー合計:** " + str(globals_len) + "**サーバー")
      await message.channel.send(embed=embed)


    #先にDM対策必須
    #AoiGlobalのWebhookを探す   
    webhook_there = discord.utils.get(await message.channel.webhooks(), name=GLOBAL_WEBHOOK_NAME)
    webhook_there = str(webhook_there)
 
    #グローバルチャット
    #先述のAoiGlobalがあるかないか
    if webhook_there != 'None':
      # globalの名前をもつチャンネルに投稿されたので、メッセージを転送する
      #if message.content == null:
      #  pass

      #コマンドだけ除外（リスト化しておけば後で使えるかも...）
      if not message.content in global_ng:
        #if message.content != prefix + "join" or prefix + "help" or prefix + "gban" or prefix + "verify-help":

        #GBANリスト読み込み
        with open('data/gbans.json', mode='r', encoding='utf-8') as f:
          gbans = json.load(f)

        #GBAN者は遮断
        if str(message.author.id) in gbans:
          embed = discord.Embed(title=":x: 送信失敗",description="あなたはグローバルBANされているため、メッセージは遮断されました。",color=0xff0000)
          await message.channel.send(embed=embed)
        else:
          #まず送信待機中
          await message.add_reaction("a:loading:785106469078958081")
          #スタンプか
          if len(message.stickers) != 0:
            #余計なパーツ除去
            global_sticker = str(message.stickers)
            global_sticker = re.sub(r"\D", "", global_sticker)
            global_sticker = int(global_sticker)
            #print(message.stickers[0].image_url_as(size=1024)) #assetにして読ませてもあり？
            if global_sticker in stickers:
              global_attachments_on = 3
              global_sticker_id = str(global_sticker)
              global_sticker = str(global_sticker) + ".gif"
              global_sticker = str(global_sticker)
              print(global_sticker)
            else:
              global_attachments_on = 4
          else:
            global_attachments_on = 0
            
          #認証確認
          if message.author.id in verifyed:
            global_authorname = str(message.author) + ' ✅'
            Verifymode = 1
          else:
            global_authorname = str(message.author)
            Verifymode = 0

          if message.author.id == OWNER_ID:
            global_authorname = global_authorname + '👑'
            Verifymode = 1

          if message.author.id in moderators:
            global_authorname = global_authorname + '⛏️'
            Verifymode = 1
          
          global_avatar = message.author.avatar_url

          #添付
          lst = [3, 4]
          if not global_attachments_on in lst:
            if len(message.attachments) != 0:
              #添付ファイルのみか
              if len(message.content) == 0:
                #未認証ユーザーはカット
                if not message.author.id in verifyed:
                  global_attachments_on = 6
                else:
                  global_attachments = message.attachments[0].url
                  print(global_attachments)
                  #ここでファイル名抜出
                  attachment_dump = message.attachments[0].filename
                  str(attachment_dump)
                  global_attachments_on = 2
              else:
                if not message.author.id in verifyed:
                  global_attachments_on = 5
                  globalcontent = str(message.content)
                else:
                  global_attachments = message.attachments[0].url
                  #ここでファイル名抜出
                  attachment_dump = message.attachments[0].filename
                  str(attachment_dump)
                  global_attachments_on = 1
                  globalcontent = str(message.content)
            else:
              global_attachments_on = 0
              globalcontent = str(message.content)

          #globalcontent = repr(globalcontent) #rawに変換で文字数確認したい
          #送信元特定
          global_msg_from = discord.utils.get(await message.channel.webhooks(), name=GLOBAL_WEBHOOK_NAME)
          #余計なパーツ除去
          global_msg_from = str(global_msg_from)
          global_msg_from = re.sub(r"\D", "", global_msg_from)
          global_msg_from = int(global_msg_from)

          channels = client.get_all_channels()
          global_channels = [ch for ch in channels if ch.name == GLOBAL_CH_NAME]
          


          #認証による文字数確認
          if global_attachments_on == 0:
            if len(globalcontent) > 200:
              if Verifymode != 1:
                globalcontent = globalcontent[:200]
                LenOut = 1
                #URLが含まれているか
                globalcontent_urllist = re.findall("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", globalcontent)

                #簡易メンション対策
                if "@everyone" or "@here" in message.content:
                  if "@everyone" in message.content:
                    globalcontent = globalcontent.replace("@everyone", "`@everyone`")
                  if "@here" in message.content:
                    globalcontent = globalcontent.replace("@here", "`@here`")

                #URLが含まれていればマスクする（招待リンクはブロック、Tenorのみ許可、但しEmbedにする必要あり）
                if globalcontent[:23] == 'https://tenor.com/view/':
                  pass
                elif globalcontent[:19] == 'https://discord.gg/':
                  for url in globalcontent_urllist:
                    url = str(url)
                    url_mask = '||`' + url + '`||'
                    globalcontent = globalcontent.replace(url, url_mask)
                elif len(globalcontent_urllist) != 0:
                  for url in globalcontent_urllist:
                    url = str(url)
                    url_mask = '`' + url + '`'
                    globalcontent = globalcontent.replace(url, url_mask)
              else:
                LenOut = 0
                #URLが含まれているか
                globalcontent_urllist = re.findall("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", globalcontent)

                #簡易メンション対策
                if "@everyone" or "@here" in message.content:
                  if "@everyone" in message.content:
                    globalcontent = globalcontent.replace("@everyone", "`@everyone`")
                  if "@here" in message.content:
                    globalcontent = globalcontent.replace("@here", "`@here`")

                #URLが含まれていればマスクする（招待リンクはブロック、Tenorのみ許可、但しEmbedにする必要あり）
                if globalcontent[:23] == 'https://tenor.com/view/':
                  pass
                elif globalcontent[:19] == 'https://discord.gg/':
                  for url in globalcontent_urllist:
                    url = str(url)
                    url_mask = '||`' + url + '`||'
                    globalcontent = globalcontent.replace(url, url_mask)
                elif len(globalcontent_urllist) != 0:
                  for url in globalcontent_urllist:
                    url = str(url)
                    url_mask = '`' + url + '`'
                    globalcontent = globalcontent.replace(url, url_mask)
            else:
              LenOut = 0
              #URLが含まれているか
              globalcontent_urllist = re.findall("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", globalcontent)

              #簡易メンション対策
              if "@everyone" or "@here" in message.content:
                if "@everyone" in message.content:
                  globalcontent = globalcontent.replace("@everyone", "`@everyone`")
                if "@here" in message.content:
                  globalcontent = globalcontent.replace("@here", "`@here`")

              #URLが含まれていればマスクする（招待リンクはブロック、Tenorのみ許可、但しEmbedにする必要あり）
              if globalcontent[:23] == 'https://tenor.com/view/':
                pass
              elif globalcontent[:19] == 'https://discord.gg/':
                for url in globalcontent_urllist:
                  url = str(url)
                  url_mask = '||`' + url + '`||'
                  globalcontent = globalcontent.replace(url, url_mask)
              elif len(globalcontent_urllist) != 0:
                for url in globalcontent_urllist:
                  url = str(url)
                  url_mask = '`' + url + '`'
                  globalcontent = globalcontent.replace(url, url_mask)

          #添付ファイルあり
          elif global_attachments_on == 1:
            LenOut = 2
            #URLが含まれているか
            globalcontent_urllist = re.findall("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", globalcontent)

            #簡易メンション対策
            if "@everyone" or "@here" in message.content:
              if "@everyone" in message.content:
                globalcontent = globalcontent.replace("@everyone", "`@everyone`")
              if "@here" in message.content:
                globalcontent = globalcontent.replace("@here", "`@here`")

            #URLが含まれていればマスクする（招待リンクはブロック、Tenorのみ許可、但しEmbedにする必要あり）
            if globalcontent[:23] == 'https://tenor.com/view/':
              pass
            elif globalcontent[:19] == 'https://discord.gg/':
              for url in globalcontent_urllist:
                url = str(url)
                url_mask = '||`' + url + '`||'
                globalcontent = globalcontent.replace(url, url_mask)
            elif len(globalcontent_urllist) != 0:
              for url in globalcontent_urllist:
                url = str(url)
                url_mask = '`' + url + '`'
                globalcontent = globalcontent.replace(url, url_mask)
          #添付ファイルのみ
          elif global_attachments_on == 2:
            LenOut = 3
          #スタンプ
          elif global_attachments_on == 3:
            LenOut = 4
          #スタンプ（在庫なし）
          elif global_attachments_on == 4:
            LenOut = 5
          #添付ファイルあり（未認証ユーザー）
          elif global_attachments_on == 5:
            LenOut = 6
          #添付ファイルのみ（未認証ユーザー）
          else:
            LenOut = 7

          print(global_attachments_on)
          print(LenOut)
          #送信スタート
          for channel in global_channels:
            ch_webhooks = await channel.webhooks()
            print(ch_webhooks)
            webhook = discord.utils.get(ch_webhooks, name=GLOBAL_WEBHOOK_NAME)
            print(webhook)
              
            if webhook is None:
              # そのチャンネルに global というWebhookは無かったので無視
              continue

            ch_id = webhook.id

            #送信元はスキップ
            if ch_id == global_msg_from:
              continue

            #文字数制限を考慮した送信
            if LenOut == 1:
              await webhook.send(content=globalcontent,
              username=global_authorname,
              avatar_url=message.author.avatar_url_as(format="png"), embed=lettersover)

            elif LenOut == 0:
              await webhook.send(content=globalcontent,
              username=global_authorname,
              avatar_url=message.author.avatar_url_as(format="png"))
            
            #ファイルあり
            elif LenOut == 2:
              embed = discord.Embed(title="添付ファイル" ,description="ファイル名: [" + attachment_dump + "](" + global_attachments + ")")
              embed.set_image(url=global_attachments)
              await webhook.send(content=globalcontent,
              username=global_authorname,
              avatar_url=message.author.avatar_url_as(format="png"), embed=embed)

            #ファイルのみ
            elif LenOut == 3:
              embed = discord.Embed(title="添付ファイル" ,description="ファイル名: [" + attachment_dump + "](" + global_attachments + ")")
              embed.set_image(url=global_attachments)
              await webhook.send(username=global_authorname,
              avatar_url=message.author.avatar_url_as(format="png"), embed=embed)

            #スタンプ
            elif LenOut == 4:
              #file = discord.File("stickers/" + global_sticker_id + ".gif")
              embed = discord.Embed(title="スタンプ")
              embed.set_image(url=STICKER_URL + global_sticker)
              await webhook.send(username=global_authorname,
              avatar_url=message.author.avatar_url_as(format="png"), embed=embed)
            
            #スタンプ（在庫なし）
            elif LenOut == 5:
              embed = discord.Embed(title="スタンプ",description="※プレビューできません")
              await webhook.send(username=global_authorname,
              avatar_url=message.author.avatar_url_as(format="png"), embed=embed)

            #添付ファイルあり（未認証ユーザー）
            elif LenOut == 6:
              embed = discord.Embed(title="添付ファイル" ,description="未認証ユーザーによる添付ファイルは遮断されました。",color=0xff0000)
              await webhook.send(content=globalcontent,
              username=global_authorname,
              avatar_url=message.author.avatar_url_as(format="png"), embed=embed)

            #添付ファイルのみ（未認証ユーザー）
            else:
              embed = discord.Embed(title="添付ファイル",description="未認証ユーザーによる添付ファイルは遮断されました。",color=0xff0000)
              await webhook.send(username=global_authorname,
              avatar_url=message.author.avatar_url_as(format="png"), embed=embed)

          #送信確認リアクション
          await message.add_reaction(":finish:798910961255317524")
          await message.clear_reaction("a:loading:785106469078958081")
          await asyncio.sleep(5)
          await message.clear_reaction(":finish:798910961255317524")            


    #認証申請
    if message.content == prefix + 'verify':
      v_id = message.author.id
      v_name = message.author
      v_icon = message.author.avatar_url_as(format="png")

      if v_id in verifyed:
        embed = discord.Embed(title=":x: 失敗",description="あなたは既にグローバルチャット認証がされています。",color=0xff0000)
        await message.author.send(embed=embed)

      else:
        embed = discord.Embed(title="グローバル認証申請",description="Name: " + str(v_name) + "\nID: " + str(v_id) ,color=0x00ff00)
        user = client.get_user(OWNER_ID)
        await user.send(embed=embed)
        embed = discord.Embed(title=":white_check_mark: 完了",description="グローバルチャット認証申請が完了しました。一週間以内に結果を送信致します。",color=0x00ff00)
        await message.author.send(embed=embed)
        
    #Botの招待リンク表示
    if message.content == prefix + 'invite':
        await message.channel.send('**Aoi招待リンク**:\nhttps://www.herebots.ml/aoi')

        
'''
#メッセージが削除された時のイベント
@client.event
async def on_message_delete(message):
  if message.author.id == client.user.id: #Botならばスルー
    return
  
  print("Deleted")
'''
  
# repl.it接続
keep_alive()

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)