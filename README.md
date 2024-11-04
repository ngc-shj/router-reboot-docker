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
├── .github/workflows/       # GitHub Actions configuration
│   └── docker-publish.yml  # CI/CD configuration
│
├── src/                    # Source code
│   └── reboot.py          # Main script
│
├── config/                 # Configuration files
│   └── config.example.yml # Example configuration
│
├── scripts/               # Execution scripts
│   ├── build.sh          # Build script
│   └── run.sh            # Run script
│
├── .gitignore            # Git exclusions
├── .dockerignore         # Docker build exclusions
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker image definition
├── requirements.txt      # Python dependencies
└── README.md             # This file
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
    login: "login.cgi"
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

## Monitoring

Check container logs:
```bash
docker logs router-reboot
```

View container status:
```bash
docker ps -a | grep router-reboot
```

## Security Considerations

- Store sensitive credentials securely
- Use strong passwords
- Restrict network access appropriately
- Review logs regularly for unauthorized access attempts

## Troubleshooting

Common issues and solutions:

1. Connection failures:
   - Verify network connectivity
   - Check router IP address
   - Ensure correct credentials

2. Container issues:
   - Check Docker logs
   - Verify configuration file
   - Ensure proper permissions

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the `LICENSE` file for details.

## Acknowledgments

- Buffalo router web interface documentation
- Selenium WebDriver
- Docker community

## Version History

- 1.0.0 (2024-11-04)
  - Initial release
  - Basic reboot functionality
  - Docker container support

