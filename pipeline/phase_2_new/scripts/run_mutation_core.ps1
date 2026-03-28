Param(
    [switch]$UseCoverage
)

$ErrorActionPreference = "Stop"

Write-Host "==> Running mutation job for simulator core methods..."
Write-Host "    Target file: agpds/simulator.py"
Write-Host "    Focus tests: add_category / add_temporal / generate"

$mutmutArgs = @(
    "-m", "mutmut", "run",
    "--paths-to-mutate", "agpds/simulator.py",
    "--runner", "python -m pytest -q tests/test_simulator_sprint2.py tests/test_simulator_sprint4.py tests/test_injection.py -k `"add_category or add_temporal or generate`""
)

if ($UseCoverage) {
    $mutmutArgs += "--use-coverage"
}

& python @mutmutArgs
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "==> Mutation summary"
python -m mutmut results
exit $LASTEXITCODE
