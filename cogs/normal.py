from discord.ext import tasks, commands
import discord
import asyncio
import random
import MySQLdb
import os

class normal(commands.Cog):
    def __init__(self, bot):
        self.conn = MySQLdb.connect(
        user=os.environ['nakagawadb_user'],
        passwd=os.environ['nakagawadb_passwd'],
        host=os.environ['nakagawadb_host'],
        db=os.environ['nakagawadb_name'],
        charset="utf8",
        autocommit=True
        )
        self.connecter.start()
        self.bluesrice = 0
        self.redsrice = 0
        self.bot = bot
        self.recruitid = 1
        self.players = []
        self.lucky = []
        self.count = 0
        self.already = {}
        self.recruitm = None

    @tasks.loop(hours=4.0)
    async def connecter(self):
        self.conn.close()
        self.conn = MySQLdb.connect(
        user=os.environ['nakagawadb_user'],
        passwd=os.environ['nakagawadb_passwd'],
        host=os.environ['nakagawadb_host'],
        db=os.environ['nakagawadb_name'],
        charset="utf8",
        autocommit=True
        )

    @commands.command()
    async def register(self, ctx, newid):
        c = self.conn.cursor()
        sql = f"SELECT COUNT(1) FROM playerdata WHERE id = {ctx.author.id}"
        c.execute(sql)
        if c.fetchone()[0]:
            await ctx.send("すでに登録されています")
        else:
            sql = 'insert into playerdata values (%s, %s)'
            c.execute(sql, (ctx.author.id, newid))#(msg.author.id, msg.content)
            await ctx.send(f"UplayIDを:**{newid}**で登録しました")
        c.close()


    @commands.command()
    async def checkid(self, ctx, *args):#自分の登録されている名前を確認
        if ctx.message.mentions:
            target = ctx.message.mentions[0]
            #print("*mention*")
        elif args:   
            if args[0].isdigit():
                #print(f"Targrt id = {args[0]}")
                target = self.bot.get_user(int(args[0]))
                #print("*id*")
            else:
                ctx.send("IDを指定する場合は数値で指定ください")
        else:
            target = ctx.author
            print("*author*")
        c = self.conn.cursor()
        sql = f'select ign from playerdata where id = {target.id}'#名前を取得
        c.execute(sql)
        ign = c.fetchone()[0]
        #print(f"{target.name} is {ign}")
        await ctx.send(f"{target.name}のUplayIDは **{ign}** です")
        c.close()


    @commands.command()
    async def changeid(self, ctx, newid):
    #id変更コマンド
        c = self.conn.cursor()
        sql = f"update playerdata set ign = '{newid}' where id= {ctx.author.id};"
        c.execute(sql)
        await ctx.channel.send(f"UplayIDを:**{newid}**にしました")
        c.close()

    @register.error
    async def register_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send("IDを入力してください\n例```n!register id```")

    @checkid.error
    async def checkid_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send("IDが登録されていません\nregisterコマンドで登録することができます\n例```n!register id```")

    @changeid.error
    async def changeid_eror(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):#引数が足りないエラー
            await ctx.send("設定するIDを入力してください\n例```n!changeid id```")
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send("IDが登録されていません\nregisterコマンドで設定してください\n例```n!register id```")
    
    @commands.command()
    async def resetall(self, ctx):
        if ctx.author.guild_permissions.administrator or ctx.message.guild.get_role(741998241989525575) in ctx.message.author.roles:
            self.already.clear()
            self.players.clear()
            self.lucky.clear()
            await ctx.send("参加プレイヤーと当選プレイヤーをリセットしました")
        else:
            ctx.channel.send("このコマンドは管理者のみ使用可能です")

    @commands.command()
    async def start(self, ctx, bluesrice: int, orangesrice: int, count=0):
        if ctx.author.guild_permissions.administrator or ctx.message.guild.get_role(741998241989525575) in ctx.message.author.roles:
            if count == 0:
                self.count = 0
            else:
                self.count = count
            self.players.clear()#抽選参加プレイヤーをクリア
            self.lucky.clear()#当選者のリセット
            self.bluesrice = bluesrice
            self.orangesrice = orangesrice
            #print(f"COUNT IS {count} class count is {self.count}")
            recruit = await ctx.channel.send("カスタムマッチの募集を始めます\n参加したい人は👍を押してください\n参加をキャンセルする場合は❌を推してください\n現在の参加プレイヤー数:**0**")
            self.recruitm = recruit
            nrecruitid = recruit.id
            self.recruitid = nrecruitid
            await recruit.add_reaction("👍")
            await recruit.add_reaction("❌")
            def check(reaction, user):
                return user.guild_permissions.administrator == True and reaction.message.id == self.recruitid and str(reaction.emoji) == '✅' or user.guild_permissions.administrator == True and reaction.message.id == self.recruitid and str(reaction.emoji) == '🔚' or user.guild.get_role(741998241989525575) in reaction.message.author.guild.roles and reaction.message.id == self.recruitid and str(reaction.emoji) == '✅' or user.guild.get_role(741998241989525575) in reaction.message.author.guild.roles and reaction.message.id == self.recruitid  and str(reaction.emoji) == '🔚'    
                #もしつけられたリアクションが✅か🔚だったというcheck関数
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check)
                #つけられたリアクションが✅か🔚なら
            except asyncio.TimeoutError:
                #タイムアウトした場合の処理
                return
            else:
                #それ以外の場合(つけられたリアクションが✅か🔚の場合)
                if str(reaction) == '✅':#つけられたリアクションが✅ならチーム分け
                    log_c = self.bot.get_channel(744180284584493086)
                    c = self.conn.cursor()
                    await ctx.channel.send('募集を締め切り、チーム分けを行います')#チーム分けをするというメッセージ
                    print(f"シャッフル前プレイヤーID:{self.players}")
                    await log_c.send(f"シャッフル前プレイヤーID:{self.players}")
                    random.shuffle(self.players)#参加しているプレイヤーが入っているリストをシャッフル
                    print(f"シャッフル後プレイヤーID:{self.players}")
                    await log_c.send(f"シャッフル後プレイヤーID:{self.players}")
                    for i in self.players[:orangesrice + bluesrice]:#チームごとの人数*2
                        sql = f"SELECT ign from playerdata WHERE id='{i}';"#当選したプレイヤーの名前からidを入手
                        c.execute(sql)#sqlを実行
                        did = c.fetchone()[0]#ignを代入
                        self.lucky.append(did)
                    blue = self.lucky[:bluesrice]#シャッフルしたリストの中からself.sriceというチームごとの人数が入った変数を使ってスライス
                    orange = self.lucky[bluesrice:]
                    # for playerid in self.players[:bluesrice+orangesrice]:#当選したプレイヤー10人の名前をスライスでfor入
                    #     self.already[playerid] = +1#辞書"already"に当選したプレイヤーのid+プレイ回数+1を追加（何回休み家のシステムのため）
                    print(f"Blue:{blue}")#ブルーチーム
                    await log_c.send(f"Blue:{blue}")
                    print(f"Orange:{orange}")#オレンジチーム
                    await log_c.send(f"Orange:{orange}")
                    bjoin = '\n'.join(blue)
                    ojoin = '\n'.join(orange)
                    embed=discord.Embed(title="Team", color=0xffffff)
                    embed.add_field(name="Blue", value=f"```\n{bjoin}```", inline=False)#Blueチームにjoinで改行しながらリストblueを入れる
                    embed.add_field(name="Orange", value=f"```\n{ojoin}```", inline=False)#orangeチームにjoinで改行しながらリストorangeを入れる
                    await ctx.channel.send(embed=embed)#チーム分けを送信
                    c.close()
                elif str(reaction) == '🔚':#つけられたリアクションが🔚の場合
                    await ctx.channel.send("募集をキャンセルします")
        else:
            await ctx.channel.send("管理者のみ使用可能です")
    
    @commands.command()
    async def changeplayer(self, ctx, before: str, after: str):
        if ctx.author.guild_permissions.administrator or ctx.message.guild.get_role(741998241989525575) in ctx.message.author.roles:
            locate = self.lucky.index(before)
            self.lucky[locate] = after
            blue = self.lucky[:self.bluesrice]#シャッフルしたリストの中からself.sriceというチームごとの人数が入った変数を使ってスライス
            orange = self.lucky[self.bluesrice:self.orangesrice*2]
            embed=discord.Embed(title="Team", color=0xffffff)
            embed.add_field(name="Blue", value='\n'.join(blue), inline=False)#Blueチームにjoinで改行しながらリストblueを入れる
            embed.add_field(name="Orange", value='\n'.join(orange), inline=False)#orangeチームにjoinで改行しながらリストorangeを入れる
            await ctx.channel.send(embed=embed)#チーム分けを送信
        else:
            await ctx.send("管理者のみ使用可能です")

    @commands.command()
    async def getmember(self, ctx, ign: str):
        c = self.conn.cursor()
        sql = f'select id from playerdata where ign = "{ign}"'
        c.execute(sql)
        id = c.fetchone()
        member = self.bot.get_user(int(id[0]))
        # await ctx.send(member.name)
        await ctx.send(member)
        
    @getmember.error#スタートコマンドのエラーハンドリング
    async def getmember_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):#引数が足りないエラー
            await ctx.send("UPLAYIDを指定してください")
        if isinstance(error, commands.errors.CommandInvokeError):#埋め込みに入れる要素がないときのエラー
            await ctx.send("該当するメンバーがいません")

    @commands.command()
    async def playerlist(self, ctx, guildid = 722059814154534932):
        playerlist = []
        embed=discord.Embed(title="Players", color=0xffffff)
        for player in  self.players:
            c = self.conn.cursor()
            sql = f'select ign from playerdata where id = "{player}"'
            c.execute(sql)
            ign = c.fetchone()
            joinuser = self.bot.get_user(player)
            res = f"```{joinuser.name}:{ign[0]}```"
            playerlist.append(res)
        a = '\n'.join(playerlist)
        embed.add_field(name="All", value=f"```{a}```", inline=False)
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def shuffle(self, ctx):
        random.shuffle(self.lucky)
        blue = self.lucky[:self.bluesrice]
        orange = self.lucky[self.bluesrice:]
        bjoin = '\n'.join(blue)
        ojoin = '\n'.join(orange)
        embed=discord.Embed(title="Team", color=0xffffff)
        embed.add_field(name="Blue", value=f"```\n{bjoin}```", inline=False)#Blueチームにjoinで改行しながらリストblueを入れる
        embed.add_field(name="Orange", value=f"```\n{ojoin}```", inline=False)#orangeチームにjoinで改行しながらリストorangeを入れる
        await ctx.channel.send(embed=embed)#チーム分けを送信


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        guild = reaction.message.guild
        if user.id == 731483416163516486:
            #print("It's bot")
            return
        elif str(reaction.emoji) != '👍' and str(reaction.emoji) != '❌':
            #print("Not this reaction")
            return
        elif self.recruitid != reaction.message.id:
            #print(f"messageid:{self.recruitid} != reactionid:{reaction.message.id}")
            #print("not this massage")
            return
        elif str(reaction.emoji) == '❌':   
            if user.id in self.players:
                self.players.remove(user.id)
                await self.recruitm.edit(content=f"カスタムマッチの募集を始めます\n参加したい人は👍を押してください\n参加をキャンセルする場合は❌を押してください\n現在の参加プレイヤー数:**{len(self.players)}**")
                try:
                    await user.send('参加を取り消しました')
                except discord.errors.Forbidden:
                    print(f"Failed to send cancel message Name:{user.name}")
            else:
                await user.send("参加していないためキャンセルできませんでした")
            for mreaction in reaction.message.reactions:
                await mreaction.remove(user)
        else:
            print("Join:👍")
            userid = user.id
            if userid not in self.already:
                self.already[userid] = 0
            c = self.conn.cursor()
            sql = f"SELECT COUNT(1) FROM playerdata WHERE id = {int(userid)}"
            c.execute(sql)
            if c.fetchone()[0]:
                if userid in self.players:
                    print("You already joined")
                    return
                self.players.append(userid)
                player = guild.get_member(userid)
                print(f"Add player:{userid} NAME:{player.name}")
                await self.recruitm.edit(content=f"カスタムマッチの募集を始めます\n参加したい人は👍を押してください\n参加をキャンセルする場合は❌を推してください\n現在の参加プレイヤー数:**{len(self.players)}**")
                #print(self.players)
                c.close()
            else:
                await user.create_dm()
                dmid = user.dm_channel.id
                await reaction.remove(user)
                try:
                    await user.send("**UplayID**が未登録です。\n**UplayID**を送信してください\nまた**__IDを送信したあとに募集のメッセージにもう一度リアクションをつけてください__**")
                except discord.errors.Forbidden:
                    print(f"Failed to send message {user.id}Name:{user.name}")
                print(f"Send to message {userid}")
                await user.create_dm()
                def check(m):
                    return userid == m.author.id and dmid == m.channel.id
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout = 60)
                except asyncio.TimeoutError:
                    await user.send('タイムアウトしました\nbotがメッセージ送信されてから60秒以内にIDを送ってください')
                else:
                    sql = f'select id from playerdata where id = {userid}'
                    c.execute(sql)
                    uplayids = c.fetchall()
                    print(uplayids)
                    if len(uplayids) > 0:
                        await user.send("既に登録されています")
                        return
                    else:
                        sql = 'insert into playerdata values (%s, %s)'
                        c.execute(sql, (msg.author.id, msg.content))
                        c.close()
                        print(f"Register player Name:{msg.content}")
                        await user.send(f"UplayIDを:**{msg.content}**で登録しました")


def setup(bot):
     bot.add_cog(normal(bot))