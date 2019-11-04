# Dan's Password Manager
A free, open-source, easy-to-deploy, web-based password manager for teams.

Use at your own risk -- I can only offer my personal blessing that the crypto here is correct.

## Deploy
### Heroku
- `git clone --recursive`
- `cd dans-password-manager`
- `heroku login`
- `python go.py --first-deploy`

## Alternatives
- KeePass -- not web-based
- BitWarden -- not free for teams
- Padlock -- not web-based
- Passbolt -- account required to get installation instructions
- Clipperz -- "The open source version of Clipperz is suitable for testing and educational purposes only."

## todo
- limit search to certain teams
- better mobile layout
- security review
- automate first deploy
	- heroku buildpacks:add --index 1 heroku/nodejs
	- heroku config:set NPM_CONFIG_PRODUCTION=false
- who's in a team?
