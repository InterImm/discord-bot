from discord_webhook import DiscordWebhook, DiscordEmbed
import requests
import click
from loguru import logger
import time
from clock import ActionBase
from clock import Clock


class DiscordIO(ActionBase):
    def __init__(self, webhook):
        super().__init__()
        self.webhook = webhook

    def output(self, payload, **kwargs):

        if not kwargs.get("mode"):
            raise Exception("Please specify a mode parameter")
        else:
            message_mode = kwargs.get("mode")

        message_forger = self.message_forger.get(message_mode)
        message_payload = message_forger(payload)

        title = message_payload.get("dt")
        description = message_payload.get("greeting")
        message_content = message_payload.get("claim")

        self.hook = DiscordWebhook(url=self.webhook, content=message_content)
        embed = DiscordEmbed(title=title, description=description, color=242424)

        embed.set_author(name="Mars Clock", url="http://interimm.org/mars-clock/")
        embed.set_footer(text="by InterImm Bot")

        self.hook.add_embed(embed)

        response = self.hook.execute()

        logger.info(f"Posted to discord: {message_content} {title} {description}")


@click.command()
@click.option("--webhook", "-w", type=str, required=True, help="Webhook url")
@click.option("--function", "-f", type=str, default="now", help="Functionality")
@click.option(
    "--interval", "-i", type=int, default=60, help="waiting time for each API check"
)
@click.option(
    "--clockapi",
    "-c",
    type=str,
    default="https://marsapi.interimm.org/now",
    help="Mars Clock API",
)
def discordbot(webhook, clockapi, function, interval):

    cb = Clock(clockapi)
    discord_client = DiscordIO(webhook=webhook)
    discord_output = discord_client.output

    if function == "now":
        cb.post_current_time(discord_output, mode="current")
    elif function == "daily":
        cb.trigger_on_new_day(check_interval=interval, actions=discord_output, mode="daily")


if __name__ == "__main__":

    # test_hook = "https://discordapp.com/api/webhooks/747174489439338516/3q3CyGbXupJevSpj7vVnbz3R2wdGqvjIwB0mDmM5PfZEgGF2UdjPAf13uyEpODN8kV6X"
    # test_clockapi = "https://marsapi.interimm.org/now"
    # ck = Clock(test_hook, test_clockapi)
    # # ck.message(content="Time on Mars", title="Clock", description="10:10")
    # print(ck._current_time())
    # ck.post_current_time()

    discordbot()

    pass
