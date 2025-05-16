# Script to replace terms across all files
$replacements = @{
    'autocura' = 'autocura'
    'autocura' = 'autocura'
    'gerador' = 'gerador'
    'gerador' = 'gerador'
    'portal' = 'portal'
}

# Get all files recursively
$files = Get-ChildItem -Recurse -File

foreach ($file in $files) {
    # Skip binary files and git directory
    if ($file.FullName -match '\.git|\.(exe|dll|so|dylib|bin|pyc|pyo|pyd)$') {
        continue
    }

    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction Stop
        
        $modified = $false
        foreach ($key in $replacements.Keys) {
            if ($content -match [regex]::Escape($key)) {
                $content = $content -replace [regex]::Escape($key), $replacements[$key]
                $modified = $true
            }
        }

        if ($modified) {
            Write-Host "Updating file: $($file.FullName)"
            $content | Set-Content $file.FullName -NoNewline
        }
    }
    catch {
        Write-Host "Error processing file $($file.FullName): $_"
    }
}

Write-Host "Replacement complete!" 