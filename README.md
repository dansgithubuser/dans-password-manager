# Dan's Password Manager
A free, open-source, easy-to-deploy, web-based password manager for teams.

Use at your own risk -- I can only offer my personal blessing that the crypto here is correct.

## Alternatives
- KeePass -- not web-based
- BitWarden -- not free for teams
- Padlock -- not web-based
- Passbolt -- account required to get installation instructions
- Clipperz -- "The open source version of Clipperz is suitable for testing and educational purposes only."

## Security Architecture
Most of the action can be seen in detail in `frontend/src/api.js`. "symmetric key" and "secret key" are used interchaneably.

### Table
| key | creation method | storage location | usage |
| --- | --------------- | ---------------- | ----- |
| user password | created by user | not stored | used to derive user symmetric key |
| user symmetric key | derived from user password | browser local storage | used to encrypt user private key |
| user public key | randomly generated | stored in database | used to encrypt team symmetric key |
| user private key | randomly generated | stored in database, encrypted by user symmetric key | used to decrypt team symmetric key |
| team symmetric key | randomly generated | stored in database, encrypted by each team member's user public key | used to encrypt team's passwords |

### Narrative
Let's start from the worst solution for a password manager and build up what we have.

The worst solution is to put the team's passwords in a database in the plain. Bad news if the database is compromised -- we want to not need to trust the server.

So, let's wrap the team's passwords under a team symmetric key. If we store the team symmetric key in the database, we've accomplished nothing, and if we don't, the team has to manually safely share it.

So, let's create a way for users to secretly send team symmetric keys to each other. We give each user a key pair. If we keep the user private key in the database, we've accomplished nothing, and if we don't, the user has to manually safely store it.

So, let's create a user symmetric key to wrap their user private key. This key shall be derivable from a password the user remembers, and doesn't need to leave the browser.

### Team Management
There are some details around adding and removing team members worth noting.

During an invitation, we want to make sure human error doesn't compromise a team's passwords, for example if the invitee gives an incorrect username or the inviter types it in wrong. So we create a verification code that the invitee must relay to the inviter for the invitation to complete.

During a revocation, if we leave the team symmetric key alone, then the revoked user still has the team symmetric key and can continue to get updates on the team's credentials as easily as if they were stored in the plain. So upon revocation, in the browser of the revoker, we generate a new team symmetric key, encrypt the team's passwords under that new team symmetric key, encrypt the new team symmetric key under each team member's public key, and send it all off to the server.

## To Do
- better mobile layout
- who's in a team?
