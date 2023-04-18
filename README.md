# Avisia Web Traffic

Simulate web traffic on the Avisia ecommerce training [website](https://avisia-tools.fr/site-formation-ecommerce/).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

The things you need before installing the software.

* You need Python installed on your computer
* The project uses Docker for the webdriver, so you need to install it and activate it if needed


chromedriver:

1. uninstall my chrome
2. use homebrew to install chromedriver: brew install chromedriver
3. se homebrew to install chrome: brew install google-chrome


### Installation

A step by step guide that will tell you how to get the development environment up and running.

```bash
# Clone the project
git clone ...
cd avisiawebtraffic

# Install dependencies
pip install -r requirements.txt

# Launch webdriver container
# Intel/Amd processor
docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" selenium/standalone-chrome

# ARM processor (Mac M1, Raspberry, ...)
docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" seleniarm/standalone-chromium
```

## Usage

A few examples of useful commands and/or tasks.

```
$ First example
$ Second example
$ And keep this in mind
```

## Deployment

## Support

## Additionnal Documentation
readme for docker selenium images :
  * [amd64](https://github.com/SeleniumHQ/docker-selenium)
  * [arm](https://github.com/seleniumhq-community/docker-seleniarm)

Official documentation : 
  * [Selenium doc](https://selenium-python.readthedocs.io/index.html)
  * [API doc](https://www.selenium.dev/selenium/docs/api/py/api.html)

Others ressources : 
  * [RealPython - Selenium](https://realpython.com/modern-web-automation-with-python-and-selenium/#motivation-tracking-listening-habits)
  * [Medium - Selenium and Airflow](https://towardsdatascience.com/selenium-on-airflow-automate-a-daily-online-task-60afc05afaae)
  * [Medium - Selenium on Cloud Composer](https://towardsdatascience.com/scraping-the-web-with-selenium-on-google-cloud-composer-airflow-7f74c211d1a1)
  * [Medium - Selenium on GKE](https://medium.com/selenium-grid-on-gcp/pytest-selenium-grid-gcp-using-kubernetes-cluster-a22a240b013)
  * [DEV - Selenium on Cloud Run](https://dev.to/googlecloud/using-headless-chrome-with-cloud-run-3fdp)

## Contributing

tag : 
  * utm_source
  * utm_medium
  * utm_campaign
  * [utm_term / utm_content]

Level in GA
  1. Category
  2. Action
  3. Label

## To Do
  * push gitlab


## Licence# traffic-generator
