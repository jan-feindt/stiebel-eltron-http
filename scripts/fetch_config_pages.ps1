# Fetch heating and hot water configuration pages from ISG
# Run this script from the repository root

$base = "http://servicewelt.localiot"
$outdir = "scripts/testdata"

# Heating pages (4,2 series)
$heating_pages = @("/?s=4,2", "/?s=4,2,0", "/?s=4,2,1", "/?s=4,2,2", "/?s=4,2,3", "/?s=4,2,4", "/?s=4,2,5", "/?s=4,25")

# Hot water pages (4,3 series)
$hotwater_pages = @("/?s=4,3", "/?s=4,3,0", "/?s=4,3,1", "/?s=4,3,2", "/?s=4,3,3", "/?s=4,3,4", "/?s=4,3,5", "/?s=4,3,6", "/?s=4,3,7")

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Fetching Heating Configuration Pages" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

foreach ($page in $heating_pages) {
    Write-Host "`nFetching $page in all languages..." -ForegroundColor Yellow
    python scripts/tools/fetch_testdata.py --base $base --endpoints $page --all-languages --outdir $outdir --timeout 60
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Warning: Failed to fetch $page" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 500
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Fetching Hot Water Configuration Pages" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

foreach ($page in $hotwater_pages) {
    Write-Host "`nFetching $page in all languages..." -ForegroundColor Yellow
    python scripts/tools/fetch_testdata.py --base $base --endpoints $page --all-languages --outdir $outdir --timeout 60
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Warning: Failed to fetch $page" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 500
}

Write-Host "`n=====================================" -ForegroundColor Green
Write-Host "Fetch Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "`nFetched files are in: $outdir" -ForegroundColor White

# Count files
$count = (Get-ChildItem "$outdir/*_4_*.html" -ErrorAction SilentlyContinue).Count
Write-Host "Total configuration page files: $count" -ForegroundColor White
