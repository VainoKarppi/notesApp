$username = "admin"
$password = "admin"
$url = "http://127.0.0.1:8000/notes"
$headers = @{
    Authorization = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($username):$($password)"))
}
Invoke-WebRequest -Uri $url -Headers $headers


# CREATE TEST NOTE FIRST WITH SUBJECT: test
$body = @{
    "subject"="test"
}
Invoke-WebRequest -Uri "http://localhost:8000/note" -Method Get -Headers $headers -Body $body



