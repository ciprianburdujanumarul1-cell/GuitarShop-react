for ($i=1; $i -le 5; $i++) {
    $body = @{ email = "test$i@test.com"; password = "Test1234!" } | ConvertTo-Json
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/register/" -Method POST -ContentType "application/json" -Body $body
        Write-Host "Status: $($response.StatusCode)"
    } catch {
        Write-Host "Status: $($_.Exception.Response.StatusCode.value__)"
    }
}