#IF RUNNING ON A WINDOWS BASED SYSTEM, START HOSTING FROM THIS FILE! SIMPLY RUN THIS FILE FROM THE TERMINAL!
#THIS CAN BE RUN BY COPY AND PASTING THIS INTO THE TERMINAL:
#.\start.ps1
docker compose up -d --build
$addr = docker compose port app 8000
$host,$port = $addr -split ":",2
$host = "127.0.0.1"
$Url = "http://$host:$port"
Write-Host "App is starting… $Url"
Start-Process $Url