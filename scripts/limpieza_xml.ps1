Get-ChildItem -Recurse -Filter "*.xml" | ForEach-Object {
    $contenido = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($contenido -match '[\x00-\x08\x0B\x0C\x0E-\x1F]') {
        Copy-Item $_.FullName "$($_.FullName).bak"
        $limpio = $contenido -replace '[\x00-\x08\x0B\x0C\x0E-\x1F]', ''
        Set-Content $_.FullName $limpio -NoNewline
        Write-Host "Limpiado: $($_.FullName)"
    }
}