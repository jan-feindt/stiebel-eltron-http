# Fetch page s=4,25 (LEISTUNGSBEEINFLUSSUNG) for all languages
$base_url = "http://servicewelt.localiot"
$page = "/?s=4,25"
$output_dir = "scripts/testdata"

# Language codes
$languages = @{
    "de" = "DEUTSCH"
    "en" = "ENGLISH"
    "fr" = "FRANÇAIS"
    "nl" = "NEDERLANDS"
    "it" = "ITALIANO"
    "sv" = "SVENSKA"
    "pl" = "POLSKI"
    "cs" = "ČEŠTINA"
    "hu" = "MAGYAR"
    "es" = "ESPAÑOL"
    "fi" = "SUOMI"
    "da" = "DANSK"
}

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Fetching page $page for all languages" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# First, set to German to get a baseline
Write-Host "`nSetting language to German..." -ForegroundColor Yellow
Invoke-WebRequest -Uri "$base_url/?s=5,3&dspBtnSprache=DEUTSCH" -UseBasicParsing -TimeoutSec 10 | Out-Null
Start-Sleep -Milliseconds 500

foreach ($lang_code in $languages.Keys | Sort-Object) {
    $lang_name = $languages[$lang_code]
    $output_file = "$output_dir/s_4_25_$lang_code.html"
    
    Write-Host "`nFetching $page in $lang_name ($lang_code)..." -ForegroundColor Yellow
    
    # Set language
    if ($lang_code -ne "de") {
        try {
            Invoke-WebRequest -Uri "$base_url/?s=5,3&dspBtnSprache=$lang_name" -UseBasicParsing -TimeoutSec 10 | Out-Null
            Start-Sleep -Milliseconds 500
        } catch {
            Write-Host "  Error setting language: $_" -ForegroundColor Red
            continue
        }
    }
    
    # Fetch page
    try {
        $response = Invoke-WebRequest -Uri "$base_url$page" -UseBasicParsing -TimeoutSec 30
        
        # Write to file (response content is already a string)
        [System.IO.File]::WriteAllText($output_file, $response.Content, [System.Text.Encoding]::UTF8)
        
        Write-Host "  Success: $output_file" -ForegroundColor Green
        Start-Sleep -Milliseconds 500
    } catch {
        Write-Host "  Error fetching page: $_" -ForegroundColor Red
    }
}

# Restore German
Write-Host "`n`nRestoring language to German..." -ForegroundColor Yellow
Invoke-WebRequest -Uri "$base_url/?s=5,3&dspBtnSprache=DEUTSCH" -UseBasicParsing -TimeoutSec 10 | Out-Null

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "Fetch complete!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
