from discord.ext import commands


class normal(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.target_message = None
        self.target_channel = None

    @commands.command()
    async def init(self, ctx):
        self.target_message = await ctx.send("```diff\n-  ____ _     ___  ____  _____ ____  \n- / ___| |   / _ \/ ___|| ____|  _ \ \n-| |   | |  | | | \___ \|  _| | | | |\n-| |___| |__| |_| |___) | |___| |_| |\n- \____|_____\___/|____/|_____|____/ \n```")
        await self.target_message.add_reaction('⭕')
        await self.target_message.add_reaction('❌')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        self.target_channel = await self.bot.fetch_channel(987756711261646868)
        self.target_message = await self.target_channel.fetch_message(989001921966801017)
        notify_channel = await self.bot.fetch_channel(989520209515798558)

        if payload.member.bot:
            return
        elif payload.message_id == self.target_message.id:
            if payload.emoji.name == '⭕':
                await self.target_message.edit(content = '```md\n#  ___  ____  _____ _   _ \n / _ \|  _ \| ____| \ | |\n| | | | |_) |  _| |  \| |\n| |_| |  __/| |___| |\  |\n \___/|_|   |_____|_| \_|\n```')
                await self.target_message.remove_reaction(emoji='⭕',member=payload.member)
                await notify_channel.send(f'部室が{payload.member.mention}によって開錠されました。')
            elif payload.emoji.name == '❌':
                await self.target_message.edit(content = '```diff\n-  ____ _     ___  ____  _____ ____  \n- / ___| |   / _ \/ ___|| ____|  _ \ \n-| |   | |  | | | \___ \|  _| | | | |\n-| |___| |__| |_| |___) | |___| |_| |\n- \____|_____\___/|____/|_____|____/ \n```')
                await self.target_message.remove_reaction(emoji='❌', member=payload.member)
                await notify_channel.send(f'部室が{payload.member.mention}によって施錠されました。')
        else:
            return




def setup(bot):
     bot.add_cog(normal(bot))