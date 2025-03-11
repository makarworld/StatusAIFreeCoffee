# AT FIRST: 
# docker build -f pybase.Dockerfile -t pybase .
FROM pybase AS base

LABEL maintainer="Make t.me/abuztrade"

ENTRYPOINT ["python", "bot.py"]
