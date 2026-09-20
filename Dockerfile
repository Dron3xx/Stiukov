FROM python:3.11-windowsservercore-ltsc2022

WORKDIR /app

ENV PYTHONPATH=C:\app

SHELL ["powershell", "-Command", \
        "$ErrorActionPreference = 'Stop'; \
        $ProgressPreference = 'SilentlyContinue';"]

RUN Invoke-WebRequest -Uri "https://aka.ms/download-jdk/microsoft-jdk-17-windows-x64.zip" -OutFile "openjdk.zip"

RUN Expand-Archive openjdk.zip -DestinationPath C:\Java_Tmp

RUN Remove-Item openjdk.zip

RUN $extractedFolder = (Get-ChildItem C:\Java_Tmp\jdk-* | Select-Object -First 1).FullName; \
    New-Item -ItemType Directory -Force -Path C:\Java; \
    Move-Item -Path $extractedFolder -Destination C:\Java\jdk17; \
    Remove-Item -Recurse -Force C:\Java_Tmp

ENV JAVA_HOME="C:\Java\jdk17"

RUN [Environment]::SetEnvironmentVariable( \
    'Path', \
     $env:Path + ';' + $env:JAVA_HOME + '\bin', \
    [EnvironmentVariableTarget]::Machine \
    )

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

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

CMD ["python", "run_tests.py"]