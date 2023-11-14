from API.handlers.spotify import spotify_handler
from API.models.twitch.events import Event


def solve_event(event: Event):
    event_type = event.subscription.type

    if event_type == "channel.channel_points_custom_reward_redemption.add":
        solve_channel_points_event(event=event)
        return


def solve_channel_points_event(event: Event):
    reward_name = event.event.reward.title.lower()
    if "song request" in reward_name:
        link = event.event.user_input
        user_name = event.event.broadcaster_user_login
        spotify_handler.add_song_to_queue(link=link, user_name=user_name)

    print("EVENT IGNORED")
