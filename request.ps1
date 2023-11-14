$username = "admin"
$password = "admin"
$uri = "http://localhost:8000/test"
$headers = @{
    Authorization = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($username):$($password)"))
}
Invoke-WebRequest -Uri $uri -Headers $headers


