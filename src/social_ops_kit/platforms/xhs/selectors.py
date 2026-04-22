from __future__ import annotations

SEARCH_TIMEOUT_MS = 60_000
PUBLISH_TIMEOUT_MS = 120_000
CREATOR_TIMEOUT_MS = 60_000

SEARCH_DEFAULT_COUNT = 20
SEARCH_MAX_COUNT = 500
SEARCH_DEFAULT_TIMEOUT_MS = 60_000
SEARCH_MAX_NO_DATA_RETRIES = 3

SEARCH_FILTER_MAP = {
    "sort_by": {
        "general": "综合",
        "latest": "最新",
        "most_liked": "最多点赞",
        "most_commented": "最多评论",
        "most_collected": "最多收藏",
    },
    "note_type": {
        "all": "不限",
        "video": "视频",
        "image": "图文",
    },
    "publish_time": {
        "all": "不限",
        "day": "一天内",
        "week": "一周内",
        "half_year": "半年内",
    },
    "search_scope": {
        "all": "不限",
        "viewed": "已看过",
        "not_viewed": "未看过",
        "following": "已关注",
    },
}

PUBLISH_URL = "https://creator.xiaohongshu.com/publish/publish"
CREATOR_NOTES_URL = "https://creator.xiaohongshu.com/publish/published"
