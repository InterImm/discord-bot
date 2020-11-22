import requests
import click
from loguru import logger
import time
from clock import ActionBase
from clock import Clock
from to_mastodon import MastodonIO
from to_discord import DiscordIO


@click.command()
@click.option("--webhook", "-w", type=str, required=True, help="Webhook url")
@click.option(
    "--mastodon_token", "-mt", type=str, required=False, help="Mastodon token"
)
@click.option(
    "--mastodon_instance", "-mi", type=str, required=False, help="Mastodon instance url"
)
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
def dailybot(webhook, clockapi, function, interval, mastodon_token, mastodon_instance):

    cb = Clock(clockapi)
    mtd_client = MastodonIO(
        mastodon_token=mastodon_token, mastodon_instance=mastodon_instance
    )
    mtd_output = mtd_client.output

    discord_client = DiscordIO(webhook=webhook)
    discord_output = discord_client.output

    if function == "now":
        cb.post_current_time(discord_output, mode="current")
        cb.post_current_time(mtd_output, mode="current")
    elif function == "daily":
        cb.trigger_on_new_day(check_interval=interval, actions=[mtd_output,discord_output], mode="daily")


if __name__ == "__main__":

    dailybot()

    pass