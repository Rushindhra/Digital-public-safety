# Download Kaggle datasets for currency and fraud detection.
# Prerequisites:
#   1. pip install kaggle
#   2. Place kaggle.json at %USERPROFILE%\.kaggle\kaggle.json
#   3. Accept dataset terms on Kaggle website for each dataset

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Raw = Join-Path $Root "datasets\raw\kaggle"
New-Item -ItemType Directory -Force -Path $Raw | Out-Null

$Datasets = @(
    @{ Slug = "sreeharisureshkaggle/fake-currency-detection-dataset"; Dir = "fake_currency" },
    @{ Slug = "yashdogra/2000-notes"; Dir = "inr_2000_notes" },
    @{ Slug = "lnasiri007/ieeecis-fraud-detection"; Dir = "ieee_cis_fraud" },
    @{ Slug = "mlg-ulb/creditcardfraud"; Dir = "credit_card_fraud" }
)

foreach ($ds in $Datasets) {
    $dest = Join-Path $Raw $ds.Dir
    if (Test-Path $dest) {
        Write-Host "Already downloaded: $($ds.Slug)"
        continue
    }
    Write-Host "Downloading $($ds.Slug) ..."
    kaggle datasets download -d $ds.Slug -p $dest --unzip
}

Write-Host ""
Write-Host "Kaggle download complete. Run: python scripts/process_kaggle_datasets.py"
