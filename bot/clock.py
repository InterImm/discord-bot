from discord_webhook import DiscordWebhook, DiscordEmbed
import requests
import click


class Clock:
    def __init__(self, webhook, clockapi) -> None:
        self.webhook = webhook
        self.clockapi = clockapi

    def _current_time(self) -> dict:
        r = requests.get(url=self.clockapi)
        r_json = r.json()
        interimm = r_json.get("interimm", {})
        return interimm

    def post_current_time(self) -> None:
        ct = self._current_time()
        title = "{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}".format(**ct)
        description = "in Isidis on Mars."
        self.message(content="Time on Mars", title=title, description=description)

    def message(self, **kwargs) -> None:

        content = kwargs.get("content")
        title = kwargs.get("title")
        description = kwargs.get("description")

        self.hook = DiscordWebhook(url=self.webhook, content=content)
        embed = DiscordEmbed(title=title, description=description, color=242424)

        embed.set_author(name="Mars Clock", url="http://interimm.org/mars-clock/")
        embed.set_footer(text="by InterImm Bot")

        self.hook.add_embed(embed)

        response = self.hook.execute()


@click.command()
@click.option("--webhook", "-w", type=str, required=True, help="Webhook url")
@click.option(
    "--clockapi",
    "-c",
    type=str,
    default="https://marsapi.interimm.org/now",
    help="Mars Clock API",
)
def clockbot(webhook, clockapi):

    cb = Clock(webhook, clockapi)
    cb.post_current_time()


if __name__ == "__main__":

    # test_hook = "https://discordapp.com/api/webhooks/747174489439338516/3q3CyGbXupJevSpj7vVnbz3R2wdGqvjIwB0mDmM5PfZEgGF2UdjPAf13uyEpODN8kV6X"
    # test_clockapi = "https://marsapi.interimm.org/now"
    # ck = Clock(test_hook, test_clockapi)
    # # ck.message(content="Time on Mars", title="Clock", description="10:10")
    # print(ck._current_time())
    # ck.post_current_time()

    clockbot()

    pass
