# Re-fetch WCCI pages with proper language switching
$base = "http://servicewelt.localiot"
$outdir = "scripts/testdata"

$languages = @{
    "cs" = "ČESKY"; "da" = "DANSK"; "de" = "DEUTSCH"; "en" = "ENGLISH"
    "es" = "ESPAÑOL"; "fi" = "SUOMI"; "fr" = "FRANÇAIS"; "hu" = "MAGYAR"
    "it" = "ITALIANO"; "nl" = "NEDERLANDS"; "pl" = "POLSKI"; "sv" = "SVENSKA"
}

foreach ($lang in $languages.Keys | Sort-Object) {
    $langName = $languages[$lang]
    $outfile = "$outdir/s_4_25_$lang.html"
    Write-Host "`nFetching $lang ($langName)..." -ForegroundColor Cyan
    try {
        $null = Invoke-WebRequest -Uri "$base/?s=5,3&dspBtnSprache=$langName" -SessionVariable session -TimeoutSec 30
        Start-Sleep -Seconds 3
        $wcciPage = Invoke-WebRequest -Uri "$base/?s=4,25" -WebSession $session -TimeoutSec 30
        [System.IO.File]::WriteAllText($outfile, $wcciPage.Content, [System.Text.Encoding]::UTF8)
        $detectedLang = if ($wcciPage.Content -match 'eingestelle_sprache.*?<strong>.*?(\w+)') { $matches[1] } else { "?" }
        Write-Host "  Saved - Detected: $detectedLang" -ForegroundColor $(if($detectedLang -eq $langName){'Green'}else{'Yellow'})
    } catch {
        Write-Host "  Error: $_" -ForegroundColor Red
    }
    Start-Sleep -Seconds 2
}
