FROM python:3.12

COPY ./dejavu /usr/share/fonts/truetype

WORKDIR /app/backend
COPY ./requirements.txt ./
RUN pip install  -r ./requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

COPY ./ .
EXPOSE 8000
ENV PYTHONPATH=/backend
CMD ["python", "app.py"] 