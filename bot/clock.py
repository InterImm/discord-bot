import requests
import click
from loguru import logger
import time


class Clock:
    """
    Clock is a module to calculate the current time and trigger actions
    """

    def __init__(self, clockapi) -> None:
        self.clockapi = clockapi

    def _current_time(self) -> dict:
        """
        _current_time retrieves the current time from clock API
        """
        try:
            r = requests.get(url=self.clockapi)
        except Exception as e:
            logger.error(f"Could not connect to {self.clockapi}\n{e}")
            return None
        r_json = r.json()
        interimm = r_json.get("interimm", {})
        return interimm

    def post_current_time(self, action, **kwargs) -> None:
        ct = self._current_time()
        if ct:
            title = "{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}".format(**ct)
            description = "in Isidis on Mars."
            post_content = action(ct, **kwargs)
        else:
            logger.error(f"Could not post current time:\n{ct}")

    def post_new_day(self, action, **kwargs) -> None:
        ct = self._current_time()
        if ct:
            post_content = action(ct, **kwargs)
        else:
            logger.error("Could not post new day")

        return {"title": title, "description": description, "content": message_content}

    def trigger_on_new_day(self, check_interval, actions, **kwargs):
        """
        trigger_on_new_day forges a message on a new day and take an action

        :param check_interval: time interval between the clock API checks.
        :type check_interval: int
        :param action: a function that defines an action to take
        """
        if not isinstance(actions, (list, tuple)):
            actions = [actions]

        st = self._current_time()
        if not st:
            raise Exception(f"Did not get current time!")
        current_day = st.get("day")

        while True:
            ct = self._current_time()
            if not ct:
                continue
            if ct.get("day") != current_day:
                for action in actions:
                    post_content = action(payload, kwargs)
                current_day = ct.get(
                    "day"
                )  # Update current_day flag and get ready for the next day
                logger.info(f"Posted to clock channel for {current_day}!")
            logger.debug(f"Not a new day yet: {ct}")
            time.sleep(check_interval)


class ActionBase:
    """
    ActionBase is the Base class of actions
    """

    def __init__(self) -> None:
        self.message_forger = {
            "current": self._forge_current_time_message,
            "daily": self._forge_new_day_message,
        }

    def _forge_new_day_message(self, ct):
        dt_string = "{year}-{month:02d}-{day:02d}".format(**ct)
        greeting = "Have a great day!"
        claim = "It's a new day on Mars!"

        return {"dt": dt_string, "greeting": greeting, "claim": claim}

    def _forge_current_time_message(self, ct):
        dt_string = "{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}".format(**ct)
        greeting = "In Isidis on Mars "
        claim = ""

        return {"dt": dt_string, "greeting": greeting, "claim": claim}

    def action(self, payload, **kwargs):

        logger.info(f"{payload}")

        raise NotImplementedError("The action method has not yet been implemented!")


class STDIO(ActionBase):
    """
    STDIO is an interface to print to the terminal
    """

    def __init__(self) -> None:
        super().__init__()

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

        logger.info(f"{message_content} {title} {description}")


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
def clockbot(webhook, clockapi, function, interval):

    cb = Clock(clockapi)
    stdio_client = STDIO()
    stdio_output = stdio_client.output

    if function == "now":
        cb.post_current_time(stdio_output, mode="current")
    elif function == "daily":
        cb.trigger_on_new_day(check_interval=interval, actions=stdio_output, mode="daily")


if __name__ == "__main__":

    # test_hook = "https://discordapp.com/api/webhooks/747174489439338516/3q3CyGbXupJevSpj7vVnbz3R2wdGqvjIwB0mDmM5PfZEgGF2UdjPAf13uyEpODN8kV6X"
    # test_clockapi = "https://marsapi.interimm.org/now"
    # ck = Clock(test_hook, test_clockapi)
    # # ck.message(content="Time on Mars", title="Clock", description="10:10")
    # print(ck._current_time())
    # ck.post_current_time()

    clockbot()

    pass
