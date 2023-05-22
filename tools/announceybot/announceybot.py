import sys
import os
from discord_webhook import DiscordWebhook
from git import Repo
import subprocess

URL = os.getenv("WEBHOOK_URL")
TAG_NAME = os.getenv("TAG_NAME", sys.argv[1])


def send_to_discord(message):
    webhook = DiscordWebhook(url=URL, rate_limit_retry=True, content=message)
    if os.getenv("DEBUG", None) == None:
        return webhook.execute()
    else:
        print("Sending ...")
        print(message)


def get_tag_annotation(tagname):
    repo = Repo('.')
    tag = repo.tags[tagname]
    return tag.tag.message


def get_replacement():
    ret = subprocess.run([
        "./tools/pkghash",
        "-g", f"--tag={TAG_NAME}",
        "--template=./tools/announceybot/release-dep-update-template.md",
        ], capture_output=True)
    text = ret.stdout.decode("utf-8")
    return text


if __name__ == '__main__':
    annotation = get_tag_annotation(TAG_NAME)
    zon_update = get_replacement()
    message = f'''# TEST-RUN TEST-RUN TEST-RUN

    # New release {TAG_NAME}!

## Updates

{annotation}

## Using it

Modify your `build.zig.zon` like this:

'''
    message += zon_update + "\n"
    message += 'See the [release page](https://github.com/zigzap/zap/releases/'
    message += f'{TAG_NAME}) for more information!'
    send_to_discord(message)
