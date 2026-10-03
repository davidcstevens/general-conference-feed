from gc_podcast import collect_episodes
from feed import build_feed

if __name__ == "__main__":
    eps = collect_episodes(max_confs=6)
    build_feed(eps, "feed.xml")
