$postParams = @{username='admin';password='admin'}
Invoke-WebRequest -Uri "http://localhost:8000/" -Method POST -Body $postParams