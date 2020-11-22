import requests
import click
from loguru import logger
import time
from mastodon import Mastodon
from clock import ActionBase
from clock import Clock


class MastodonIO(ActionBase):
    def __init__(self, mastodon_token, mastodon_instance):
        super().__init__()
        self.mastodon_token = mastodon_token
        self.mastodon_instance = mastodon_instance
        self._client()

    def _client(self):
        if (self.mastodon_token is not None) and (self.mastodon_instance is not None):
            self.mastodon = Mastodon(
                access_token=self.mastodon_token,
                api_base_url=self.mastodon_instance,
            )
        else:
            raise Exception(f"mastodon client is not defined")

    def output(self, payload, **kwargs):

        if not kwargs.get("mode"):
            raise Exception("Please specify a mode parameter")
        else:
            message_mode = kwargs.get("mode")

        message_forger = self.message_forger.get(message_mode)
        message_payload = message_forger(payload)

        title = message_payload.get("dt")
        greeting = message_payload.get("greeting")
        claim = message_payload.get("claim")

        mastodon_message = f"{title} {greeting} Check the current time here: http://interimm.org/mars-clock #marsclock"
        self.mastodon.toot(mastodon_message)

        logger.info(f"{mastodon_message}")


@click.command()
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
def clockbot(clockapi, function, interval, mastodon_token, mastodon_instance):

    cb = Clock(clockapi)
    mtd_client = MastodonIO(
        mastodon_token=mastodon_token, mastodon_instance=mastodon_instance
    )
    mtd_output = mtd_client.output

    if function == "now":
        cb.post_current_time(mtd_output, mode="current")
    elif function == "daily":
        cb.trigger_on_new_day(check_interval=interval, actions=mtd_output, mode="daily")


if __name__ == "__main__":

    # test_hook = "https://discordapp.com/api/webhooks/747174489439338516/3q3CyGbXupJevSpj7vVnbz3R2wdGqvjIwB0mDmM5PfZEgGF2UdjPAf13uyEpODN8kV6X"
    # test_clockapi = "https://marsapi.interimm.org/now"
    # ck = Clock(test_hook, test_clockapi)
    # # ck.message(content="Time on Mars", title="Clock", description="10:10")
    # print(ck._current_time())
    # ck.post_current_time()

    clockbot()

    pass
