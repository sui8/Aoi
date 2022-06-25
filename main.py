import discord
from discord.ext import commands
from server import keep_alive
import os #token
import asyncio #タイマー
from datetime import datetime #日付
import json #.json
from replit import db #SQL
import traceback #エラー内容取得

intents = discord.Intents.default()
intents.members = True

#############################
#Prefix反映
def _prefix_callable(bot: commands.Bot, msg: discord.Message) -> str:
  #DMはデフォルト
  if msg.guild is None:
    return DefaultPrefix
    
  else:
    if str(msg.guild.id) in db["prefix"]:
      return str(db["prefix"][str(msg.guild.id)])

    else:
      return DefaultPrefix
#############################

bot = commands.Bot(command_prefix=_prefix_callable, intents=intents)
bot.remove_command("help") #help置き換え用

#############################
ICON = os.environ['ICON']
OWNER = int(os.environ['OWNER'])
BotVersion = "4.14.2pre-α"
DefaultPrefix = "o."
NGwords = ["o.help", "o.invite", "o.ping", "o.join", "o.leave", "o.globallist", "o.prefix", "o.prefix"]
#############################


@bot.event
async def on_ready():
    #ログイン通知
    print('[System] ログインしました')

    #メンバー数等取得
    bot_guilds = len(bot.guilds)

    bot_members = []
    for guild in bot.guilds:
      for member in guild.members:
        if member.bot:
          pass
        else:
          bot_members.append(member)

    
    activity = discord.Game(name='Aoi 起動完了', url="https://www.twitch.tv/discord")
    await bot.change_presence(activity=activity)
    #起動メッセージをHereBots Hubに送信（チャンネルが存在しない場合、スルー）
    try:
      ready_log = bot.get_channel(int(os.environ['LOG_CHANNEL']))
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
    activity = discord.Streaming(name='o.help | ' + str(bot_guilds) + ' Servers ', url="https://www.twitch.tv/discord")
    await bot.change_presence(activity=activity)


@bot.event
async def on_message(message): #メッセージ受け取り
    await bot.process_commands(message) #必須
    if message.author.bot or message.guild == None: #Bot&DM弾き
        return

    #メンションされたらヘルプ返す
    if bot.user.mentioned_in(message):
      #Prefix確認から
      if message.guild is None:
        srvprefix = DefaultPrefix
      
      else:
        if str(message.guild.id) in db["prefix"]:
          srvprefix = str(db["prefix"][str(message.guild.id)])
      
        else:
          srvprefix = DefaultPrefix
  
      if str(bot.user.id) in message.content:
        embed = discord.Embed(title="📖コマンドリスト",description="```Aoi コマンドリストです。{0}<コマンド> の形で送信することで、コマンドを実行することが出来ます。```\n**🤖Botコマンド**\n`help`, `invite`, `ping`, `prefix`, `setprefix`\n\n**グローバルチャットコマンド**\n`join`, `globallist`\n\n☆このBotは開発中です。機能追加等の提案も募集しています。\n**※現在Botの大規模な改修中のため、一部機能の使用が制限されております。**）\n連絡は`HereBranch#5679`まで".format(srvprefix))
        embed.set_footer(text="❓コマンドの説明: {0}help <コマンド名>  -  Aoi v{1}".format(srvprefix, BotVersion))
        await message.reply(embed=embed, mention_author=False)

    if message.content == "なに買って来たん？":
      await message.reply("**Chocomint Ice!**", mention_author=False)

    elif message.content == "ほかには？":
      await message.reply("**Chocomint Ice!**", mention_author=False)

    elif message.content == "チョコミント":
      await message.reply("大好き！", mention_author=False)

    elif message.content == "チョコ":
      await message.reply("ミントアイス！", mention_author=False)



    #リスト作成
    sendlist = []
    
    for i in db["guilds"]: #リスト作成
      sendlist.append((int(i), db["guilds"][str(i)]["channel"], db["guilds"][str(i)]["webhook"]))

    sendchlist = [x[1] for x in sendlist]
  
    if message.channel.id in sendchlist:
      if not message.content in NGwords:
        if len(message.content) > 0:
          if len(message.content) < 2000:
            await message.add_reaction("a:loading:785106469078958081")
  
            globalcontent = str(message.content)
  
  
            #簡易メンション対策
            if "@everyone" in globalcontent:
                globalcontent = globalcontent.replace("@everyone", "`@everyone`")
            
            if "@here" in message.content:
                globalcontent = globalcontent.replace("@here", "`@here`")
  

            #仮設
            verified = [557371571153534978, 864454554614890497, 736215070375411765, 691913615376252949]
            if message.author.id in verified:
              global_authorname = str(message.author) + ' ✅'
  
              if message.author.id == OWNER:
                global_authorname = global_authorname + '👑'
        
            else:
              global_authorname = str(message.author)
  
              
            for i in range(len(sendlist)):
              gl = discord.utils.get(bot.guilds, id=sendlist[i][0])
              ch = discord.utils.get(gl.text_channels, id=sendlist[i][1])
              wh = discord.utils.get(await ch.webhooks(), id=sendlist[i][2])
        
              if wh is None:
                continue
  
              if sendlist[i][0] == message.guild.id:
                continue
              
              #メッセージ設定
              await wh.send(content=globalcontent, username=global_authorname, avatar_url=message.author.avatar_url_as(format="png"))
  
  
            #送信確認リアクション
            await message.add_reaction(":finish:798910961255317524")
            await message.clear_reaction("a:loading:785106469078958081")
            await asyncio.sleep(5)
            await message.clear_reaction(":finish:798910961255317524")   
        



@bot.command()
async def help(ctx, *arg):
  #Prefix確認から
  if ctx.guild is None:
    srvprefix = DefaultPrefix
  
  else:
    if str(ctx.guild.id) in db["prefix"]:
      srvprefix = str(db["prefix"][str(ctx.guild.id)])
  
    else:
      srvprefix = DefaultPrefix
      
  #引数がある（helpのhelpの）とき
  if arg:
    with open('data/commands.json', encoding='utf-8') as f:
      commands = json.load(f)

    if str(arg[0]) in commands:
      category = commands[str(arg[0])]["category"]
      help_usage = commands[str(arg[0])]["usage"]
      help_info = commands[str(arg[0])]["info"]
      embed = discord.Embed(title=category + ": **{0}**".format(arg[0]),description="")
      embed.add_field(name="使い方", value="\n```{0}{1}```".format(srvprefix, help_usage),inline=False)
      embed.add_field(name="説明", value="```{0}```".format(help_info),inline=False)
      embed.set_footer(text="<> : 必要引数 | [] : オプション引数")
      await ctx.reply(embed=embed, mention_author=False)

  else:
    embed = discord.Embed(title="📖コマンドリスト",description="```Aoi コマンドリストです。{0}<コマンド> の形で送信することで、コマンドを実行することが出来ます。```\n**🤖Botコマンド**\n`help`, `invite`, `ping`, `prefix`, `setprefix`\n\n**グローバルチャットコマンド**\n`join`, `globallist`\n\n☆このBotは開発中です。機能追加等の提案も募集しています。\n**※現在Botの大規模な改修中のため、一部機能の使用が制限されております。**）\n連絡は`HereBranch#5679`まで".format(srvprefix))
    embed.set_footer(text="❓コマンドの説明: {0}help <コマンド名>  -  Aoi v{1}".format(srvprefix, BotVersion))
    await ctx.reply(embed=embed, mention_author=False)


@bot.command()
async def invite(ctx):
    embed = discord.Embed(title="招待リンク",description="こちらから、サーバー管理権限を持ったユーザーでAoiの招待が出来ます。\nhttps://www.herebots.ml/aoi",color=0xdda0dd)
    await ctx.reply(embed=embed, mention_author=False)


@bot.command()
async def ping(ctx):
    embed = discord.Embed(title="📤Ping", description="`{0}ms`".format(round(bot.latency*1000, 2)), color=0xc8ff00)
    await ctx.reply(embed=embed, mention_author=False)


@bot.command()
async def prefix(ctx):
  guild = str(ctx.guild.id)

  if guild in db["prefix"]:
    nowprefix = db["prefix"][guild]

  else:
    nowprefix = DefaultPrefix
        
  embed = discord.Embed(title="サーバーのPrefix",description="このサーバーのPrefixは`{0}`です。\n変更する場合は`setprefix`コマンドを実行して下さい。".format(nowprefix),color=0xf5deb3)
  await ctx.reply(embed=embed, mention_author=False)


@bot.command()
async def setprefix(ctx, *arg):
  guild = str(ctx.guild.id)

  #権限不足
  if not ctx.author.guild_permissions.administrator:
    embed = discord.Embed(title=":x: エラー",description="このコマンドを実行するにはサーバー管理権限が必要です",color=0xff0000)
    await ctx.reply(embed=embed, mention_author=False)

  else:
    if arg:
      #すでに変更したことがあった場合
      if guild in db["prefix"]:
        oldprefix = db["prefix"][guild]
        db["prefix"][guild] = str(arg[0])
        
        embed = discord.Embed(title=":white_check_mark: 完了",description="このサーバーのPrefixを`{0}`から`{1}`に変更しました。".format(oldprefix, str(arg[0])),color=0x00ff00)
        await ctx.reply(embed=embed, mention_author=False)

      else:
        db["prefix"][guild] = str(arg[0])
        
        embed = discord.Embed(title=":white_check_mark: 完了",description="このサーバーのPrefixを`{0}`から`{1}`に変更しました。".format(DefaultPrefix, str(arg[0])),color=0x00ff00)
        await ctx.reply(embed=embed, mention_author=False)

    else:
      embed = discord.Embed(title=":x: エラー",description="引数を指定して下さい",color=0xff0000)
      await ctx.reply(embed=embed, mention_author=False)


@bot.command()
async def join(ctx):
  guild = str(ctx.guild.id)

  #権限不足
  if not ctx.author.guild_permissions.administrator:
    embed = discord.Embed(title=":x: エラー",description="このコマンドを実行するにはサーバー管理権限が必要です",color=0xff0000)
    await ctx.reply(embed=embed, mention_author=False)

  else:
  
    #未登録
    if not guild in db["guilds"]:
      webhook = await ctx.channel.create_webhook(name='AoiGlobal')
      db["guilds"][guild] = {}
      db["guilds"][guild]["channel"] = ctx.channel.id
      db["guilds"][guild]["webhook"] = webhook.id
      db["guilds"][guild]["owner"] = ctx.guild.owner.id
      db["guilds"][guild]["datetime"] = str(datetime.now())
  
      embed = discord.Embed(title=":white_check_mark: 成功",description="グローバルチャットへの登録に成功しました。作成されているウェブフックは削除しないで下さい。（グローバルチャットを解除する場合は、`o.leave` を実行して下さい）",color=0x00ff00)
      await ctx.reply(embed=embed)
  
      #登録通知
      sendlist = []
      
      for i in db["guilds"]: #リスト作成
        sendlist.append((int(i), db["guilds"][str(i)]["channel"], db["guilds"][str(i)]["webhook"]))
  
      #sendchlist = [x[1] for x in sendlist]
  
      for i in range(len(sendlist)):
        gl = discord.utils.get(bot.guilds, id=sendlist[i][0])
        ch = discord.utils.get(gl.text_channels, id=sendlist[i][1])
        wh = discord.utils.get(await ch.webhooks(), id=sendlist[i][2])
  
        if wh is None:
          continue
        
        #Aoi設定
        embed = discord.Embed(title=":white_check_mark: 参加",description="**{0}**がグローバルチャットに参加しました".format(ctx.guild.name),color=0x00ff00)
        await wh.send(username="Aoi ✅🤖", avatar_url=ICON, embed=embed)
  
  
    else:
      embed = discord.Embed(title=":x: エラー",description="このサーバーは既にグローバルチャットに登録されています。",color=0xff0000)
      await ctx.reply(embed=embed, mention_author=False)


'''
@bot.command()
@commands.has_permissions(administrator=True)
async def leave(ctx):
  guild = str(ctx.guild.id)

  #未登録
  if guild in db["guilds"]:
    gl = discord.utils.get(bot.guilds, id=guild)
    ch = discord.utils.get(gl.text_channels, id=db["guilds"][guild]["channel"])
    wh = discord.utils.get(await ch.webhooks(), id=db["guilds"][guild]["webhook"])
    await wh.delete()

    del db["guilds"][guild]

    embed = discord.Embed(title=":white_check_mark: 成功",description="グローバルチャットを解除しました。",color=0x00ff00)
    await ctx.send(embed=embed)

    #登録通知
    sendlist = []
    
    for i in db["guilds"]: #リスト作成
      sendlist.append((int(i), db["guilds"][str(i)]["channel"], db["guilds"][str(i)]["webhook"]))

    sendchlist = [x[1] for x in sendlist]

    for i in range(len(sendlist)):
      gl = discord.utils.get(bot.guilds, id=sendlist[i][0])
      ch = discord.utils.get(gl.text_channels, id=sendlist[i][1])
      wh = discord.utils.get(await ch.webhooks(), id=sendlist[i][2])

      if wh is None:
        continue
      
      #Aoi設定
      embed = discord.Embed(title=":x: 退出",description="**{0}**がグローバルチャットから退出しました".format(ctx.guild.name),color=0xff0000)
      await wh.send(username="Aoi ✅🤖", avatar_url=ICON, embed=embed)


  else:
    embed = discord.Embed(title=":x: エラー",description="このサーバーは既にグローバルチャットに登録されています。",color=0xff0000)
    await ctx.send(embed=embed)
'''
    
@bot.command()
async def globallist(ctx):
  globalllist = []
  
  #for i in db["guilds"]:
  # bot.get_guild(i)
    
  embed = discord.Embed(title="グローバルチャット接続中サーバーリスト", description="準備中")
  embed.set_footer(text="接続中サーバー数: {0}サーバー".format(len(db["guilds"])))
  await ctx.reply(embed=embed, mention_author=False)




######ここから下は開発用######
@bot.command()
async def devhelp(ctx):
  if ctx.author.id == OWNER:
    embed = discord.Embed(title="📖開発用コマンドリスト",description="```Aoi コマンドリストです。/ + <ここに記載されているコマンド> の形で送信することで、コマンドを実行することが出来ます。```\n`devhelp`, `db_show`, `db_setkey`, `db_getkey`, `db_delkey`\n\n☆このBotは開発中です。機能追加等の提案も募集しています。\n**※現在Botの大規模な改修中のため、一部機能の使用が制限されております。**）\n連絡は`HereBranch#5679`まで")
    embed.set_footer(text="❓コマンドの説明: o.help <コマンド名>  -  Aoi v{0}".format(BotVersion))
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





keep_alive()

#429エラー防止
try:
  bot.run(os.environ['TOKEN'])

except:
  os.system("kill 1")