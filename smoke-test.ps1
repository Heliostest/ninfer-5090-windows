$ErrorActionPreference = 'Stop'
$BaseUrl = 'http://127.0.0.1:39217'

Write-Host 'Checking health...'
$Health = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get -TimeoutSec 30
$Health | ConvertTo-Json -Depth 10

$Body = @{
    model = 'qwen3.8-27b-huihui-abliterated'
    messages = @(
        @{ role = 'user'; content = 'Reply with exactly: NInfer Huihui is ready.' }
    )
    # Thinking-capable Qwen models may consume a short reasoning prelude first.
    max_tokens = 128
    temperature = 0
} | ConvertTo-Json -Depth 10

Write-Host 'Sending chat completion...'
$Response = Invoke-RestMethod `
    -Uri "$BaseUrl/v1/chat/completions" `
    -Method Post `
    -ContentType 'application/json' `
    -Body $Body `
    -TimeoutSec 600

$Response | ConvertTo-Json -Depth 20
