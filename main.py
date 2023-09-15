import discord
import discord.app_commands
from discord.ext import commands
from server import keep_alive
import os #token
import asyncio #タイマー
from datetime import datetime #日付
import json #.json
from replit import db #SQL
import traceback #エラー内容取得
import io
import aiohttp

intents = discord.Intents.all()
intents.members = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

#############################
ICON = os.environ['ICON']
OWNER = int(os.environ['OWNER'])
BotVersion = "5.1.0"
global_channel_name = "aoiglobal"
verified = ["557371571153534978"]
blocked = []
#############################


@client.event
async def on_ready():
    #ログイン通知
    print('[Aoi] ログインしました')

    #メンバー数等取得
    bot_guilds = len(client.guilds)

    bot_members = []
    for guild in client.guilds:
      for member in guild.members:
        if member.bot:
          pass
        else:
          bot_members.append(member)

    
    activity = discord.Game(name='Aoi 起動完了', url="https://www.twitch.tv/discord")
    await client.change_presence(activity=activity)
    #起動メッセージをHereBots Hubに送信（チャンネルが存在しない場合、スルー）
    try:
      ready_log = client.get_channel(int(os.environ['LOG_CHANNEL']))
      embed = discord.Embed(title="Aoi 起動完了",
                            description="**Aoi#5716** が起動しました。\n```サーバー数: {0}\nユーザー数: {1}```".format( 
                              bot_guilds, 
                              len(bot_members)),
                            timestamp=datetime.now())
      embed.set_footer(text="Aoi - Ver" + BotVersion,icon_url=ICON)
      await ready_log.send(embed=embed)

    except:
      pass


    await asyncio.sleep(10)
    activity = discord.Streaming(name='/help | ' + str(bot_guilds) + ' Servers ', url="https://www.twitch.tv/discord")
    await client.change_presence(activity=activity)
  
    #コマンドをSync
    try:
      await tree.sync()
    except:
      print("Failed to sync.")
    else:
      print("Commands synced.")


@client.event
async def on_message(message): #メッセージ受け取り
    if message.author.bot:
      return
      
    if message.channel.name == global_channel_name: #グローバルチャットにメッセージが来たとき
        #メッセージ送信部
        if str(message.author.id) in blocked:
          embed = discord.Embed(title=":x: 送信失敗",description="あなたはグローバルチャットからBANされています。",color=0xff0000)
          await message.reply(embed=embed, mention_author=True)

        else:
          for channel in client.get_all_channels(): #BOTが所属する全てのチャンネルをループ
              if channel.name == global_channel_name: #グローバルチャット用のチャンネルが見つかったとき
                  if channel == message.channel: #発言したチャンネルには送らない
                      continue
  
                  webhooks = await channel.webhooks()
  
                  if len(webhooks) == 0:
                    await channel.create_webhook(name="AoiGlobal")
                    webhooks = await channel.webhooks()
  
                  if str(message.author.discriminator) == "0":
                    if str(message.author.id) in verified:
                      authorname = "{0} ✅ (From: {1})".format(message.author.name, message.guild.name)
  
                    else:
                      authorname = "{0} (From: {1})".format(message.author.name, message.guild.name)
  
                  else:
                    authorname = "{0}#{1} (From: {2})".format(message.author.name, message.author.discriminator, message.guild.name) 


                  if len(message.content) > 0:
                    if message.attachments != []: #添付ファイルが存在するとき
                      async with aiohttp.ClientSession() as session:
                        async with session.get(message.attachments[0].url) as resp:
                          if resp.status != 200:
                            embed = discord.Embed(title=":x: 送信失敗",description="ファイルの添付に失敗しました",color=0xff0000)
                            await message.reply(embed=embed, mention_author=False)
          
                          else:
                            data = io.BytesIO(await resp.read())
                        
                            if hasattr(message.author.avatar, 'key'):
                              await webhooks[0].send(content=message.content, username=authorname, avatar_url=message.author.avatar.url, file=discord.File(data, str(message.attachments[0].filename)))
    
                            else:
                             await webhooks[0].send(content=message.content, username=authorname, file=discord.File(data, str(message.attachments[0].filename)))

                    else:
                      if hasattr(message.author.avatar, 'key'):
                        await webhooks[0].send(content=message.content, username=authorname, avatar_url=message.author.avatar.url)
    
                      else:
                        await webhooks[0].send(content=message.content, username=authorname)
                    
                  else:
                    if message.attachments != []: #添付ファイルが存在するとき
                      async with aiohttp.ClientSession() as session:
                        async with session.get(message.attachments[0].url) as resp:
                          if resp.status != 200:
                            embed = discord.Embed(title=":x: 送信失敗",description="ファイルの添付に失敗しました",color=0xff0000)
                            await message.reply(embed=embed, mention_author=False)
          
                          else:
                            data = io.BytesIO(await resp.read())
                        
                            if hasattr(message.author.avatar, 'key'):
                              await webhooks[0].send(username=authorname, avatar_url=message.author.avatar.url, file=discord.File(data, str(message.attachments[0].filename)))
    
                            else:
                             await webhooks[0].send(username=authorname, file=discord.File(data, str(message.attachments[0].filename)))

                
          await message.add_reaction('✅') #リアクションを送信


    elif message.author.bot: #Bot弾き
      return
      
    elif message.content == "なに買って来たん？":
      await message.reply("**Chocomint Ice!**", mention_author=False)

    elif message.content == "ほかには？":
      await message.reply("**Chocomint Ice!**", mention_author=False)

    elif message.content == "チョコミント":
      await message.reply("大好き！", mention_author=False)

    elif message.content == "チョコ":
      await message.reply("ミントアイス！", mention_author=False)


@tree.command(name="help", description="このBotのヘルプを表示します")
@discord.app_commands.describe(command="指定したコマンドの説明を表示します")
async def help(ctx: discord.Interaction, command: str = None):
  if command:
    with open('data/commands.json', encoding='utf-8') as f:
      commands = json.load(f)
      print(command[0])

    if str(command[0]) in commands:
      category = commands[str(command[0])]["category"]
      help_usage = commands[str(command[0])]["usage"]
      help_info = commands[str(command[0])]["info"]
      embed = discord.Embed(title=category + ": **" + str(command[0]) + "**",
                            description="")
      embed.add_field(name="使い方",
                      value="\n```/" + help_usage + "```",
                      inline=False)
      embed.add_field(name="説明", value="```" + help_info + "```", inline=False)
      embed.set_footer(text="<> : 必要引数 | [] : オプション引数")
      await ctx.response.send_message(embed=embed)

    else:
      embed = discord.Embed(
      title="📖コマンドリスト",
      description=
      "```Aoi コマンドリストです。/ + <ここに記載されているコマンド> の形で送信することで、コマンドを実行することが出来ます。```\n**🤖Botコマンド**\n`help`, `invite`, `ping`\n\n☆このBotは開発中です。機能追加等の提案も募集しています。\n**#aoiglobalを作成するとグローバルチャットが利用できます！**）\n連絡は`@bz6 (Branch#7777)`まで"
      )
      embed.set_footer(text="❓コマンドの説明: /help <コマンド名>")
      await ctx.response.send_message(embed=embed)

  else:
    embed = discord.Embed(
      title="📖コマンドリスト",
      description=
      "```Aoi コマンドリストです。/ + <ここに記載されているコマンド> の形で送信することで、コマンドを実行することが出来ます。```\n**🤖Botコマンド**\n`help`, `invite`, `ping`\n\n☆このBotは開発中です。機能追加等の提案も募集しています。\n**#aoiglobalを作成するとグローバルチャットが利用できます！**）\n連絡は`@bz6 (Branch#7777)`まで"
      )
    embed.set_footer(text="❓コマンドの説明: /help <コマンド名>")
    await ctx.response.send_message(embed=embed)


#招待リンク
@tree.command(name="invite", description="このBotの招待リンクを表示します")
async def invite(ctx: discord.Interaction):
  button = discord.ui.Button(label="招待する",style=discord.ButtonStyle.link,url="https://www.herebots.ml/akane")
  embed = discord.Embed(
    title="招待リンク",
    description=
    "以下のボタンから、サーバー管理権限を持ったユーザーでAkaneの招待が出来ます。",
    color=0xdda0dd)
  view = discord.ui.View()
  view.add_item(button)
  await ctx.response.send_message(embed=embed,view=view)
    

#ping
@tree.command(name="ping", description="このBotのPingを確認します")
async def ping(ctx: discord.Interaction):
  embed = discord.Embed(title="📤Ping",
                        description="`{0}ms`".format(
                          round(bot.latency * 1000, 2)),
                        color=0xc8ff00)
  await ctx.response.send_message(embed=embed)

#招待リンク
@tree.command(name="glist", description="グローバルチャットに接続しているサーバー一覧を表示します")
async def glist(ctx: discord.Interaction):
  glist = []
  
  for channel in client.get_all_channels(): #BOTが所属する全てのチャンネルをループ
    if channel.name == global_channel_name:
      glist.append(str(channel.guild.name))
      
  embed = discord.Embed(
    title="接続中サーバー一覧",
    description=
    f"サーバー数: `{len(glist)}`",
    color=0xdda0dd)

  glist_print = ""
  
  for i in glist:
    glist_print = glist_print + f"・{i}\n"

  if len(glist_print) > 1000:
    glist_print = glist_print[:999]
  
  embed.add_field(name="一覧",value=glist_print)
  view = discord.ui.View()
  await ctx.response.send_message(embed=embed,view=view)

'''
######ここから下は開発用######
@bot.command()
async def devhelp(ctx):
  if ctx.author.id == OWNER:
    embed = discord.Embed(title="📖開発用コマンドリスト",description="```Aoi コマンドリストです。/ + <ここに記載されているコマンド> の形で送信することで、コマンドを実行することが出来ます。```\n`devhelp`, `db_show`, `db_setkey`, `db_getkey`, `db_delkey`\n\n☆このBotは開発中です。機能追加等の提案も募集しています。\n**※現在Botの大規模な改修中のため、一部機能の使用が制限されております。**）\n連絡は`@bz6 (Branch#7777)`まで")
    embed.set_footer(text="❓コマンドの説明: /help <コマンド名>  -  Aoi v{0}".format(BotVersion))
    await ctx.reply(embed=embed, mention_author=False)

@bot.command()
async def db_show(ctx):
  if ctx.author.id == OWNER:
    try:
      items = list(db.items())

    except:
            embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(traceback.format_exc()),color=0xff0000)
            await ctx.reply(embed=embed, mention_author=False)

    else:
      await ctx.reply("データベース情報を出力します。\n```{0}```".format(items), mention_author=False)

@bot.command()
async def db_setkey(ctx, *args):
  if ctx.author.id == OWNER:
    if not args:
      embed = discord.Embed(title=":x: エラー",description="keyを指定して下さい",color=0xff0000)
      await ctx.reply(embed=embed, mention_author=False)

    else:
      if len(args) != 2:
        embed = discord.Embed(title=":x: エラー",description="`key` `value` の順で引数を指定してください",color=0xff0000)
        await ctx.reply(embed=embed, mention_author=False)

      elif args[0][0] == "/":
        embed = discord.Embed(title=":x: エラー",description="keyを正しく設定して下さい",color=0xff0000)
        await ctx.reply(embed=embed, mention_author=False)
      
      elif not args[0].replace('/', '').replace(' ', ''): #空のkey排除
        embed = discord.Embed(title=":x: エラー",description="keyを正しく設定して下さい",color=0xff0000)
        await ctx.reply(embed=embed, mention_author=False)

      else:
        key_nest = args[0].split('/')

        #########################ここから最悪実装！！一般化必須！！
        if len(key_nest) > 5:
          embed = discord.Embed(title=":x: エラー",description="5層以上のkeyは指定できませんを正しく設定して下さい",color=0xff0000)
          await ctx.reply(embed=embed, mention_author=False)

        else:
          #1層
          if len(key_nest) == 1:
            try:
              if args[1].lower() == "null":
                db[str(key_nest[0])] = {}
    
              else:
                db[str(key_nest[0])] = args[1]
  
            except Exception as e:
              embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(e),color=0xff0000)
              await ctx.reply(embed=embed, mention_author=False)

            else:
              await ctx.reply("`{0}`の値を`{1}`に設定しました。".format(args[0], args[1]), mention_author=False)

          #2層
          elif len(key_nest) == 2:
            try:
              if args[1].lower() == "null":
                db[str(key_nest[0])][str(key_nest[1])] = {}
    
              else:
                db[str(key_nest[0])][str(key_nest[1])] = args[1]
  
            except Exception as e:
              embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(e),color=0xff0000)
              await ctx.reply(embed=embed, mention_author=False)

            else:
              await ctx.reply("`{0}`の値を`{1}`に設定しました。".format(args[0], args[1]), mention_author=False)

          #3層
          elif len(key_nest) == 3:
            try:
              if args[1].lower() == "null":
                db[str(key_nest[0])][str(key_nest[1])][str(key_nest[2])] = {}
    
              else:
                db[str(key_nest[0])][str(key_nest[1])][str(key_nest[2])] = args[1]
  
            except Exception as e:
              embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(e),color=0xff0000)
              await ctx.reply(embed=embed, mention_author=False)

            else:
              await ctx.reply("`{0}`の値を`{1}`に設定しました。".format(args[0], args[1]), mention_author=False)

          #4層
          elif len(key_nest) == 4:
            try:
              if args[1].lower() == "null":
                db[str(key_nest[0])][str(key_nest[1])][str(key_nest[2])][str(key_nest[3])] = {}
    
              else:
                db[str(key_nest[0])][str(key_nest[1])][str(key_nest[2])][str(key_nest[3])] = args[1]
  
            except Exception as e:
              embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(e),color=0xff0000)
              await ctx.reply(embed=embed, mention_author=False)

            else:
              await ctx.reply("`{0}`の値を`{1}`に設定しました。".format(args[0], args[1]), mention_author=False)

          #5層
          elif len(key_nest) == 5:
            try:
              if args[1].lower() == "null":
                db[str(key_nest[0])][str(key_nest[1])][str(key_nest[2])][str(key_nest[3])][str(key_nest[4])] = {}
    
              else:
                db[str(key_nest[0])][str(key_nest[1])][str(key_nest[2])][str(key_nest[3])][str(key_nest[4])] = args[1]
  
            except Exception as e:
              embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(e),color=0xff0000)
              await ctx.reply(embed=embed, mention_author=False)

            else:
              await ctx.reply("`{0}`の値を`{1}`に設定しました。".format(args[0], args[1]), mention_author=False)



@bot.command()
async def db_getkey(ctx, *args):
  if ctx.author.id == OWNER:
    if not args:
      embed = discord.Embed(title=":x: エラー",description="keyを指定して下さい",color=0xff0000)
      await ctx.reply(embed=embed, mention_author=False)

    else:
      if len(args) != 1:
        embed = discord.Embed(title=":x: エラー",description="keyのみを指定して下さい",color=0xff0000)
        await ctx.reply(embed=embed, mention_author=False)

      elif args[0][0] == "/":
          embed = discord.Embed(title=":x: エラー",description="keyを正しく設定して下さい",color=0xff0000)
          await ctx.reply(embed=embed, mention_author=False)
      
      elif not args[0].replace('/', '').replace(' ', ''): #空のkey排除
        embed = discord.Embed(title=":x: エラー",description="keyを正しく設定して下さい",color=0xff0000)
        await ctx.reply(embed=embed, mention_author=False)
  
      else:
        key_nest = args[0].split('/')

        #########################ここから最悪実装！！一般化必須！！

        if len(key_nest) > 5:
          embed = discord.Embed(title=":x: エラー",description="5層以上のkeyは指定できません",color=0xff0000)
          await ctx.reply(embed=embed, mention_author=False)

        #1層
        elif len(key_nest) == 1:
          try:
            value = db[key_nest[0]]
  
          except:
            embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(traceback.format_exc()),color=0xff0000)
            await ctx.reply(embed=embed, mention_author=False)
  
          else:
            await ctx.reply("`{0}`の値は`{1}`です。".format(args[0],value), mention_author=False)

        #2層
        if len(key_nest) == 2:
          try:
            value = db[key_nest[0]][key_nest[1]]
  
          except:
            embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(traceback.format_exc()),color=0xff0000)
            await ctx.reply(embed=embed, mention_author=False)
  
          else:
            await ctx.reply("`{0}`の値は`{1}`です。".format(args[0],value), mention_author=False)

        #3層
        if len(key_nest) == 3:
          try:
            value = db[key_nest[0]][key_nest[1]][key_nest[2]]
  
          except:
            embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(traceback.format_exc()),color=0xff0000)
            await ctx.reply(embed=embed, mention_author=False)
  
          else:
            await ctx.reply("`{0}`の値は`{1}`です。".format(args[0],value), mention_author=False)

        #4層
        if len(key_nest) == 4:
          try:
            value = db[key_nest[0]][key_nest[1]][key_nest[2]][key_nest[3]]
  
          except:
            embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(traceback.format_exc()),color=0xff0000)
            await ctx.reply(embed=embed, mention_author=False)
  
          else:
            await ctx.reply("`{0}`の値は`{1}`です。".format(args[0],value), mention_author=False)

        #5層
        if len(key_nest) == 5:
          try:
            value = db[key_nest[0]][key_nest[1]][key_nest[2]][key_nest[3]][key_nest[4]]
  
          except:
            embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(traceback.format_exc()),color=0xff0000)
            await ctx.reply(embed=embed, mention_author=False)
  
          else:
            await ctx.reply("`{0}`の値は`{1}`です。".format(args[0],value), mention_author=False)




@bot.command()
async def db_delkey(ctx, *args):
  if ctx.author.id == OWNER:
    if not args:
      embed = discord.Embed(title=":x: エラー",description="keyを指定して下さい",color=0xff0000)
      await ctx.reply(embed=embed, mention_author=False)

    else:
      if len(args) != 1:
        embed = discord.Embed(title=":x: エラー",description="keyのみを指定して下さい",color=0xff0000)
        await ctx.reply(embed=embed, mention_author=False)

      elif args[0][0] == "/":
          embed = discord.Embed(title=":x: エラー",description="keyを正しく設定して下さい",color=0xff0000)
          await ctx.reply(embed=embed, mention_author=False)
      
      elif not args[0].replace('/', '').replace(' ', ''): #空のkey排除
        embed = discord.Embed(title=":x: エラー",description="keyを正しく設定して下さい",color=0xff0000)
        await ctx.reply(embed=embed, mention_author=False)
  
      else:
        key_nest = args[0].split('/')

        #########################ここから最悪実装！！一般化必須！！

        if len(key_nest) > 5:
          embed = discord.Embed(title=":x: エラー",description="5層以上のkeyは指定できません",color=0xff0000)
          await ctx.reply(embed=embed, mention_author=False)
        
        #1層
        if len(key_nest) == 1:
          try:
            del db[str(key_nest[0])]
  
          except:
            embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(traceback.format_exc()),color=0xff0000)
            await ctx.reply(embed=embed, mention_author=False)
  
          else:
            await ctx.reply("`{0}`を削除しました。".format(args[0]), mention_author=False)

        #2層
        if len(key_nest) == 2:
          try:
            del db[str(key_nest[0])][str(key_nest[1])]
  
          except:
            embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(traceback.format_exc()),color=0xff0000)
            await ctx.reply(embed=embed, mention_author=False)
  
          else:
            await ctx.reply("`{0}`を削除しました。".format(args[0]), mention_author=False)

        #3層
        if len(key_nest) == 3:
          try:
            del db[str(key_nest[0])][str(key_nest[1])][str(key_nest[2])]
  
          except:
            embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(traceback.format_exc()),color=0xff0000)
            await ctx.reply(embed=embed, mention_author=False)
  
          else:
            await ctx.reply("`{0}`を削除しました。".format(args[0]), mention_author=False)

        #4層
        if len(key_nest) == 4:
          try:
            del db[str(key_nest[0])][str(key_nest[1])][str(key_nest[2])][str(key_nest[3])]
  
          except:
            embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(traceback.format_exc()),color=0xff0000)
            await ctx.reply(embed=embed, mention_author=False)
  
          else:
            await ctx.reply("`{0}`を削除しました。".format(args[0]), mention_author=False)

        #5層
        if len(key_nest) == 5:
          try:
            del db[str(key_nest[0])][str(key_nest[1])][str(key_nest[2])][str(key_nest[3])][str(key_nest[4])]
  
          except:
            embed = discord.Embed(title=":x: エラー",description="予期しないエラーが発生しました。\nエラー内容を以下に表示します。\n```{0}```".format(traceback.format_exc()),color=0xff0000)
            await ctx.reply(embed=embed, mention_author=False)
  
          else:
            await ctx.reply("`{0}`を削除しました。".format(args[0]), mention_author=False)
'''




keep_alive()

#429エラー防止
try:
  client.run(os.environ['TOKEN'])

except:
  os.system("kill 1")
db["VERIFIED"] = "2"
db["VERIFIED"] = "256565"
