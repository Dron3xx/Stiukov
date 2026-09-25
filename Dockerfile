FROM python:3.11-windowsservercore-ltsc2022

WORKDIR /app

ENV PYTHONPATH=C:\app

SHELL ["powershell", "-Command", \
        "$ErrorActionPreference = 'Stop'; \
        $ProgressPreference = 'SilentlyContinue';"]

RUN Invoke-WebRequest ` \
    -Uri "https://aka.ms/vc14/vc_redist.x64.exe" ` \
    -OutFile "vc_redist.x64.exe"; ` \
    Start-Process ` \
        -FilePath "vc_redist.x64.exe" ` \
        -ArgumentList "/install", "/quiet", "/norestart" ` \
        -Wait; ` \
    Remove-Item -Force "vc_redist.x64.exe"

COPY requirements.txt .
COPY requirements-dev.txt .

RUN python.exe -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

CMD ["python", "run_tests.py"]