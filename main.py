from discord.ext import commands
import os

INITIAL_EXTENSIONS = [
    'cogs.normal',
]

class MyBot(commands.Bot):
    def __init__(self, command_prefix):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(command_prefix)
        for cog in INITIAL_EXTENSIONS:
            self.load_extension(cog)

    async def on_ready(self):
        print(f"{self.user.name} is Ready.")

if __name__ == '__main__':
    bot = MyBot(command_prefix='n!')
    bot.load_extension('dispander')
    bot.run(os.environ['']) # Botのトークン
