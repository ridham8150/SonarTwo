
import os
import subprocess

def run_sonar_scanner():
    # Path to the SonarQube scanner binary
    scanner_path = "/path/to/sonar-scanner/bin/sonar-scanner"
    
    # Set environment variables if needed
    os.environ['SONAR_SCANNER_OPTS'] = "-Xmx512m"
    
    # Run the scanner
    try:
        result = subprocess.run([scanner_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("SonarQube Scan Completed!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("SonarQube Scan Failed!")
        print(e.stderr)

if __name__ == "__main__":
    run_sonar_scanner()
