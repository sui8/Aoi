#インポート群
import discord #基本
import os
from server import keep_alive
from data.vips import verifyed, moderators, OWNER_ID
from data.stickers import stickers
import re #正規表現

#変数群
TOKEN = os.getenv("TOKEN") #トークン
prefix = 'o.' #Prefix
Verifymode = 0
activity = discord.Streaming(name='o.help でヘルプ', url="https://www.twitch.tv/discord")
embed_help = discord.Embed(title="Aoi コマンドリスト",description="o.invite…このBotの招待リンクを表示するよ\no.join…このコマンドを実行したチャンネルをグローバルチャットにするよ\no.verify…グローバルチャットアカウント認証申請をするよ\n\n（グローバルチャットを解除する場合は、そのチャンネルを削除してください）")
lettersover = discord.Embed(title="文字数制限超過",description="未認証ユーザーによる文字数制限超過の為、200文字を超える投稿は遮断されました。",color=0xff0000)

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

    GLOBAL_CH_NAME = "aoi-global" #グローバルチャットのチャンネル名
    GLOBAL_WEBHOOK_NAME = "AoiGlobal" #グローバルチャットのWebhook名
    if message.content == prefix + 'help':
        await message.channel.send(embed=embed_help)

    #登録
    if message.content == prefix + 'join':
      try:
        await message.channel.create_webhook(name=GLOBAL_WEBHOOK_NAME)
        await message.channel.edit(name=GLOBAL_CH_NAME)
        embed = discord.Embed(title=":white_check_mark: 成功",description="グローバルチャットへの登録に成功しました。チャンネル名は変更しないでください。",color=0x00ff00)
        await message.channel.send(embed=embed)
      except:
        await message.channel.send('**エラーが発生しました。**\nBot管理者までお問い合わせください。')

    '''
    #解除
    if message.content == prefix + 'leave':
      await discord.Webhook.delete(self=GLOBAL_CH_NAME, reason='AoiGlobal解除')
      embed = discord.Embed(title=":white_check_mark: 成功",description="グローバルチャットへの登録を解除しました。チャンネル名は変更しても問題ありません。",color=0xff0000)
      await message.channel.send(embed=embed)
      await message.channel.send('**エラーが発生しました。**\n該当するチャンネルで正しく実行できているか確認してください。')
    '''
    #DM対策必須
    if message.channel.name == GLOBAL_CH_NAME:
        # globalの名前をもつチャンネルに投稿されたので、メッセージを転送する
        #if message.content == null:
        #  pass

        #スタンプか
        if len(message.stickers) != 0:
          #余計なパーツ除去
          global_sticker = str(message.stickers)
          global_sticker = re.sub(r"\D", "", global_sticker)
          global_sticker = int(global_sticker)
          if global_sticker in stickers:
            global_attachments_on = 3
            global_sticker_id = str(global_sticker)
            global_sticker = "attachment://stickers/" + str(global_sticker) + ".gif"
            print(global_sticker)
          else:
            global_attachments_on = 4
        else:
          global_attachments_on = 0
          

        #stickers.idなどでリストから出せそう

        #添付
        lst = [3, 4]
        if not global_attachments_on in lst:
          if len(message.attachments) != 0:
            #添付ファイルのみか
            if len(message.content) == 0:
              global_attachments = message.attachments[0].url
              print(global_attachments)
              #ここでファイル名抜出
              attachment_dump = message.attachments[0].filename
              str(attachment_dump)
              global_attachments_on = 2
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

        #認証による文字数確認
        if global_attachments_on == 0:
          if len(globalcontent) > 200:
            if Verifymode != 1:
              globalcontent = globalcontent[:200]
              LenOut = 1
              globalcontent_url = re.findall("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", globalcontent)
              print(globalcontent_url)
            else:
              LenOut = 0
              globalcontent_url = re.findall("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", globalcontent)
              print(globalcontent_url)
          else:
            LenOut = 0
            globalcontent_url = re.findall("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", globalcontent)
            print(globalcontent_url)
        #添付ファイルあり
        elif global_attachments_on == 1:
          LenOut = 2
          globalcontent_url = re.findall("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", globalcontent)
          print(globalcontent_url)
        #添付ファイルのみ
        elif global_attachments_on == 2:
          LenOut = 3
        #スタンプ
        elif global_attachments_on == 3:
          LenOut = 4
        #スタンプ（在庫なし）
        else:
          LenOut = 5

        print(global_attachments_on)
        print(LenOut)
        #送信スタート
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
            file = discord.File("stickers/" + global_sticker_id + ".gif")
            #embed = discord.Embed(title="スタンプ")
            #embed.set_image(url=global_sticker)
            await webhook.send(username=global_authorname,
            avatar_url=message.author.avatar_url_as(format="png"), file=file)
          
          #スタンプ（在庫なし）
          else:
            embed = discord.Embed(title="スタンプ",description="※プレビューできません")
            await webhook.send(username=global_authorname,
            avatar_url=message.author.avatar_url_as(format="png"), embed=embed)   


        
    #せやな
    if message.content == 'せやな':
        await message.channel.send('せやな')

    #認証申請
    if message.content == prefix + 'verify':
      v_id = message.author.id
      v_name = message.author
      v_icon = message.author.avatar_url_as(format="png")

      if v_id in verifyed:
        embed = discord.Embed(title=":x: 失敗",description="あなたは既にグローバルチャット認証がされています。",color=0xff0000)
        user = client.get_user(v_id)
        await user.send(embed=embed)

      else:
        embed = discord.Embed(title="グローバル認証申請",description="Name: " + v_name + "\nID: " + str(v_id) ,color=0x00ff00)
        user = client.get_user(OWNER_ID)
        await user.send(embed=embed)

        embed = discord.Embed(title=":white_check_mark: 完了",description="グローバルチャット認証申請が完了しました。一週間以内に結果を送信致します。",color=0x00ff00)
        user = client.get_user(v_id)
        await user.send(embed=embed)
        
    #Botの招待リンク表示
    if message.content == prefix + 'invite':
        await message.channel.send('**Aoi招待リンク**:\nhttps://www.herebots.ml/aoi')
        
# repl.it接続
keep_alive()

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)