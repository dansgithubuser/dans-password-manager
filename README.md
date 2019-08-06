# UNDER CONSTRUCTION - don't use for sensitive information yet!

# Dan's Password Manager
A free, open-source, easy-to-deploy, web-based password manager for teams.

## Deploy
### Heroku
- `git clone --recursive`
- `cd dans-password-manager`
- ensure you're logged into Heroku CLI
- `python go.py -d`

## Alternatives
- KeePass -- not web-based
- BitWarden -- not free for teams
- Padlock -- not web-based
- Passbolt -- account required to get installation instructions
- Clipperz -- "The open source version of Clipperz is suitable for testing and educational purposes only."

## todo
- implement frontend crypto - https://wwwtyro.github.io/cryptico/
	- signup
	- log in
	- create team
	- add/update item
	- view item
	- invite
	- rotate
- vuetify frontend
	- signup
	- log in
	- teams
	- items
	- verify + invite
	- revoke + rotate
- digest notes into arch docs
	- for sharing accounts to avoid having to make a team on that service
	- a convenience, not a security measure

## Notes
```
user
	private_key
	team_secret
server
	user
		public_key
		encrypt(private_key, password)
		encrypt(team_secret, public_key)
	item
		encrypt(item, team_secret)

when user signs up:
	user creates key pair and team_secret
	user encrypts private_key and team_secret with password
	user sends public_key, encrypted private_key, and encrypted team_secret to server

when user logs in:
	user receives encrypted private_key and public_key
	user decrypts private_key with password

when user creates a team:
	user encrypts team_secret with public_key
	user sends to server

when a user adds an item to a team:
	user encrypts item with team_secret
	user sends to server

when a user wants to view an item:
	user requests encrypted item
	user decrypts with team_secret

when a user invites a user to a team:
	inviter gets invitee's public_key from server
	inviter encrypts team_secret with invitee's public_key
	inviter sends to server

when team_secret must be rotated to protect against a former user:
	user decrypts all items with old team_secret
	user creates new team_secret
	user encrypts all items with new team_secret
	user encrypts new team_secret with public_key of each other current user of team
	user sends to server

when user has an outdated team_secret:
	user receives new encrypted team_secret
	user decrypts with public_key to obtain new team_secret
```
