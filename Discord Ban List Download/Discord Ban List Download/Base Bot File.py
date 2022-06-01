import os.path

import disnake

from bot import Bot


@Bot.slash_command(name="export_bans", description="Exports all the bans in this guild to a text file.")
async def slash_command_export_bans(inter: disnake.CommandInteraction):
    await inter.response.defer(ephemeral=True)

    bans = await inter.guild.bans(limit=None).flatten()
    ban_strings = []
    for ban in bans:
        reason = ban.reason.strip("\n") if ban.reason is not None else 'No reason specified.'
        ban_strings.append(f'{str(ban.user)} | {ban.user.id} - {reason}\n')

    with open(os.path.join('bans', f'{inter.guild.id} bans.txt'), 'w+') as file:
        file.writelines(ban_strings)

    await inter.edit_original_message(content=f"Completed exporting the bans for {inter.guild.name}!", file=disnake.File(os.path.join('bans', f'{inter.guild.id} bans.txt')))


    console_output = ''.join(ban_strings)
    print(f'{inter.guild.name} | {inter.guild.id} has just run the `{inter.application_command.name} with the following output:\n{console_output}\n')

Bot.run()
