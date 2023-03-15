import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class Scraper:
    def __init__(self, youtube):
        self.youtube = youtube

    def get_channel_videos_id(self, name, channel_ids):
        channel_data = pd.DataFrame(self.get_channel_stats(channel_ids))
        return channel_data.loc[channel_data["channel_name"] == name, "playlist_id"].iloc[0]

    def get_channel_stats(self, channel_ids):
        response = self.youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=",".join(channel_ids)
        ).execute()

        data = []
        for channel in range(len(channel_ids)):
            data.append(dict(
                channel_name=response["items"][channel]["snippet"]["title"],
                sub_count=response["items"][channel]["statistics"]["subscriberCount"],
                view_count=response["items"][channel]["statistics"]["viewCount"],
                video_count=response["items"][channel]["statistics"]["videoCount"],
                playlist_id=response["items"][channel]["contentDetails"]["relatedPlaylists"]["uploads"],
            ))
        return data

    def visualize_channel_stats(self, channel_ids, x_key="channel_name", y_key="sub_count"):
        data = pd.DataFrame(self.get_channel_stats(channel_ids))
        data["sub_count"] = pd.to_numeric(data["sub_count"])
        data["view_count"] = pd.to_numeric(data["view_count"])
        data["video_count"] = pd.to_numeric(data["video_count"])

        sns.set(rc={'figure.figsize': (10, 8)})
        ax = sns.barplot(x=x_key, y=y_key, data=data)
        plt.show()

    def get_playlist_video_ids(self, playlist_id):
        video_ids = []

        response = self.youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
        ).execute()

        for i in range(len(response["items"])):
            video_ids.append(response["items"][i]["contentDetails"]["videoId"])

        next_page_token = response.get("nextPageToken")
        more_pages = True

        while more_pages:
            if next_page_token is None:
                more_pages = False
            else:
                response = self.youtube.playlistItems().list(
                    part="contentDetails",
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()

                for i in range(len(response["items"])):
                    video_ids.append(response["items"][i]["contentDetails"]["videoId"])

                next_page_token = response.get("nextPageToken")

        return video_ids

    def get_video_details(self, video_ids):
        all_video_stats = []
        for i in range(0, len(video_ids), 50):
            response = self.youtube.videos().list(
                part="snippet,statistics",
                id=",".join(video_ids[i:i+50])
            ).execute()

            for video in response["items"]:
                video_stats = dict(
                    title=video["snippet"]["title"],
                    published_date=video["snippet"]["publishedAt"],
                    view_count=video["statistics"]["viewCount"],
                    like_count=video["statistics"]["likeCount"],
                    comment_count=video["statistics"]["commentCount"],
                )
                all_video_stats.append(video_stats)

        return all_video_stats

    def visualize_video_details(self, video_details):

        video_data = pd.DataFrame(video_details)

        video_data["published_date"] = pd.to_datetime(video_data["published_date"]).dt.date
        video_data["view_count"] = pd.to_numeric(video_data["view_count"])
        video_data["like_count"] = pd.to_numeric(video_data["like_count"])
        video_data["comment_count"] = pd.to_numeric(video_data["comment_count"])

        top10_videos = video_data.sort_values(by="view_count", ascending=False).head(10)

        sns.set(rc={'figure.figsize': (21, 8)})

        ax = sns.barplot(x="view_count", y="title", data=top10_videos)
        plt.show()

    def get_top_channels_by_search(self, query: str, results: int=10) -> list[dict[str:str]]:
        res = self.youtube.search().list(
            part="snippet",
            maxResults=results if results <= 25 else 25,
            q=query,
            type="video"
        ).execute()

        channels = []
        for video in res["items"]:
            data = dict(
                channel_name=video["snippet"]["channelTitle"],
                channel_id=video["snippet"]["channelId"]
            )
            if data not in channels:
                channels.append(data)

        return channels
    
    def get_top_videos_by_search(self, query: str, results: int=10) -> list[dict[str:str]]:
        res = self.youtube.search().list(
            part="snippet",
            maxResults=results if results <= 25 else 25,
            q=query,
            type="video"
        ).execute()

        return [dict(
                video_id= vid["id"]["videoId"],
                video_titel=vid["snippet"]["title"]
            ) for vid in res["items"]]
    
    def get_regions_categories(self, region):
        res = self.youtube.videoCategories().list(
            part="snippet",
            regionCode=region
        ).execute()
        return [item["snippet"]["title"] for item in res["items"]]