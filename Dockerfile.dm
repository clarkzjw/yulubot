FROM python:3

ADD dm.py /dm.py

CMD [python3, dm.py]
