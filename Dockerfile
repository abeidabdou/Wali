FROM python:3.11.5

RUN useradd -m -u 1000 user

WORKDIR /app

COPY --chown=user:user ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user:user . /app

EXPOSE 7860

USER user

CMD ["python", "wali.py"]