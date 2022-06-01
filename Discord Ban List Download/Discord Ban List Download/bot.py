import datetime
import json
import os

import disnake
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv()


def read_json(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


def write_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
    return data


class CustomBotObject(commands.InteractionBot):

    def __init__(self, intents, **options):
        # noinspection PyTypeChecker
        super().__init__(
            case_insensitive=True,
            help_command=None,
            intents=intents,
            owner_ids={owner id here,},
            test_guilds=[guild id here],
            **options
        )

        self.ready_count = 0
        self.disconnect_time = None

    async def on_ready(self):
        if os.path.exists("./invite.txt") is False:
            with open("invite.txt", "w+") as invite_file:
                invite_file.write(f"https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot%20applications.commands")

        if self.ready_count < 1:
            print(f"[{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Logged in as {str(self.user)}")
            print("")
        else:
            if int(str(self.ready_count)[-1]) == 1:
                suffix = "st"
            elif int(str(self.ready_count)[-1]) == 2:
                suffix = "nd"
            elif int(str(self.ready_count)[-1]) == 3:
                suffix = "rd"
            else:
                suffix = "th"
            print(f"[{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Re-readied as {str(self.user)} for the {self.ready_count}{suffix} time.")
        self.ready_count += 1

    async def on_disconnect(self):
        if self.disconnect_time is None:
            print(f"[{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Disconnected from Discord...")
            self.disconnect_time = datetime.datetime.now()

    async def on_resumed(self):
        if self.ready_count >= 1:
            print(f"[{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Resumed as {str(self.user)}")

    # TODO: Make sure error messages are correct and work well.
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            if ctx.guild.id in self.info["CNF Enabled Guilds"]:
                await ctx.reply(content=f"That is not a command! Try use `{ctx.prefix}help` for a list of commands.", delete_after=15, mention_author=False)
        elif isinstance(error, commands.MissingPermissions):
            ctx.command.reset_cooldown(ctx)
            perms = ""
            perm_len = len(error.missing_permissions)
            for permission in error.missing_permissions:
                perms += f"{permission}"
                perm_len -= 1
                if perm_len > 1:
                    perms += ", "
                elif perm_len == 1:
                    perms += " and "
            await ctx.reply(f":x: **You don't have permission to do that! You must have the `{perms}` permission{'' if int(len(error.missing_permissions)) < 2 else 's'} if you want to use that command!**")
        elif isinstance(error, commands.CommandOnCooldown):
            delay = datetime.timedelta()
            if error.retry_after > 3600:
                delay += datetime.timedelta(hours=(error.retry_after // 60) // 60)
            elif error.retry_after > 60:
                delay += datetime.timedelta(minutes=error.retry_after // 60)
            else:
                delay += datetime.timedelta(seconds=round(error.retry_after))

            cooldown_time = datetime.datetime.now() + delay

            await ctx.reply(content=f":x: **This command is on a cooldown, you can use this again {disnake.utils.format_dt(cooldown_time, style='R')} or when this message deletes.**", delete_after=error.retry_after)
        elif isinstance(error, commands.MissingRequiredArgument):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(content=f":x: **You need to specify the:** `{error.param.name}` **parameter.**\n*You can use* `{ctx.prefix}help {ctx.command.name}` *to get the proper syntax.*", mention_author=False)
        elif isinstance(error, commands.BotMissingPermissions):
            ctx.command.reset_cooldown(ctx)
            perms = ""
            perm_len = len(error.missing_permissions)
            for permission in error.missing_permissions:
                if permission == disnake.Permissions.send_messages:
                    return
                perms += f"{permission}"
                perm_len -= 1
                if perm_len > 1:
                    perms += ", "
                elif perm_len == 1:
                    perms += " and "
            await ctx.reply(content=f":x: **The bot doesn't have permission to do that! You must give the bot the `{perms}` permission{'' if int(len(error.missing_permissions)) < 2 else 's'} if you want to use that command!**", mention_author=False)
        elif isinstance(error, commands.BadArgument):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(content=f":x: **Invalid argument passed, you might be using the command wrong... Try using `{ctx.prefix}help {ctx.command.name}` to get the proper syntax.**", mention_author=False)
        elif isinstance(error, commands.NoPrivateMessage):
            ctx.command.reset_cooldown(ctx)
            await ctx.reply(content=f":x: **You can only use that command in a server!**", mention_author=False)
        elif hasattr(error, "original"):
            raise error.original
        else:
            raise error

    def run(self):
        super().run(os.getenv("TOKEN"), reconnect=True)


Bot = CustomBotObject(
    intents=disnake.Intents(bans=True, guilds=True)
)
