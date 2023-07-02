FROM python:3.8.13

# Original:
# RUN mkdir -p /home/project/multidim_vis
# WORKDIR /home/project/multidim_vis
# RUN pip install --upgrade pip
# COPY requirements.txt /home/project/multidim_vis
# RUN pip install --upgrade pip --no-cache-dir -r requirements.txt
# COPY . /home/project/multidim_vis

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . ./
CMD gunicorn -b 0.0.0.0:80 app:server