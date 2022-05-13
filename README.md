# auto-salaries
A simple selenium bot to gather salaries from glassdoor .com varying country and titles with output to ods file

## Dependencies

- python3
- python3 selenium libs
- selenium (https://www.selenium.dev/downloads/)
- selenium gecko driver (https://github.com/mozilla/geckodriver/releases)
- firefox

## Howto

- Edit `config.py` to meet your requirements
- Run `main.py`

Note that you need to provide a user folder,
select the folder of the user already logged 
to glassdoor.

Sometimes a captcha popups. In these cases
just resolve the captcha and the script will continue.

After a bunch of log lines, an output ods file is created.
If the script ends early, the file is created with all the
lines collected so far.

## Additional notes

The main programming loop reload the main search page every time,
indeed the main search page differs from internal pages and implement
less antibot controls.

Also the active waits are added to avoid data loss.

## Improvements

This is a toy project I programmed in ~2 hours from scratch for personal use, feel free to suggest improvements.



