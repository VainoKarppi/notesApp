$body = @{
    "username"="admin"
    "password"="admin"
   } | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/" -Method POST -Body $body