# router-reboot-docker

🔄 A Docker container for automated Buffalo router rebooting

## Overview

This tool provides a Docker container that automates the rebooting of Buffalo routers. It uses browser automation to handle the login process and UI interactions, enabling scheduled router reboots.

## Key Features

- Automated browser control using Selenium
- Headless mode for background operation
- Automated login authentication
- Automated reboot process
- Automatic retry on failures
- Detailed logging

## Prerequisites

- Docker
- Docker Compose (optional)
- Network access to the router

## Directory Structure

```
router-reboot-docker/
│
├── .github/                        # GitHub Actions configuration
│   └── workflows/                  # CI/CD workflow definitions
│       └── docker-publish.yml      # Docker image publishing workflow
│
├── src/                           # Source code
│   └── reboot.py                  # Main router reboot script
│
├── config/                        # Configuration files
│   ├── .gitkeep                  # Keep empty directory in git
│   └── config.example.yml        # Example configuration file
│
├── scripts/                       # Utility scripts
│   ├── build.sh                  # Build Docker image
│   ├── run.sh                    # Run Docker container
│   └── cron-reboot.sh           # Scheduled execution script
│
├── logs/                         # Application logs
│   └── .gitkeep                 # Keep empty directory in git
│
├── .gitignore                    # Git ignore rules
├── .dockerignore                 # Docker build ignore rules
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Docker image definition
├── requirements.txt              # Python dependencies
├── LICENSE                       # Apache 2.0 license
└── README.md                     # Project documentation
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ngc-shj/router-reboot-docker.git
cd router-reboot-docker
```

2. Prepare the configuration file:
```bash
cp config/config.example.yml config/config.yml
```

3. Edit the configuration file:
```bash
vim config/config.yml
```

Configuration example:
```yaml
router:
  connection:
    base_url: "http://192.168.11.1"
    timeout_seconds: 30
  
  auth:
    username: "admin"
    password: ""
    
  endpoints:
    login: "login.html"
    reboot: "save_init.html"
  
  options:
    verify_ssl: false
    retry_count: 3
    retry_interval_seconds: 5
    mobile_mode: false
```

## Usage

### Building

Build the Docker image using the build script:

```bash
./scripts/build.sh
```

### Running

Launch the container using the run script:

```bash
./scripts/run.sh
```

### Script Options

The `run.sh` script supports the following options:

```bash
Usage: ./scripts/run.sh [OPTIONS]

Options:
  -h, --help           Show this help message
  -c, --config <dir>   Specify config directory (default: ./config)
  -t, --tag <tag>      Specify image tag (default: latest)
  -n, --name <name>    Specify container name (default: router-reboot)
```

### Using Docker Compose

Alternatively, you can use Docker Compose:

```bash
docker-compose up -d
```

## Scheduled Execution

To schedule the router reboot to run daily at 5 AM, follow these steps:

### Setup

1. Make the cron script executable:
```bash
chmod +x scripts/cron-reboot.sh
```

2. Add to crontab:
```bash
# Edit crontab
crontab -e

# Add the following line (replace with your actual path)
0 5 * * * /path/to/router-reboot-docker/scripts/cron-reboot.sh
```

### Logging

The script logs all operations to `logs/router-reboot.log`. The log entries include:
- Timestamp for each operation
- Container startup and cleanup
- Success/failure status

To monitor the execution:
```bash
# View the latest log entries
tail -f logs/router-reboot.log

# Check the last execution
grep "Starting router reboot process" logs/router-reboot.log | tail -n 1
```

### Cron Format Explanation

```
# Format: 
# Minute Hour Day Month DayOfWeek Command
# 0      5    *   *     *        /path/to/script

# Fields:
# Minute        0-59
# Hour          0-23
# Day           1-31
# Month         1-12 or jan-dec
# DayOfWeek     0-6  or sun-sat (0=Sunday)
```

### Verification

To verify the setup:

1. Check if cron job is registered:
```bash
crontab -l
```

2. Ensure log directory exists and is writable:
```bash
ls -ld logs/
```

3. Test the script manually:
```bash
./scripts/cron-reboot.sh
```

### Notes

- Ensure Docker has appropriate permissions
- The script uses absolute paths for reliability
- Logs are rotated automatically (10MB per file, max 3 files)
- The script handles cleanup of existing containers

## Monitoring

To monitor the container status and logs:

```bash
# View container logs
docker logs router-reboot

# View container status
docker ps -a | grep router-reboot

# Follow log output
docker logs -f router-reboot
```

## Security Considerations

- Store sensitive credentials securely
- Use strong passwords
- Restrict network access appropriately
- Review logs regularly for unauthorized access attempts
- Ensure proper file permissions for configuration files
- Run container with minimal required privileges

## Troubleshooting

Common issues and solutions:

1. Connection failures:
   - Verify network connectivity
   - Check router IP address
   - Ensure correct credentials
   - Verify router web interface is accessible

2. Container issues:
   - Check Docker logs: `docker logs router-reboot`
   - Verify configuration file
   - Ensure proper permissions
   - Check container status: `docker ps -a | grep router-reboot`

3. Selenium/Chrome issues:
   - Check Chrome driver compatibility
   - Verify memory allocation (`--shm-size=2g`)
   - Review browser automation logs

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Buffalo router web interface
- Selenium WebDriver
- Docker technology

