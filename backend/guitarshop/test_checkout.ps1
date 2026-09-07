$loginBody = @{ email = "checkoutuser1@test.com"; password = "Test1234!" } | ConvertTo-Json
$loginResp = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login/" -Method POST -ContentType "application/json" -Body $loginBody -UseBasicParsing
$token = ($loginResp.Content | ConvertFrom-Json).access
Write-Host "Token obtinut: $($token.Substring(0,20))..."

for ($i=1; $i -le 12; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:8000/api/cart/checkout/" -Method POST `
            -ContentType "application/json" -Headers @{Authorization = "Bearer $token"} `
            -Body '{"items":{}}' -UseBasicParsing
        Write-Host "Status: $($resp.StatusCode)"
    } catch {
        Write-Host "Status: $($_.Exception.Response.StatusCode.value__)"
    }
}