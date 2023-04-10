import subprocess

# List of required packages
packages = [
    'setuptools',
    'requests',
    'python-dotenv',
    'haversine',
    'openpyxl',
    'typing',
]

for package in packages:
    subprocess.check_call(['pip', 'install', '--use-pep517', '--no-cache-dir', package])