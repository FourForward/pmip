FROM ubuntu
MAINTAINER tina_han<553630934@qq.com>
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean
RUN apt-get update
RUN apt-get install -y vim
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip3 config set global.index-url http://mirrors.aliyun.com/pypi/simple
RUN pip3 config set install.trusted-host mirrors.aliyun.com
RUN pip3 install pip -U
RUN pip3 install django
RUN pip3 install requests
RUN pip3 install uwsgi
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone
RUN apt-get install -y nginx
RUN rm /etc/nginx/sites-enabled/default
COPY default /etc/nginx/sites-enabled/
ADD PMIP.tar.gz /home/
CMD ["sh", "-c", "uwsgi -i /home/PMIP/PMIP/uwsgi.ini && nginx -g 'daemon off;'"]
