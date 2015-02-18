DeCAPTCHA
===

A Scrapy middleware that solves CAPTCHAs found on web pages

The middleware uses 2 kind of sub-components:

- **Engines**: responsible for finding captcha on page and submitting it
- **Solvers**: convert CAPTCHA image file to text

Usage
---

To use decaptcha in your Scrapy project, you must set some variables in your `settings.py` file:

	# enable/disable middleware
	DECAPTCHA_ENABLED = 1

	# set engines classes
    DECAPTCHA_ENGINES = {
        'decaptcha.engines.recaptcha.RecaptchaEngine': 500,
    }
    
    # set solver class
    DECAPTCHA_SOLVER = 'decaptcha.solvers.deathbycaptcha.DeathbycaptchaSolver'
    
    # configure deathbycaptcha solver
    DECAPTCHA_DEATHBYCAPTCHA_USERNAME = 'your-username'
    DECAPTCHA_DEATHBYCAPTCHA_PASSWORD = 'your-password'
    
    
Supported engines
---

- `decaptcha.engines.recaptcha.RecaptchaEngine` - Google reCAPTCHA engine

Supported solvers
---

- `decaptcha.solvers.deathbycaptcha.DeathbycaptchaSolver` - Solver that uses [http://www.deathbycaptcha.com/](http://www.deathbycaptcha.com/) service

    

