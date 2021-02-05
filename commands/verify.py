def verify():
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