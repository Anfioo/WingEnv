[CmdletBinding()]
param(
    [string]$PrivateKeyPath,
    [string]$PublicKeyPath,
    [string]$UpdaterEndpoint = "https://github.com/Anfioo/WingEnv/releases/latest/download/latest.json",
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if ([string]::IsNullOrWhiteSpace($PrivateKeyPath)) {
    $PrivateKeyPath = Join-Path $projectRoot ".key\wingenv.key"
}

if ([string]::IsNullOrWhiteSpace($PublicKeyPath)) {
    $PublicKeyPath = Join-Path $projectRoot ".key\wingenv.key.pub"
}

function Get-TauriSigningKey {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Name file not found: $Path`nGenerate it with: pnpm.cmd tauri signer generate -w `"$PrivateKeyPath`""
    }

    $value = (Get-Content -LiteralPath $Path -Raw).Trim()
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "$Name file is empty: $Path"
    }

    try {
        $decoded = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($value))
    }
    catch {
        throw "$Name is not a Tauri signer key in Base64 format: $Path"
    }

    $lines = @($decoded -split "\r?\n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($lines.Count -lt 2 -or -not $lines[0].StartsWith("untrusted comment:")) {
        throw "$Name is incomplete or invalid: $Path"
    }

    return $value
}

if (-not [Uri]::IsWellFormedUriString($UpdaterEndpoint, [UriKind]::Absolute)) {
    throw "UpdaterEndpoint must be an absolute URL: $UpdaterEndpoint"
}

$pnpm = Get-Command "pnpm.cmd" -ErrorAction SilentlyContinue
if ($null -eq $pnpm) {
    throw "pnpm.cmd was not found. Install pnpm before building WingEnv."
}

$privateKey = Get-TauriSigningKey -Path $PrivateKeyPath -Name "Private key"
$publicKey = Get-TauriSigningKey -Path $PublicKeyPath -Name "Public key"

$previousPrivateKey = $env:TAURI_SIGNING_PRIVATE_KEY
$previousPassword = $env:TAURI_SIGNING_PRIVATE_KEY_PASSWORD
$temporaryConfigPath = Join-Path ([IO.Path]::GetTempPath()) "wingenv-tauri-$PID-$([Guid]::NewGuid().ToString('N')).json"

try {
    $env:TAURI_SIGNING_PRIVATE_KEY = $privateKey

    if ($null -eq $env:TAURI_SIGNING_PRIVATE_KEY_PASSWORD) {
        $securePassword = Read-Host "Updater private key password (press Enter if none)" -AsSecureString
        $passwordPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
        try {
            $env:TAURI_SIGNING_PRIVATE_KEY_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($passwordPointer)
        }
        finally {
            [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passwordPointer)
        }
    }

    $localConfig = @{
        plugins = @{
            updater = @{
                pubkey = $publicKey
                endpoints = @($UpdaterEndpoint)
            }
        }
        bundle = @{
            createUpdaterArtifacts = $true
        }
    }

    $configJson = $localConfig | ConvertTo-Json -Depth 5
    [IO.File]::WriteAllText($temporaryConfigPath, $configJson, [Text.UTF8Encoding]::new($false))

    Push-Location $projectRoot
    try {
        if (-not $SkipInstall) {
            Write-Host "Installing frontend dependencies..."
            & $pnpm.Source install --frozen-lockfile
            if ($LASTEXITCODE -ne 0) {
                throw "pnpm install failed with exit code $LASTEXITCODE"
            }
        }

        Write-Host "Building signed WingEnv NSIS and updater bundles..."
        Write-Host "Updater endpoint: $UpdaterEndpoint"
        & $pnpm.Source exec tauri build --bundles "nsis,updater" --config $temporaryConfigPath
        if ($LASTEXITCODE -ne 0) {
            throw "Tauri build failed with exit code $LASTEXITCODE"
        }

        $bundleDirectory = Join-Path $projectRoot "src-tauri\target\release\bundle"
        Write-Host "Build completed: $bundleDirectory"
        Get-ChildItem -LiteralPath $bundleDirectory -Recurse -File |
            Where-Object { $_.Extension -in ".exe", ".msi", ".zip", ".sig" } |
            Select-Object -ExpandProperty FullName
    }
    finally {
        Pop-Location
    }
}
finally {
    if (Test-Path -LiteralPath $temporaryConfigPath) {
        Remove-Item -LiteralPath $temporaryConfigPath -Force
    }

    $env:TAURI_SIGNING_PRIVATE_KEY = $previousPrivateKey
    $env:TAURI_SIGNING_PRIVATE_KEY_PASSWORD = $previousPassword
}
